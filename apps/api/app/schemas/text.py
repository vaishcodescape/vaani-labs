from __future__ import annotations

from pydantic import BaseModel


class TokenPronunciationSchema(BaseModel):
    phonemes: str
    confidence: float
    is_uncertain: bool
    source: str


class AnalysedTokenSchema(BaseModel):
    index: int
    surface: str
    start_offset: int
    end_offset: int
    script: str
    language: str
    normalized: str
    token_type: str
    codepoints: list[str]
    pronunciation: TokenPronunciationSchema


class CodeSwitchSpanSchema(BaseModel):
    start_offset: int
    end_offset: int
    language: str


class AnalyseTextRequest(BaseModel):
    text: str


class AnalyseTextResponse(BaseModel):
    text: str
    tokens: list[AnalysedTokenSchema]
    code_switch_spans: list[CodeSwitchSpanSchema]


class NormalizeTextRequest(BaseModel):
    text: str


class NormalizeTextResponse(BaseModel):
    text: str
    normalized: str
    token_type: str
