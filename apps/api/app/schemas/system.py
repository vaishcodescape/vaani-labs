from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


class SystemResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: float
    providers: dict[str, str]
    active_sessions: int
    lexicon_entry_count: int


class ModelInfo(BaseModel):
    id: str
    kind: str
    is_default: bool


class ModelsResponse(BaseModel):
    acoustic_models: list[ModelInfo]
    vocoders: list[ModelInfo]


class VoiceInfo(BaseModel):
    id: str
    language: str
    label: str
    gender: str


class VoicesResponse(BaseModel):
    voices: list[VoiceInfo]


class LanguageInfo(BaseModel):
    code: str
    name: str
    script: str


class LanguagesResponse(BaseModel):
    languages: list[LanguageInfo]
