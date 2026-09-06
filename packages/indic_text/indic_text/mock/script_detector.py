"""Deterministic Unicode-block-based script detector.

No ML model is needed for script detection even in a "real" system —
Unicode block membership is authoritative — so this mock is expected to
survive into later phases largely unchanged (see docs/model-adapter.md).
"""

from __future__ import annotations

from indic_text.models import ScriptSpan

_DEVANAGARI_RANGE = (0x0900, 0x097F)
_GUJARATI_RANGE = (0x0A80, 0x0AFF)
_LATIN_RANGES = ((0x0041, 0x005A), (0x0061, 0x007A), (0x00C0, 0x024F))


def _script_of(ch: str) -> str:
    cp = ord(ch)
    if _DEVANAGARI_RANGE[0] <= cp <= _DEVANAGARI_RANGE[1]:
        return "Devanagari"
    if _GUJARATI_RANGE[0] <= cp <= _GUJARATI_RANGE[1]:
        return "Gujarati"
    for lo, hi in _LATIN_RANGES:
        if lo <= cp <= hi:
            return "Latin"
    return "Common"


class MockScriptDetector:
    """Merges consecutive same-script characters into spans."""

    provider_id = "mock-unicode-range"

    def detect(self, text: str) -> list[ScriptSpan]:
        if not text:
            return []
        spans: list[ScriptSpan] = []
        span_start = 0
        current_script = _script_of(text[0])
        for i in range(1, len(text)):
            script = _script_of(text[i])
            if script != current_script:
                spans.append(ScriptSpan(span_start, i, current_script))
                span_start = i
                current_script = script
        spans.append(ScriptSpan(span_start, len(text), current_script))
        return spans
