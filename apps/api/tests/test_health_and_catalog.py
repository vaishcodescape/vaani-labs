from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_system(client: TestClient) -> None:
    r = client.get("/api/v1/system")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "script_detector" in body["providers"]
    assert body["lexicon_entry_count"] == 0


def test_models(client: TestClient) -> None:
    r = client.get("/api/v1/models")
    assert r.status_code == 200
    assert r.json()["acoustic_models"][0]["kind"] == "mock"


def test_voices(client: TestClient) -> None:
    r = client.get("/api/v1/voices")
    assert r.status_code == 200
    assert len(r.json()["voices"]) > 0


def test_languages(client: TestClient) -> None:
    r = client.get("/api/v1/languages")
    assert r.status_code == 200
    codes = {lang["code"] for lang in r.json()["languages"]}
    assert {"hi", "gu", "mr", "en"} <= codes
