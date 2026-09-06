from __future__ import annotations

from indic_text.mock.ranker import MockPronunciationRanker
from indic_text.models import PronunciationCandidate, PronunciationSource


def test_ranks_descending_by_confidence() -> None:
    candidates = [
        PronunciationCandidate("a", 0.2, PronunciationSource.G2P_ALT),
        PronunciationCandidate("b", 0.9, PronunciationSource.G2P),
        PronunciationCandidate("c", 0.5, PronunciationSource.G2P_ALT),
    ]
    ranked = MockPronunciationRanker().rank(candidates)
    assert [c.phonemes for c in ranked] == ["b", "c", "a"]


def test_empty_input() -> None:
    assert MockPronunciationRanker().rank([]) == []
