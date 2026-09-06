"""Deterministic heuristic language identifier.

Real LID would use a statistical/neural classifier. This mock uses
closed word lists so behavior is 100% reproducible for demos and tests:
Devanagari text is Hindi unless it contains a Marathi marker word;
Gujarati script is always Gujarati; Latin text is English unless it
contains a romanized-Hindi or romanized-Marathi marker word.
"""

from __future__ import annotations

from indic_text.models import LanguageSpan, ScriptSpan

_MARATHI_DEVANAGARI_MARKERS = frozenset(
    {"आहे", "आहेत", "मी", "तू", "तो", "ती", "करतो", "करते", "नाही", "कसा", "कशी", "मराठी"}
)
_ROMANIZED_HINDI_MARKERS = frozenset(
    {"hai", "hain", "kya", "tum", "nahi", "mujhe", "kal", "bahut", "accha", "kaise", "namaste"}
)
_ROMANIZED_MARATHI_MARKERS = frozenset(
    {"aahe", "mala", "tula", "kase", "kashi", "marathi", "nahi", "tyala"}
)


def _looks_marathi(substr: str) -> bool:
    words = substr.split()
    return any(w in _MARATHI_DEVANAGARI_MARKERS for w in words)


def _looks_romanized_hindi(substr: str) -> bool:
    words = substr.lower().split()
    return any(w in _ROMANIZED_HINDI_MARKERS for w in words)


def _looks_romanized_marathi(substr: str) -> bool:
    words = substr.lower().split()
    return any(w in _ROMANIZED_MARATHI_MARKERS for w in words)


class MockLanguageIdentifier:
    provider_id = "mock-heuristic-lid"

    def identify(self, text: str, script_spans: list[ScriptSpan]) -> list[LanguageSpan]:
        result: list[LanguageSpan] = []
        last_lang = "und"
        for span in script_spans:
            substr = text[span.start_offset : span.end_offset]
            if span.script == "Devanagari":
                lang = "mr" if _looks_marathi(substr) else "hi"
            elif span.script == "Gujarati":
                lang = "gu"
            elif span.script == "Latin":
                if _looks_romanized_marathi(substr):
                    lang = "mr"
                elif _looks_romanized_hindi(substr):
                    lang = "hi"
                else:
                    lang = "en"
            else:
                lang = last_lang
            result.append(LanguageSpan(span.start_offset, span.end_offset, lang))
            if lang != "und":
                last_lang = lang
        return result
