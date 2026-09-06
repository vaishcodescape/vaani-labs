from __future__ import annotations

from pydantic import BaseModel, Field


class LexiconEntrySchema(BaseModel):
    id: str
    surface: str
    language: str
    phonemes: str
    notes: str
    created_at: str
    updated_at: str


class LexiconListResponse(BaseModel):
    entries: list[LexiconEntrySchema]


class LexiconCreateRequest(BaseModel):
    surface: str = Field(min_length=1)
    language: str = Field(min_length=1)
    phonemes: str = Field(min_length=1)
    notes: str = ""


class LexiconUpdateRequest(BaseModel):
    phonemes: str | None = None
    notes: str | None = None
