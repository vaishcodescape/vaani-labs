"""Provider interfaces (typing.Protocol) for all Indic text processing steps.

Every interface here must have at least one deterministic mock
implementation under `indic_text.mock`. Real implementations live in
sibling modules/packages and are wired in `apps/api/app/deps.py` — see
`docs/model-adapter.md`.
"""

from __future__ import annotations

from typing import Protocol

from indic_text.models import (
    AnalysedToken,
    CodeSwitchSpan,
    LanguageSpan,
    LexiconEntry,
    PronunciationCandidate,
    ScriptSpan,
    TokenType,
)


class ScriptDetector(Protocol):
    def detect(self, text: str) -> list[ScriptSpan]:
        """Split text into contiguous same-script spans."""
        ...


class LanguageIdentifier(Protocol):
    def identify(self, text: str, script_spans: list[ScriptSpan]) -> list[LanguageSpan]:
        """Assign a language code to each script span."""
        ...


class TextNormalizer(Protocol):
    def normalize(self, surface: str, token_type: TokenType) -> str:
        """Produce the spoken/normalized form of a single token."""
        ...


class CodeSwitchDetector(Protocol):
    def detect(self, tokens: list[AnalysedToken]) -> list[CodeSwitchSpan]:
        """Identify contiguous runs of tokens in a non-matrix language."""
        ...


class Transliterator(Protocol):
    def transliterate(self, text: str, source_script: str, target_script: str) -> str:
        """Best-effort character-level transliteration between two scripts."""
        ...


class GraphemeToPhoneme(Protocol):
    def to_phonemes(self, surface: str, language: str, script: str) -> list[PronunciationCandidate]:
        """Return one or more candidate pronunciations, unordered, with confidence in [0, 1]."""
        ...


class PronunciationRanker(Protocol):
    def rank(self, candidates: list[PronunciationCandidate]) -> list[PronunciationCandidate]:
        """Return candidates sorted descending by confidence."""
        ...


class PronunciationLexicon(Protocol):
    def get(self, surface: str, language: str) -> LexiconEntry | None: ...

    def list(
        self, query: str | None = None, language: str | None = None
    ) -> list[LexiconEntry]: ...

    def create(self, surface: str, language: str, phonemes: str, notes: str) -> LexiconEntry: ...

    def update(
        self, entry_id: str, phonemes: str | None, notes: str | None
    ) -> LexiconEntry | None: ...

    def delete(self, entry_id: str) -> bool: ...
