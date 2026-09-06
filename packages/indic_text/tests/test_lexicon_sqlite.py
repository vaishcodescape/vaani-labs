from __future__ import annotations

import pytest

from indic_text.lexicon_sqlite import LexiconConflictError, SqliteLexicon


def test_create_and_get(lexicon: SqliteLexicon) -> None:
    entry = lexicon.create("meeting", "en", "m iː t ɪ ŋ", "note")
    assert entry.surface == "meeting"
    fetched = lexicon.get("meeting", "en")
    assert fetched is not None
    assert fetched.id == entry.id


def test_create_conflict_raises(lexicon: SqliteLexicon) -> None:
    lexicon.create("meeting", "en", "m iː t ɪ ŋ", "")
    with pytest.raises(LexiconConflictError):
        lexicon.create("meeting", "en", "different", "")


def test_update(lexicon: SqliteLexicon) -> None:
    entry = lexicon.create("meeting", "en", "old", "")
    updated = lexicon.update(entry.id, phonemes="new", notes="updated note")
    assert updated is not None
    assert updated.phonemes == "new"
    assert updated.notes == "updated note"
    assert updated.updated_at >= entry.updated_at


def test_update_missing_returns_none(lexicon: SqliteLexicon) -> None:
    assert lexicon.update("does-not-exist", phonemes="x", notes=None) is None


def test_delete(lexicon: SqliteLexicon) -> None:
    entry = lexicon.create("meeting", "en", "m iː t ɪ ŋ", "")
    assert lexicon.delete(entry.id) is True
    assert lexicon.get("meeting", "en") is None
    assert lexicon.delete(entry.id) is False


def test_list_filters_by_query_and_language(lexicon: SqliteLexicon) -> None:
    lexicon.create("meeting", "en", "a", "")
    lexicon.create("schedule", "en", "b", "")
    lexicon.create("बैठक", "hi", "c", "")
    assert len(lexicon.list()) == 3
    assert len(lexicon.list(query="meet")) == 1
    assert len(lexicon.list(language="hi")) == 1


def test_count(lexicon: SqliteLexicon) -> None:
    assert lexicon.count() == 0
    lexicon.create("meeting", "en", "a", "")
    assert lexicon.count() == 1
