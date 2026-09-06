"""In-process registry of live StreamingSynthesisSession objects.

AGENTS.md rule #7: all mutable streaming session state must live here,
not scattered across router-level globals. One session per
`session_id` (the client mints this UUID before opening the socket).

The very first session created process-wide is flagged to trigger the
one deterministic buffer-underflow test event described in
docs/websocket-protocol.md; every session after that streams cleanly.
"""

from __future__ import annotations

from tts_runtime.interfaces import AcousticModelAdapter, StreamingVocoderAdapter
from tts_runtime.session import StreamingSynthesisSession

_sessions: dict[str, StreamingSynthesisSession] = {}
_connected: set[str] = set()
_underflow_assigned = False


def get_or_create_session(
    session_id: str,
    *,
    acoustic_model: AcousticModelAdapter,
    vocoder: StreamingVocoderAdapter,
) -> StreamingSynthesisSession:
    global _underflow_assigned
    session = _sessions.get(session_id)
    if session is None:
        trigger_underflow = not _underflow_assigned
        _underflow_assigned = True
        session = StreamingSynthesisSession(
            session_id,
            acoustic_model=acoustic_model,
            vocoder=vocoder,
            real_time=True,
            trigger_underflow_once=trigger_underflow,
        )
        _sessions[session_id] = session
    return session


def mark_connected(session_id: str) -> None:
    _connected.add(session_id)


def mark_disconnected(session_id: str) -> None:
    _connected.discard(session_id)


def remove_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
    _connected.discard(session_id)


def count_active_sessions() -> int:
    return len(_connected)


def reset_all_for_tests() -> None:
    global _underflow_assigned
    _sessions.clear()
    _connected.clear()
    _underflow_assigned = False
