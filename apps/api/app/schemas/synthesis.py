from __future__ import annotations

from pydantic import BaseModel, Field


class OfflineSynthesisRequest(BaseModel):
    text: str
    voice_id: str
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=0.0, ge=-12.0, le=12.0)
    energy: float = Field(default=1.0, ge=0.25, le=2.0)


class OfflineSynthesisResponse(BaseModel):
    sample_rate: int
    channels: int
    bit_depth: int
    duration_ms: float
    rtf: float
    pcm_base64: str
