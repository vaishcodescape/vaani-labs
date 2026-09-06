from __future__ import annotations

from indic_text.mock.g2p import MockGraphemeToPhoneme
from indic_text.models import PronunciationSource


def test_deterministic_across_calls() -> None:
    g2p = MockGraphemeToPhoneme()
    a = g2p.to_phonemes("meeting", "en", "Latin")
    b = g2p.to_phonemes("meeting", "en", "Latin")
    assert a == b


def test_devanagari_has_higher_confidence_than_latin() -> None:
    g2p = MockGraphemeToPhoneme()
    hi = g2p.to_phonemes("नमस्ते", "hi", "Devanagari")[0]
    en = g2p.to_phonemes("meeting", "en", "Latin")[0]
    assert hi.confidence > en.confidence


def test_returns_at_least_two_candidates() -> None:
    g2p = MockGraphemeToPhoneme()
    candidates = g2p.to_phonemes("meeting", "en", "Latin")
    assert len(candidates) >= 2
    assert candidates[0].source is PronunciationSource.G2P
    assert all(c.source.value == "g2p-alt" for c in candidates[1:])


def test_confidence_in_valid_range() -> None:
    g2p = MockGraphemeToPhoneme()
    for surface in ["meeting", "नमस्ते", "office", "हाय", ""]:
        for c in g2p.to_phonemes(surface, "en", "Latin"):
            assert 0.0 <= c.confidence <= 1.0
