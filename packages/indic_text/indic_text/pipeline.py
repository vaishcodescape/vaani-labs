"""Orchestrates tokenizer + provider interfaces into full text analysis.

This is business logic, not API logic: it depends only on the provider
Protocols defined in this package, takes provider instances as plain
function arguments (constructor injection happens one level up, in
apps/api/app/deps.py), and has no FastAPI/Pydantic dependency. That
makes it directly unit-testable and reusable from both the REST
`/text/analyse` handler and the WebSocket `start`/`edit` handlers.
"""

from __future__ import annotations

from dataclasses import dataclass

from indic_text.constants import PRONUNCIATION_UNCERTAINTY_THRESHOLD
from indic_text.interfaces import (
    CodeSwitchDetector,
    GraphemeToPhoneme,
    LanguageIdentifier,
    PronunciationLexicon,
    PronunciationRanker,
    ScriptDetector,
    TextNormalizer,
)
from indic_text.models import (
    AnalysedToken,
    CodeSwitchSpan,
    PronunciationSource,
    TokenPronunciation,
    TokenType,
)
from indic_text.tokenizer import tokenize


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    text: str
    tokens: list[AnalysedToken]
    code_switch_spans: list[CodeSwitchSpan]


def _span_lookup(spans: list, offset: int, attr: str, default: str) -> str:
    for span in spans:
        if span.start_offset <= offset < span.end_offset:
            return getattr(span, attr)
    return default


def analyse_text(
    text: str,
    *,
    script_detector: ScriptDetector,
    language_identifier: LanguageIdentifier,
    normalizer: TextNormalizer,
    g2p: GraphemeToPhoneme,
    ranker: PronunciationRanker,
    lexicon: PronunciationLexicon,
    code_switch_detector: CodeSwitchDetector,
) -> AnalysisResult:
    raw_tokens = tokenize(text)
    script_spans = script_detector.detect(text)
    language_spans = language_identifier.identify(text, script_spans)

    analysed: list[AnalysedToken] = []
    for raw in raw_tokens:
        script = _span_lookup(script_spans, raw.start_offset, "script", "Common")
        language = _span_lookup(language_spans, raw.start_offset, "language", "und")
        normalized = normalizer.normalize(raw.surface, raw.token_type)
        codepoints = tuple(f"U+{ord(ch):04X}" for ch in raw.surface)

        if raw.token_type is TokenType.WORD:
            lexicon_entry = lexicon.get(raw.surface, language)
            if lexicon_entry is not None:
                pronunciation = TokenPronunciation(
                    phonemes=lexicon_entry.phonemes,
                    confidence=1.0,
                    is_uncertain=False,
                    source=PronunciationSource.LEXICON,
                )
            else:
                candidates = ranker.rank(g2p.to_phonemes(raw.surface, language, script))
                top = candidates[0]
                pronunciation = TokenPronunciation(
                    phonemes=top.phonemes,
                    confidence=top.confidence,
                    is_uncertain=top.confidence < PRONUNCIATION_UNCERTAINTY_THRESHOLD,
                    source=top.source,
                )
        else:
            pronunciation = TokenPronunciation(
                phonemes="", confidence=1.0, is_uncertain=False, source=PronunciationSource.G2P
            )

        analysed.append(
            AnalysedToken(
                index=raw.index,
                surface=raw.surface,
                start_offset=raw.start_offset,
                end_offset=raw.end_offset,
                script=script,
                language=language,
                normalized=normalized,
                token_type=raw.token_type,
                codepoints=codepoints,
                pronunciation=pronunciation,
            )
        )

    code_switch_spans = code_switch_detector.detect(analysed)
    return AnalysisResult(text=text, tokens=analysed, code_switch_spans=code_switch_spans)
