"""Framework-agnostic data types shared by every provider interface.

These are plain dataclasses (not Pydantic) so that this package has zero
dependency on FastAPI/Pydantic and can be unit tested in isolation. The
API layer (apps/api) maps these onto its Pydantic response models.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenType(str, Enum):
    WORD = "word"
    NUMBER = "number"
    DATE = "date"
    ABBREVIATION = "abbreviation"
    PUNCTUATION = "punctuation"
    WHITESPACE = "whitespace"


class PronunciationSource(str, Enum):
    LEXICON = "lexicon"
    G2P = "g2p"
    G2P_ALT = "g2p-alt"


@dataclass(frozen=True, slots=True)
class RawToken:
    index: int
    surface: str
    start_offset: int
    end_offset: int
    token_type: TokenType


@dataclass(frozen=True, slots=True)
class ScriptSpan:
    start_offset: int
    end_offset: int
    script: str


@dataclass(frozen=True, slots=True)
class LanguageSpan:
    start_offset: int
    end_offset: int
    language: str


@dataclass(frozen=True, slots=True)
class CodeSwitchSpan:
    start_offset: int
    end_offset: int
    language: str


@dataclass(frozen=True, slots=True)
class PronunciationCandidate:
    phonemes: str
    confidence: float
    source: PronunciationSource


@dataclass(frozen=True, slots=True)
class TokenPronunciation:
    phonemes: str
    confidence: float
    is_uncertain: bool
    source: PronunciationSource


@dataclass(frozen=True, slots=True)
class AnalysedToken:
    index: int
    surface: str
    start_offset: int
    end_offset: int
    script: str
    language: str
    normalized: str
    token_type: TokenType
    codepoints: tuple[str, ...]
    pronunciation: TokenPronunciation


@dataclass(frozen=True, slots=True)
class LexiconEntry:
    id: str
    surface: str
    language: str
    phonemes: str
    notes: str
    created_at: str
    updated_at: str
