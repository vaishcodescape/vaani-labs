from __future__ import annotations

from indic_text.mock.transliterator import MockTransliterator


def test_same_script_is_identity() -> None:
    t = MockTransliterator()
    assert t.transliterate("hello", "Latin", "Latin") == "hello"


def test_devanagari_to_latin() -> None:
    t = MockTransliterator()
    result = t.transliterate("नमस्ते", "Devanagari", "Latin")
    assert result
    assert all(ord(c) < 128 or c in {"̆"} for c in result)


def test_latin_to_devanagari_roundtrip_shape() -> None:
    t = MockTransliterator()
    result = t.transliterate("namaste", "Latin", "Devanagari")
    assert any(0x0900 <= ord(c) <= 0x097F for c in result)
