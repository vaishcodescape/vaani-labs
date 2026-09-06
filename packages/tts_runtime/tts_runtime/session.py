"""Stateful streaming synthesis session engine.

Owns exactly the state described in docs/websocket-protocol.md's state
machine: idle/running/paused/cancelled/completed, plus the monotonic
revision counter. Produces an async stream of transport-agnostic events
(`JsonEvent` / `BinaryChunkEvent`); the WebSocket router in apps/api
maps these onto actual `send_json`/`send_bytes` calls. This module has
no FastAPI/websockets import, by design (AGENTS.md rule #7).

Timing is simulated: the mock acoustic model and vocoder report
`planning_ms`/`acoustic_ms`/`vocoder_ms` as plain data without actually
sleeping (so they stay instant and deterministic for unit tests). This
session is the *one* place that turns those numbers into real
`asyncio.sleep` calls, gated by `real_time`, so tests can disable
wall-clock delay while exercising the exact same control flow used in
production.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass
from enum import Enum

from audio_metrics.metrics import AudioMetricCalculator
from audio_metrics.pcm import pack_chunk_frame
from indic_text.models import AnalysedToken

from tts_runtime.interfaces import AcousticModelAdapter, StreamingVocoderAdapter, SynthesisControls

UNDERFLOW_TEST_CHUNK_INDEX = 3
"""Deterministic Phase-1 test hook — see docs/websocket-protocol.md."""


class SessionState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass(frozen=True, slots=True)
class JsonEvent:
    type: str
    payload: dict[str, object]


@dataclass(frozen=True, slots=True)
class BinaryChunkEvent:
    frame: bytes


SessionEvent = JsonEvent | BinaryChunkEvent


class StreamingSynthesisSession:
    def __init__(
        self,
        session_id: str,
        *,
        acoustic_model: AcousticModelAdapter,
        vocoder: StreamingVocoderAdapter,
        real_time: bool = True,
        trigger_underflow_once: bool = False,
    ) -> None:
        self.session_id = session_id
        self._acoustic_model = acoustic_model
        self._vocoder = vocoder
        self._real_time = real_time
        self._trigger_underflow_once = trigger_underflow_once
        self._underflow_triggered = False

        self.state = SessionState.IDLE
        self.revision_id = 0
        self.metrics = AudioMetricCalculator()

        self._cancel_requested = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()

    def cancel(self) -> None:
        self._cancel_requested = True
        self._pause_event.set()

    def pause(self) -> None:
        if self.state is SessionState.RUNNING:
            self.state = SessionState.PAUSED
            self._pause_event.clear()

    def resume(self) -> None:
        if self.state is SessionState.PAUSED:
            self.state = SessionState.RUNNING
            self._pause_event.set()

    def reset(self) -> None:
        self.state = SessionState.IDLE
        self.revision_id = 0
        self._cancel_requested = False
        self._underflow_triggered = False
        self._pause_event.set()

    async def start(
        self, tokens: list[AnalysedToken], controls: SynthesisControls
    ) -> AsyncIterator[SessionEvent]:
        self.revision_id = 1
        async for event in self._run_revision(tokens, controls):
            yield event

    async def edit(
        self, tokens: list[AnalysedToken], controls: SynthesisControls
    ) -> AsyncIterator[SessionEvent]:
        self.revision_id += 1
        async for event in self._run_revision(tokens, controls):
            yield event

    async def _run_revision(
        self, tokens: list[AnalysedToken], controls: SynthesisControls
    ) -> AsyncIterator[SessionEvent]:
        revision_id = self.revision_id
        self._cancel_requested = False
        self.state = SessionState.RUNNING

        plan = self._acoustic_model.plan(tokens, controls)
        if self._real_time:
            await asyncio.sleep(plan.planning_ms / 1000)

        yield JsonEvent(
            "synthesis_started",
            {
                "session_id": self.session_id,
                "revision_id": revision_id,
                "sample_rate": plan.sample_rate,
                "channels": 1,
                "bit_depth": 16,
                "estimated_duration_ms": plan.estimated_duration_ms,
                "token_durations_ms": list(plan.token_durations_ms),
            },
        )
        yield JsonEvent(
            "audio_metadata",
            {
                "session_id": self.session_id,
                "revision_id": revision_id,
                "sample_rate": plan.sample_rate,
                "channels": 1,
                "bit_depth": 16,
                "chunk_size_ms": controls.chunk_size_ms,
            },
        )

        self.metrics.start(start_time_ms=time.monotonic() * 1000)
        buffered_ms = 0.0

        for chunk in self._vocoder.stream(plan):
            await self._pause_event.wait()
            if self._cancel_requested:
                self.state = SessionState.CANCELLED
                yield JsonEvent(
                    "cancelled", {"session_id": self.session_id, "revision_id": revision_id}
                )
                return

            if self._real_time:
                await asyncio.sleep((chunk.acoustic_ms + chunk.vocoder_ms) / 1000)

            produced_at_ms = time.monotonic() * 1000
            self.metrics.record_chunk(
                sequence=chunk.sequence,
                acoustic_ms=chunk.acoustic_ms,
                vocoder_ms=chunk.vocoder_ms,
                produced_at_ms=produced_at_ms,
                chunk_duration_ms=chunk.duration_ms,
            )
            is_first_audio = chunk.sequence == 0
            yield JsonEvent(
                "chunk_metric",
                {
                    "session_id": self.session_id,
                    "revision_id": revision_id,
                    "sequence": chunk.sequence,
                    "acoustic_ms": chunk.acoustic_ms,
                    "vocoder_ms": chunk.vocoder_ms,
                    "chunk_latency_ms": chunk.acoustic_ms + chunk.vocoder_ms,
                    "is_first_audio": is_first_audio,
                },
            )

            yield BinaryChunkEvent(
                frame=pack_chunk_frame(revision_id=revision_id, sequence=chunk.sequence, pcm=chunk.pcm)
            )

            buffered_ms += chunk.duration_ms
            underflow = False
            if (
                self._trigger_underflow_once
                and not self._underflow_triggered
                and chunk.sequence == UNDERFLOW_TEST_CHUNK_INDEX
            ):
                underflow = True
                self._underflow_triggered = True
                buffered_ms = 0.0
                yield JsonEvent(
                    "warning",
                    {
                        "code": "SIMULATED_BUFFER_UNDERFLOW",
                        "message": "Simulated buffer underflow for demo/test purposes.",
                    },
                )
            yield JsonEvent(
                "buffer_status",
                {
                    "session_id": self.session_id,
                    "revision_id": revision_id,
                    "buffered_ms": buffered_ms,
                    "underflow": underflow,
                },
            )

        self.state = SessionState.COMPLETED
        summary = self.metrics.summary()
        yield JsonEvent(
            "completed",
            {
                "session_id": self.session_id,
                "revision_id": revision_id,
                "total_chunks": summary.total_chunks,
                "total_duration_ms": summary.total_duration_ms,
                "rtf": summary.rtf,
                "first_audio_latency_ms": summary.first_audio_latency_ms,
                "p50_chunk_latency_ms": summary.p50_chunk_latency_ms,
                "p95_chunk_latency_ms": summary.p95_chunk_latency_ms,
                "p99_chunk_latency_ms": summary.p99_chunk_latency_ms,
            },
        )
