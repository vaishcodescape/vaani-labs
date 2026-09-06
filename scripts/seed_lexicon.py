#!/usr/bin/env python3
"""Seed the pronunciation lexicon with a few demo corrections.

Run via `make seed`. Idempotent — skips entries that already exist so
it's safe to re-run before every demo.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "packages" / "indic_text"))

from indic_text.lexicon_sqlite import LexiconConflictError, SqliteLexicon  # noqa: E402

SEED_ENTRIES = [
    ("meeting", "en", "m iː t ɪ ŋ", "Corrected during demo prep — default G2P candidate was noisier."),
    ("schedule", "en", "ʃ ɛ d j uː l", "British pronunciation preferred for this demo audience."),
]


def main() -> None:
    db_path = REPO_ROOT / "data" / "lexicons" / "lexicon.db"
    lexicon = SqliteLexicon(db_path)
    for surface, language, phonemes, notes in SEED_ENTRIES:
        try:
            lexicon.create(surface, language, phonemes, notes)
            print(f"created {surface!r} ({language})")
        except LexiconConflictError:
            print(f"skipped {surface!r} ({language}) — already exists")
    lexicon.close()


if __name__ == "__main__":
    main()
