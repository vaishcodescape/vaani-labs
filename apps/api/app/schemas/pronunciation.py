from __future__ import annotations

from pydantic import BaseModel


class PronunciationCandidateSchema(BaseModel):
    phonemes: str
    confidence: float
    source: str


class PronunciationCandidatesRequest(BaseModel):
    surface: str
    language: str
    script: str


class PronunciationCandidatesResponse(BaseModel):
    surface: str
    candidates: list[PronunciationCandidateSchema]


class PronunciationPreviewRequest(BaseModel):
    surface: str
    phonemes: str
    voice_id: str


class PronunciationPreviewResponse(BaseModel):
    sample_rate: int
    channels: int
    bit_depth: int
    pcm_base64: str
