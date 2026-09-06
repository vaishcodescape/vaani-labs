"""Acoustic model and streaming vocoder provider interfaces.

See docs/model-adapter.md for what a real implementation must preserve.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol

from indic_text.models import AnalysedToken


@dataclass(frozen=True, slots=True)
class SynthesisControls:
    voice_id: str
    speed: float = 1.0
    pitch: float = 0.0
    energy: float = 1.0
    chunk_size_ms: int = 200
    mrss_slow_update_rate: int = 4
    """Recompute MRSS's slow-path conditioning every N chunks instead of every chunk."""


@dataclass(frozen=True, slots=True)
class SynthesisPlan:
    tokens: tuple[AnalysedToken, ...]
    controls: SynthesisControls
    estimated_duration_ms: float
    sample_rate: int
    planning_ms: float
    """Simulated acoustic-model planning latency, applied once before streaming starts."""
    token_durations_ms: tuple[float, ...]
    """Estimated spoken duration of each entry in `tokens`, same order/length."""


@dataclass(frozen=True, slots=True)
class AudioChunk:
    sequence: int
    pcm: bytes
    duration_ms: float
    acoustic_ms: float
    vocoder_ms: float
    is_last: bool


class AcousticModelAdapter(Protocol):
    def plan(
        self, tokens: list[AnalysedToken], controls: SynthesisControls
    ) -> SynthesisPlan:
        """Produce a duration-estimated synthesis plan. Must not block/sleep."""
        ...


class StreamingVocoderAdapter(Protocol):
    def stream(self, plan: SynthesisPlan) -> Iterator[AudioChunk]:
        """Yield audio chunks in order. Must not block/sleep — timing is simulated
        via the returned `acoustic_ms`/`vocoder_ms` fields, applied by the caller."""
        ...
