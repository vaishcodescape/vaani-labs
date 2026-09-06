"""Client -> server WebSocket event validation.

Every inbound WS text frame is parsed as JSON and validated through one
of these models before it is acted on (constraint #14). See
docs/websocket-protocol.md for the full event table.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter


class StartEvent(BaseModel):
    type: Literal["start"]
    text: str
    voice_id: str
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=0.0, ge=-12.0, le=12.0)
    energy: float = Field(default=1.0, ge=0.25, le=2.0)
    streaming: bool = True
    chunk_size_ms: int = Field(default=200, ge=20, le=5000)
    mrss_slow_update_rate: int = Field(default=4, ge=1, le=50)


class EditEvent(BaseModel):
    type: Literal["edit"]
    revision_id: int
    unsynthesized_text: str
    edit_offset_ms: float = 0.0


class CancelEvent(BaseModel):
    type: Literal["cancel"]


class PauseEvent(BaseModel):
    type: Literal["pause"]


class ResumeEvent(BaseModel):
    type: Literal["resume"]


class ResetEvent(BaseModel):
    type: Literal["reset"]


class PingEvent(BaseModel):
    type: Literal["ping"]


ClientEvent = (
    StartEvent | EditEvent | CancelEvent | PauseEvent | ResumeEvent | ResetEvent | PingEvent
)

_DiscriminatedClientEvent = Annotated[ClientEvent, Field(discriminator="type")]
_CLIENT_EVENT_ADAPTER: TypeAdapter[ClientEvent] = TypeAdapter(_DiscriminatedClientEvent)


def parse_client_event(raw: dict[str, object]) -> ClientEvent:
    return _CLIENT_EVENT_ADAPTER.validate_python(raw)
