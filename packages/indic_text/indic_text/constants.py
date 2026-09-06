"""Shared constants for the indic_text package.

Kept in one module so the uncertainty threshold used by the ranker, the
API layer, and the frontend documentation all agree on the same number.
"""

from __future__ import annotations

PRONUNCIATION_UNCERTAINTY_THRESHOLD: float = 0.7
"""Candidates with confidence strictly below this are flagged uncertain."""

MAX_ANALYSE_TEXT_CODEPOINTS: int = 5000
"""Upper bound on request text length for /text/analyse, enforced at the API boundary."""
