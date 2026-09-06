from __future__ import annotations

import base64

from fastapi.testclient import TestClient


def test_candidates_sorted_by_confidence(client: TestClient) -> None:
    r = client.post(
        "/api/v1/pronunciation/candidates",
        json={"surface": "meeting", "language": "en", "script": "Latin"},
    )
    assert r.status_code == 200
    candidates = r.json()["candidates"]
    assert len(candidates) >= 2
    confidences = [c["confidence"] for c in candidates]
    assert confidences == sorted(confidences, reverse=True)


def test_candidates_deterministic(client: TestClient) -> None:
    body = {"surface": "meeting", "language": "en", "script": "Latin"}
    r1 = client.post("/api/v1/pronunciation/candidates", json=body)
    r2 = client.post("/api/v1/pronunciation/candidates", json=body)
    assert r1.json() == r2.json()


def test_preview_returns_valid_pcm(client: TestClient) -> None:
    r = client.post(
        "/api/v1/pronunciation/preview",
        json={"surface": "meeting", "phonemes": "m iː t ɪ ŋ", "voice_id": "hi-female-1"},
    )
    assert r.status_code == 200
    body = r.json()
    pcm = base64.b64decode(body["pcm_base64"])
    assert len(pcm) > 0
    assert len(pcm) % 2 == 0  # PCM16 -> even byte count
