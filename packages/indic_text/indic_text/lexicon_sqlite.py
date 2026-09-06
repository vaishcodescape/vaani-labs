"""SQLite-backed implementation of the PronunciationLexicon protocol.

Deliberately not an ORM: one table, simple CRUD, a single lock for
thread safety (FastAPI's sync path handlers run in a thread pool). If a
future real deployment needs Postgres, implement the same protocol in a
new module — no API-layer changes required.
"""

from __future__ import annotations

import sqlite3
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

from indic_text.models import LexiconEntry

_SCHEMA = """
CREATE TABLE IF NOT EXISTS lexicon_entries (
    id TEXT PRIMARY KEY,
    surface TEXT NOT NULL,
    language TEXT NOT NULL,
    phonemes TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(surface, language)
)
"""


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _row_to_entry(row: sqlite3.Row) -> LexiconEntry:
    return LexiconEntry(
        id=row["id"],
        surface=row["surface"],
        language=row["language"],
        phonemes=row["phonemes"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class LexiconConflictError(Exception):
    """Raised when creating an entry whose (surface, language) already exists."""


class SqliteLexicon:
    provider_id = "sqlite-lexicon"

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock, self._conn:
            self._conn.execute(_SCHEMA)

    def get(self, surface: str, language: str) -> LexiconEntry | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM lexicon_entries WHERE surface = ? AND language = ?",
                (surface, language),
            ).fetchone()
        return _row_to_entry(row) if row else None

    def get_by_id(self, entry_id: str) -> LexiconEntry | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM lexicon_entries WHERE id = ?", (entry_id,)
            ).fetchone()
        return _row_to_entry(row) if row else None

    def list(self, query: str | None = None, language: str | None = None) -> list[LexiconEntry]:
        sql = "SELECT * FROM lexicon_entries WHERE 1=1"
        params: list[str] = []
        if query:
            sql += " AND surface LIKE ?"
            params.append(f"%{query}%")
        if language:
            sql += " AND language = ?"
            params.append(language)
        sql += " ORDER BY updated_at DESC"
        with self._lock:
            rows = self._conn.execute(sql, params).fetchall()
        return [_row_to_entry(r) for r in rows]

    def create(self, surface: str, language: str, phonemes: str, notes: str) -> LexiconEntry:
        if self.get(surface, language) is not None:
            raise LexiconConflictError(f"{surface!r}/{language!r} already exists")
        entry_id = uuid.uuid4().hex[:12]
        now = _now()
        with self._lock, self._conn:
            self._conn.execute(
                "INSERT INTO lexicon_entries "
                "(id, surface, language, phonemes, notes, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (entry_id, surface, language, phonemes, notes, now, now),
            )
        entry = self.get_by_id(entry_id)
        assert entry is not None
        return entry

    def update(
        self, entry_id: str, phonemes: str | None, notes: str | None
    ) -> LexiconEntry | None:
        existing = self.get_by_id(entry_id)
        if existing is None:
            return None
        new_phonemes = phonemes if phonemes is not None else existing.phonemes
        new_notes = notes if notes is not None else existing.notes
        with self._lock, self._conn:
            self._conn.execute(
                "UPDATE lexicon_entries SET phonemes = ?, notes = ?, updated_at = ? WHERE id = ?",
                (new_phonemes, new_notes, _now(), entry_id),
            )
        return self.get_by_id(entry_id)

    def delete(self, entry_id: str) -> bool:
        with self._lock, self._conn:
            cursor = self._conn.execute(
                "DELETE FROM lexicon_entries WHERE id = ?", (entry_id,)
            )
        return cursor.rowcount > 0

    def count(self) -> int:
        with self._lock:
            row = self._conn.execute("SELECT COUNT(*) AS c FROM lexicon_entries").fetchone()
        return int(row["c"])

    def close(self) -> None:
        with self._lock:
            self._conn.close()
