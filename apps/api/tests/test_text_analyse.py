from __future__ import annotations

from fastapi.testclient import TestClient


def test_mixed_devanagari_and_latin(client: TestClient) -> None:
    r = client.post("/api/v1/text/analyse", json={"text": "मुझे कल 5 बजे meeting है।"})
    assert r.status_code == 200
    body = r.json()
    languages = {t["language"] for t in body["tokens"] if t["token_type"] == "word"}
    assert "hi" in languages
    assert "en" in languages
    assert len(body["code_switch_spans"]) >= 1


def test_mixed_gujarati_and_latin(client: TestClient) -> None:
    r = client.post("/api/v1/text/analyse", json={"text": "હું office જાઉં છું"})
    assert r.status_code == 200
    languages = {t["language"] for t in r.json()["tokens"] if t["token_type"] == "word"}
    assert "gu" in languages
    assert "en" in languages


def test_marathi_text(client: TestClient) -> None:
    r = client.post("/api/v1/text/analyse", json={"text": "मी मराठी आहे"})
    assert r.status_code == 200
    languages = {t["language"] for t in r.json()["tokens"] if t["token_type"] == "word"}
    assert languages == {"mr"}


def test_numbers(client: TestClient) -> None:
    r = client.post("/api/v1/text/analyse", json={"text": "5 बजे"})
    assert r.status_code == 200
    number_token = r.json()["tokens"][0]
    assert number_token["token_type"] == "number"
    assert number_token["normalized"] == "पाँच"


def test_dates(client: TestClient) -> None:
    r = client.post("/api/v1/text/analyse", json={"text": "06/09/2026"})
    assert r.status_code == 200
    token = r.json()["tokens"][0]
    assert token["token_type"] == "date"
    assert "सितंबर" in token["normalized"]


def test_abbreviations(client: TestClient) -> None:
    r = client.post("/api/v1/text/analyse", json={"text": "Dr. Sharma"})
    assert r.status_code == 200
    token = r.json()["tokens"][0]
    assert token["token_type"] == "abbreviation"
    assert token["normalized"] == "डॉक्टर"


def test_empty_input_is_rejected(client: TestClient) -> None:
    r = client.post("/api/v1/text/analyse", json={"text": ""})
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_unicode_is_rejected(client: TestClient) -> None:
    # A raw JSON `\uD800` escape decodes to a lone (unpaired) surrogate
    # codepoint. Real UTF-8 bytes can never encode one directly (that's
    # exactly why it's invalid) — this is how a client actually smuggles
    # one in: as an escape sequence inside an otherwise-ASCII JSON body.
    raw_body = b'{"text": "hello \\ud800 world"}'
    r = client.post(
        "/api/v1/text/analyse", content=raw_body, headers={"content-type": "application/json"}
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "INVALID_UTF8"


def test_very_long_input_is_rejected(client: TestClient) -> None:
    r = client.post("/api/v1/text/analyse", json={"text": "क " * 3000})
    assert r.status_code == 413
    assert r.json()["error"]["code"] == "TEXT_TOO_LONG"


def test_very_long_input_within_limit_succeeds(client: TestClient) -> None:
    r = client.post("/api/v1/text/analyse", json={"text": "क " * 100})
    assert r.status_code == 200


def test_normalize_endpoint(client: TestClient) -> None:
    r = client.post("/api/v1/text/normalize", json={"text": "5"})
    assert r.status_code == 200
    assert r.json()["normalized"] == "पाँच"


def test_uncertain_pronunciation_flagged(client: TestClient) -> None:
    r = client.post("/api/v1/text/analyse", json={"text": "meeting"})
    token = r.json()["tokens"][0]
    assert token["pronunciation"]["confidence"] < 1.0
