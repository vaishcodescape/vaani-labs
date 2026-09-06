"""Deterministic duration-estimating acoustic model mock.

Estimates spoken duration from phoneme counts and token type rather
than running any real acoustic model. Confidence/quality of the
estimate is irrelevant for Phase 1 — determinism and plausibility are
what matter (see docs/product-requirements.md's non-goals).
"""

from __future__ import annotations

from indic_text.models import AnalysedToken, TokenType

from tts_runtime.interfaces import SynthesisControls, SynthesisPlan

_MS_PER_PHONEME = 90.0
_PUNCTUATION_PAUSE_MS = 150.0
_WHITESPACE_PAUSE_MS = 60.0
_PLANNING_BASE_MS = 15.0
_PLANNING_MS_PER_TOKEN = 0.8


def _token_duration_ms(token: AnalysedToken, speed: float) -> float:
    if token.token_type is TokenType.PUNCTUATION:
        base = _PUNCTUATION_PAUSE_MS
    elif token.token_type is TokenType.WHITESPACE:
        base = _WHITESPACE_PAUSE_MS
    else:
        phoneme_count = len(token.pronunciation.phonemes.split()) if token.pronunciation.phonemes else 1
        base = max(phoneme_count, 1) * _MS_PER_PHONEME
    return base / max(speed, 0.01)


class MockAcousticModelAdapter:
    provider_id = "mock-duration-acoustic"

    def plan(self, tokens: list[AnalysedToken], controls: SynthesisControls) -> SynthesisPlan:
        durations = tuple(_token_duration_ms(t, controls.speed) for t in tokens)
        planning_ms = _PLANNING_BASE_MS + _PLANNING_MS_PER_TOKEN * len(tokens)
        return SynthesisPlan(
            tokens=tuple(tokens),
            controls=controls,
            estimated_duration_ms=sum(durations),
            sample_rate=22050,
            planning_ms=planning_ms,
            token_durations_ms=durations,
        )
