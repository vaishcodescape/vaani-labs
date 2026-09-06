"""Deterministic, script-agnostic tokenizer.

Splits raw text into words, numbers, dates, abbreviations, punctuation,
and whitespace. Uses the third-party `regex` module (not stdlib `re`)
specifically for `\\p{L}`/`\\p{M}` Unicode property classes: stdlib
`\\w` does NOT include combining marks (Unicode category Mn/Mc), so a
Devanagari/Gujarati vowel sign (matra) immediately following its base
consonant — e.g. the "ु" in "मुझे" — would otherwise be split off into
its own "punctuation" token instead of staying attached to the word.
This is intentionally simple otherwise — it exists to feed the rest of
the mock pipeline with stable, reproducible tokens, not to be a
linguistically complete tokenizer.
"""

from __future__ import annotations

import regex

from indic_text.models import RawToken, TokenType

_DATE_PATTERN = r"\p{Nd}{1,2}[/-]\p{Nd}{1,2}[/-]\p{Nd}{2,4}"
_ABBREVIATION_PATTERN = r"(?:[A-Za-z]\.){2,}|[A-Z][a-z]{0,3}\."
_NUMBER_PATTERN = r"\p{Nd}+(?:[.,]\p{Nd}+)*"
_WORD_PATTERN = r"[\p{L}\p{M}]+"
_WHITESPACE_PATTERN = r"\s+"
_PUNCTUATION_PATTERN = r"[^\w\s]"

_TOKEN_RE = regex.compile(
    "|".join(
        f"(?P<{name}>{pattern})"
        for name, pattern in [
            ("date", _DATE_PATTERN),
            ("abbreviation", _ABBREVIATION_PATTERN),
            ("number", _NUMBER_PATTERN),
            ("word", _WORD_PATTERN),
            ("whitespace", _WHITESPACE_PATTERN),
            ("punctuation", _PUNCTUATION_PATTERN),
        ]
    ),
    regex.UNICODE,
)


def tokenize(text: str) -> list[RawToken]:
    """Tokenize `text` into an ordered list of RawToken.

    Every codepoint of `text` is covered by exactly one token (offsets
    are contiguous and non-overlapping), so downstream consumers can
    reconstruct `text` by concatenating `surface` in order.
    """
    tokens: list[RawToken] = []
    for i, match in enumerate(_TOKEN_RE.finditer(text)):
        kind = match.lastgroup
        assert kind is not None
        tokens.append(
            RawToken(
                index=i,
                surface=match.group(),
                start_offset=match.start(),
                end_offset=match.end(),
                token_type=TokenType(kind),
            )
        )
    return tokens
