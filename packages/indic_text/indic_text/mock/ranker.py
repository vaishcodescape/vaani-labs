"""Pronunciation candidate ranker.

Deliberately trivial and separated from G2P so a "smarter" ranker can be
swapped in independently of the G2P provider (see docs/model-adapter.md).
"""

from __future__ import annotations

from indic_text.models import PronunciationCandidate


class MockPronunciationRanker:
    provider_id = "mock-confidence-ranker"

    def rank(self, candidates: list[PronunciationCandidate]) -> list[PronunciationCandidate]:
        return sorted(candidates, key=lambda c: c.confidence, reverse=True)
