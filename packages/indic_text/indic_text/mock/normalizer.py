"""Deterministic text normalizer.

Numbers -> Hindi number words, dates -> spoken Hindi date form,
abbreviations -> a small expansion table, everything else -> NFC form.
This is a mock: coverage is intentionally limited to what the demo
sample sentences exercise, with safe fallbacks for anything else.
"""

from __future__ import annotations

import unicodedata

from indic_text.models import TokenType

_ONES = ["", "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ"]
_TEENS = [
    "दस", "ग्यारह", "बारह", "तेरह", "चौदह", "पंद्रह",
    "सोलह", "सत्रह", "अठारह", "उन्नीस",
]
_TENS = [
    "", "", "बीस", "तीस", "चालीस", "पचास", "साठ", "सत्तर", "अस्सी", "नब्बे",
]

_MONTHS_HI = [
    "जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून",
    "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर",
]

_ABBREVIATIONS = {
    "dr.": "डॉक्टर",
    "mr.": "मिस्टर",
    "mrs.": "मिसेज़",
    "e.g.": "उदाहरण के लिए",
    "i.e.": "अर्थात",
    "etc.": "इत्यादि",
    "u.s.": "यू. एस.",
    "u.k.": "यू. के.",
}


def _number_to_hindi_words(n: int) -> str:
    if n == 0:
        return "शून्य"
    if n < 0:
        return "ऋण " + _number_to_hindi_words(-n)
    if n < 10:
        return _ONES[n]
    if n < 20:
        return _TEENS[n - 10]
    if n < 100:
        tens, ones = divmod(n, 10)
        return _TENS[tens] + (f" {_ONES[ones]}" if ones else "")
    if n < 1000:
        hundreds, rest = divmod(n, 100)
        prefix = f"{_ONES[hundreds]} सौ"
        return prefix + (f" {_number_to_hindi_words(rest)}" if rest else "")
    if n < 100000:
        thousands, rest = divmod(n, 1000)
        prefix = f"{_number_to_hindi_words(thousands)} हज़ार"
        return prefix + (f" {_number_to_hindi_words(rest)}" if rest else "")
    # Fallback for very large numbers: read digit by digit.
    return " ".join(_ONES[int(d)] if d != "0" else "शून्य" for d in str(n))


def _normalize_number(surface: str) -> str:
    cleaned = surface.replace(",", "")
    try:
        if "." in cleaned:
            whole, frac = cleaned.split(".", 1)
            whole_words = _number_to_hindi_words(int(whole)) if whole else "शून्य"
            frac_words = " ".join(_ONES[int(d)] if d != "0" else "शून्य" for d in frac)
            return f"{whole_words} दशमलव {frac_words}"
        return _number_to_hindi_words(int(cleaned))
    except ValueError:
        return surface


def _normalize_date(surface: str) -> str:
    sep = "/" if "/" in surface else "-"
    parts = surface.split(sep)
    if len(parts) != 3:
        return surface
    try:
        day, month, year = (int(p) for p in parts)
        if not (1 <= month <= 12):
            return surface
        return f"{_number_to_hindi_words(day)} {_MONTHS_HI[month - 1]} {year}"
    except ValueError:
        return surface


def _normalize_abbreviation(surface: str) -> str:
    return _ABBREVIATIONS.get(surface.lower(), surface)


class MockTextNormalizer:
    provider_id = "mock-rule-normalizer"

    def normalize(self, surface: str, token_type: TokenType) -> str:
        if token_type is TokenType.NUMBER:
            return _normalize_number(surface)
        if token_type is TokenType.DATE:
            return _normalize_date(surface)
        if token_type is TokenType.ABBREVIATION:
            return _normalize_abbreviation(surface)
        return unicodedata.normalize("NFC", surface)
