"""Wraps indic_text's pure `analyse_text` pipeline with the API's provider registry
and maps its dataclass output onto the wire-format Pydantic schemas."""

from __future__ import annotations

from indic_text.models import AnalysedToken
from indic_text.pipeline import AnalysisResult, analyse_text

from app.deps import ProviderRegistry
from app.schemas.text import (
    AnalysedTokenSchema,
    AnalyseTextResponse,
    CodeSwitchSpanSchema,
    TokenPronunciationSchema,
)


def analyse(text: str, registry: ProviderRegistry) -> AnalysisResult:
    return analyse_text(
        text,
        script_detector=registry.script_detector,
        language_identifier=registry.language_identifier,
        normalizer=registry.normalizer,
        g2p=registry.g2p,
        ranker=registry.ranker,
        lexicon=registry.lexicon,
        code_switch_detector=registry.code_switch_detector,
    )


def to_response(result: AnalysisResult) -> AnalyseTextResponse:
    return AnalyseTextResponse(
        text=result.text,
        tokens=[_token_schema(t) for t in result.tokens],
        code_switch_spans=[
            CodeSwitchSpanSchema(
                start_offset=s.start_offset, end_offset=s.end_offset, language=s.language
            )
            for s in result.code_switch_spans
        ],
    )


def _token_schema(token: AnalysedToken) -> AnalysedTokenSchema:
    return AnalysedTokenSchema(
        index=token.index,
        surface=token.surface,
        start_offset=token.start_offset,
        end_offset=token.end_offset,
        script=token.script,
        language=token.language,
        normalized=token.normalized,
        token_type=token.token_type.value,
        codepoints=list(token.codepoints),
        pronunciation=TokenPronunciationSchema(
            phonemes=token.pronunciation.phonemes,
            confidence=token.pronunciation.confidence,
            is_uncertain=token.pronunciation.is_uncertain,
            source=token.pronunciation.source.value,
        ),
    )
