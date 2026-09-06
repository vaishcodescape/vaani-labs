from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_read_update_delete(client: TestClient) -> None:
    create = client.post(
        "/api/v1/lexicon",
        json={"surface": "meeting", "language": "en", "phonemes": "m iː t ɪ ŋ", "notes": "demo"},
    )
    assert create.status_code == 201
    entry_id = create.json()["id"]

    listed = client.get("/api/v1/lexicon")
    assert listed.status_code == 200
    assert len(listed.json()["entries"]) == 1

    updated = client.patch(f"/api/v1/lexicon/{entry_id}", json={"notes": "updated"})
    assert updated.status_code == 200
    assert updated.json()["notes"] == "updated"
    assert updated.json()["phonemes"] == "m iː t ɪ ŋ"

    deleted = client.delete(f"/api/v1/lexicon/{entry_id}")
    assert deleted.status_code == 204

    listed_after = client.get("/api/v1/lexicon")
    assert listed_after.json()["entries"] == []


def test_create_conflict(client: TestClient) -> None:
    body = {"surface": "meeting", "language": "en", "phonemes": "a", "notes": ""}
    first = client.post("/api/v1/lexicon", json=body)
    assert first.status_code == 201
    second = client.post("/api/v1/lexicon", json=body)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "LEXICON_CONFLICT"


def test_update_missing_returns_404(client: TestClient) -> None:
    r = client.patch("/api/v1/lexicon/does-not-exist", json={"notes": "x"})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"


def test_delete_missing_returns_404(client: TestClient) -> None:
    r = client.delete("/api/v1/lexicon/does-not-exist")
    assert r.status_code == 404


def test_list_filters(client: TestClient) -> None:
    client.post("/api/v1/lexicon", json={"surface": "meeting", "language": "en", "phonemes": "a"})
    client.post("/api/v1/lexicon", json={"surface": "schedule", "language": "en", "phonemes": "b"})
    client.post("/api/v1/lexicon", json={"surface": "बैठक", "language": "hi", "phonemes": "c"})

    by_query = client.get("/api/v1/lexicon", params={"q": "meet"})
    assert len(by_query.json()["entries"]) == 1

    by_language = client.get("/api/v1/lexicon", params={"language": "hi"})
    assert len(by_language.json()["entries"]) == 1


def test_lexicon_override_takes_precedence_in_analysis(client: TestClient) -> None:
    client.post(
        "/api/v1/lexicon",
        json={"surface": "meeting", "language": "en", "phonemes": "CUSTOM", "notes": ""},
    )
    r = client.post("/api/v1/text/analyse", json={"text": "meeting"})
    token = r.json()["tokens"][0]
    assert token["pronunciation"]["phonemes"] == "CUSTOM"
    assert token["pronunciation"]["source"] == "lexicon"
    assert token["pronunciation"]["is_uncertain"] is False
