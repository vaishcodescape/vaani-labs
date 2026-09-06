"""Shared external-input validation (constraint #17: validate all external input)."""

from __future__ import annotations

from indic_text.constants import MAX_ANALYSE_TEXT_CODEPOINTS

from app.errors import InvalidUnicodeError, TextTooLongError, ValidationApiError


def _contains_lone_surrogate(text: str) -> bool:
    return any(0xD800 <= ord(ch) <= 0xDFFF for ch in text)


def validate_analysable_text(text: str) -> str:
    """Validate text intended for /text/analyse, /text/normalize, and synthesis endpoints."""
    if not text:
        raise ValidationApiError("text must not be empty", {"field": "text"})
    if _contains_lone_surrogate(text):
        raise InvalidUnicodeError()
    if len(text) > MAX_ANALYSE_TEXT_CODEPOINTS:
        raise TextTooLongError(MAX_ANALYSE_TEXT_CODEPOINTS)
    return text
