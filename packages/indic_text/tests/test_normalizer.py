from __future__ import annotations

from indic_text.mock.normalizer import MockTextNormalizer
from indic_text.models import TokenType


def test_number_normalization() -> None:
    n = MockTextNormalizer()
    assert n.normalize("5", TokenType.NUMBER) == "पाँच"
    assert n.normalize("0", TokenType.NUMBER) == "शून्य"
    assert n.normalize("21", TokenType.NUMBER) == "बीस एक"


def test_date_normalization() -> None:
    n = MockTextNormalizer()
    result = n.normalize("06/09/2026", TokenType.DATE)
    assert "सितंबर" in result
    assert "2026" in result


def test_abbreviation_normalization() -> None:
    n = MockTextNormalizer()
    assert n.normalize("Dr.", TokenType.ABBREVIATION) == "डॉक्टर"
    assert n.normalize("e.g.", TokenType.ABBREVIATION) == "उदाहरण के लिए"


def test_unknown_abbreviation_falls_back_to_surface() -> None:
    n = MockTextNormalizer()
    assert n.normalize("Xy.", TokenType.ABBREVIATION) == "Xy."


def test_word_nfc_normalization() -> None:
    n = MockTextNormalizer()
    combining = "न" + "ा"  # ना as base + combining vowel sign
    assert n.normalize(combining, TokenType.WORD) == "ना"
