from __future__ import annotations

import base64

from fastapi.testclient import TestClient


def test_offline_synthesis_returns_full_pcm(client: TestClient) -> None:
    r = client.post(
        "/api/v1/synthesis/offline",
        json={"text": "नमस्ते दुनिया", "voice_id": "hi-female-1", "speed": 1.0},
    )
    assert r.status_code == 200
    body = r.json()
    pcm = base64.b64decode(body["pcm_base64"])
    assert len(pcm) > 0
    assert body["duration_ms"] > 0
    assert body["rtf"] >= 0.0
    assert body["sample_rate"] == 22050


def test_offline_synthesis_rejects_empty_text(client: TestClient) -> None:
    r = client.post("/api/v1/synthesis/offline", json={"text": "", "voice_id": "hi-female-1"})
    assert r.status_code == 422


def test_offline_synthesis_rejects_out_of_range_speed(client: TestClient) -> None:
    r = client.post(
        "/api/v1/synthesis/offline",
        json={"text": "नमस्ते", "voice_id": "hi-female-1", "speed": 10.0},
    )
    assert r.status_code == 422
