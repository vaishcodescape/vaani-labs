"""WS /api/v1/synthesis/stream/{session_id} — see docs/websocket-protocol.md.

Orchestration only: parses/validates client events, drives the pure
`StreamingSynthesisSession` async generator, and maps its output events
onto actual `send_json`/`send_bytes` calls. No NLP/TTS business logic
lives here (AGENTS.md rule #3) — that's all in `tts_runtime` and
`indic_text`, reached via the injected `ProviderRegistry`.

Task lifecycle (not a `tts_runtime` concern — see docs/architecture.md):
one asyncio.Task drives the "producer" (the currently running
revision's event generator) at a time. `edit`/`reset`/a fresh `start`
hard-cancel that task and replace it; `cancel`/`pause`/`resume` instead
set flags on the session and let the producer task wind down or
continue on its own, so it can still emit a graceful `cancelled` event.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from tts_runtime.interfaces import SynthesisControls
from tts_runtime.session import BinaryChunkEvent, JsonEvent

from app.deps import ProviderRegistry, get_registry
from app.schemas.ws import (
    CancelEvent,
    EditEvent,
    PauseEvent,
    PingEvent,
    ResetEvent,
    ResumeEvent,
    StartEvent,
    parse_client_event,
)
from app.services.analysis_service import analyse, to_response
from app.services.session_registry import get_or_create_session, mark_connected, mark_disconnected

router = APIRouter(tags=["synthesis"])
logger = logging.getLogger(__name__)


async def _send_error(websocket: WebSocket, code: str, message: str) -> None:
    await websocket.send_json({"type": "error", "code": code, "message": message})


async def _drive_and_send(
    websocket: WebSocket, event_stream: AsyncIterator[JsonEvent | BinaryChunkEvent]
) -> None:
    async for event in event_stream:
        if isinstance(event, BinaryChunkEvent):
            await websocket.send_bytes(event.frame)
        else:
            await websocket.send_json({"type": event.type, **event.payload})


async def _cancel_task(task: asyncio.Task[None] | None) -> None:
    if task is None or task.done():
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


@router.websocket("/api/v1/synthesis/stream/{session_id}")
async def synthesis_stream(
    websocket: WebSocket,
    session_id: str,
    registry: ProviderRegistry = Depends(get_registry),
) -> None:
    await websocket.accept()
    mark_connected(session_id)
    session = get_or_create_session(
        session_id, acoustic_model=registry.acoustic_model, vocoder=registry.vocoder
    )
    await websocket.send_json(
        {"type": "session_started", "session_id": session_id, "revision_id": session.revision_id}
    )

    current_task: asyncio.Task[None] | None = None
    last_controls: SynthesisControls | None = None

    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                raw = json.loads(raw_text)
                event = parse_client_event(raw)
            except (json.JSONDecodeError, ValidationError, ValueError) as exc:
                await _send_error(websocket, "VALIDATION_ERROR", str(exc))
                continue

            if isinstance(event, StartEvent):
                await _cancel_task(current_task)
                result = analyse(event.text, registry)
                last_controls = SynthesisControls(
                    voice_id=event.voice_id,
                    speed=event.speed,
                    pitch=event.pitch,
                    energy=event.energy,
                    chunk_size_ms=event.chunk_size_ms,
                    mrss_slow_update_rate=event.mrss_slow_update_rate,
                )
                await websocket.send_json(
                    {
                        "type": "text_analysis",
                        "session_id": session_id,
                        "revision_id": session.revision_id + 1,
                        **to_response(result).model_dump(),
                    }
                )
                current_task = asyncio.create_task(
                    _drive_and_send(websocket, session.start(result.tokens, last_controls))
                )

            elif isinstance(event, EditEvent):
                if session.revision_id == 0:
                    await _send_error(websocket, "SESSION_NOT_STARTED", "call start before edit")
                    continue
                if event.revision_id != session.revision_id + 1:
                    await _send_error(
                        websocket,
                        "INVALID_REVISION_TRANSITION",
                        f"expected revision_id {session.revision_id + 1}, got {event.revision_id}",
                    )
                    continue
                await _cancel_task(current_task)
                result = analyse(event.unsynthesized_text, registry)
                controls = last_controls or SynthesisControls(voice_id="hi-female-1")
                await websocket.send_json(
                    {
                        "type": "text_analysis",
                        "session_id": session_id,
                        "revision_id": session.revision_id + 1,
                        **to_response(result).model_dump(),
                    }
                )
                current_task = asyncio.create_task(
                    _drive_and_send(websocket, session.edit(result.tokens, controls))
                )

            elif isinstance(event, CancelEvent):
                session.cancel()

            elif isinstance(event, PauseEvent):
                session.pause()

            elif isinstance(event, ResumeEvent):
                session.resume()

            elif isinstance(event, ResetEvent):
                await _cancel_task(current_task)
                current_task = None
                session.reset()

            elif isinstance(event, PingEvent):
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        pass
    finally:
        mark_disconnected(session_id)
        await _cancel_task(current_task)
