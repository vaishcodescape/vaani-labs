from __future__ import annotations

import json
import struct

from fastapi.testclient import TestClient


def _unpack_frame(frame: bytes) -> tuple[int, int, bytes]:
    revision_id, sequence, sample_count = struct.unpack(">III", frame[:12])
    return revision_id, sequence, frame[12 : 12 + sample_count * 2]


def _drain_until_text_type(ws, event_type: str) -> dict:
    while True:
        message = ws.receive()
        text = message.get("text")
        if text is not None:
            payload = json.loads(text)
            if payload["type"] == event_type:
                return payload


def test_session_started_on_connect(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/synthesis/stream/ws-connect") as ws:
        first = ws.receive_json()
        assert first["type"] == "session_started"
        assert first["revision_id"] == 0


def test_full_streaming_workflow_and_binary_ordering(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/synthesis/stream/ws-full") as ws:
        ws.receive_json()  # session_started
        ws.send_json(
            {
                "type": "start",
                "text": "नमस्ते दुनिया",
                "voice_id": "hi-female-1",
                "chunk_size_ms": 100,
            }
        )
        analysis = ws.receive_json()
        assert analysis["type"] == "text_analysis"
        assert len(analysis["tokens"]) > 0

        started = ws.receive_json()
        assert started["type"] == "synthesis_started"
        assert started["revision_id"] == 1

        metadata = ws.receive_json()
        assert metadata["type"] == "audio_metadata"

        sequences: list[int] = []
        revisions: set[int] = set()
        completed = None
        while completed is None:
            message = ws.receive()
            if message.get("bytes") is not None:
                revision_id, sequence, pcm = _unpack_frame(message["bytes"])
                sequences.append(sequence)
                revisions.add(revision_id)
                assert len(pcm) > 0
            elif message.get("text") is not None:
                payload = json.loads(message["text"])
                if payload["type"] == "completed":
                    completed = payload

        assert sequences == sorted(sequences)
        assert sequences == list(range(len(sequences)))
        assert revisions == {1}
        assert completed["total_chunks"] == len(sequences)
        assert completed["first_audio_latency_ms"] >= 0
        assert completed["rtf"] >= 0


def test_cancel_stops_stream(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/synthesis/stream/ws-cancel") as ws:
        ws.receive_json()
        ws.send_json(
            {
                "type": "start",
                "text": "नमस्ते दुनिया कैसे हो आप सब लोग",
                "voice_id": "hi-female-1",
                "chunk_size_ms": 50,
            }
        )
        ws.receive_json()  # text_analysis
        ws.receive_json()  # synthesis_started
        ws.receive_json()  # audio_metadata
        ws.send_json({"type": "cancel"})

        final = None
        while final is None:
            message = ws.receive()
            text = message.get("text")
            if text is not None:
                payload = json.loads(text)
                if payload["type"] in ("cancelled", "completed"):
                    final = payload
        assert final["type"] == "cancelled"


def test_edit_mid_stream_switches_to_new_revision_cleanly(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/synthesis/stream/ws-edit") as ws:
        ws.receive_json()
        text = "नमस्ते दुनिया कैसे हो आप सब लोग यहाँ पर आज"
        ws.send_json(
            {"type": "start", "text": text, "voice_id": "hi-female-1", "chunk_size_ms": 50}
        )
        ws.receive_json()  # text_analysis (rev 1)
        ws.receive_json()  # synthesis_started (rev 1)
        ws.receive_json()  # audio_metadata (rev 1)

        # Consume at least one binary frame of revision 1 before editing.
        while True:
            message = ws.receive()
            if message.get("bytes") is not None:
                break

        ws.send_json(
            {
                "type": "edit",
                "revision_id": 2,
                "unsynthesized_text": "दुनिया",
                "edit_offset_ms": 50,
            }
        )

        analysis2 = _drain_until_text_type(ws, "text_analysis")
        assert analysis2["revision_id"] == 2

        started2 = _drain_until_text_type(ws, "synthesis_started")
        assert started2["revision_id"] == 2

        completed = None
        while completed is None:
            message = ws.receive()
            if message.get("bytes") is not None:
                revision_id, _sequence, _pcm = _unpack_frame(message["bytes"])
                assert revision_id == 2  # no stale revision-1 frames leak after edit
            elif message.get("text") is not None:
                payload = json.loads(message["text"])
                if payload["type"] == "completed":
                    completed = payload
        assert completed["revision_id"] == 2


def test_edit_with_wrong_revision_id_is_rejected(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/synthesis/stream/ws-bad-edit") as ws:
        ws.receive_json()
        ws.send_json(
            {"type": "start", "text": "नमस्ते", "voice_id": "hi-female-1", "chunk_size_ms": 100}
        )
        ws.receive_json()  # text_analysis
        ws.send_json({"type": "edit", "revision_id": 99, "unsynthesized_text": "दुनिया"})
        error = _drain_until_text_type(ws, "error")
        assert error["code"] == "INVALID_REVISION_TRANSITION"


def test_buffer_underflow_simulated_once(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/synthesis/stream/ws-underflow") as ws:
        ws.receive_json()
        text = "नमस्ते दुनिया कैसे हो आप सब लोग यहाँ पर आज सुबह"
        ws.send_json(
            {"type": "start", "text": text, "voice_id": "hi-female-1", "chunk_size_ms": 50}
        )
        ws.receive_json()  # text_analysis
        ws.receive_json()  # synthesis_started
        ws.receive_json()  # audio_metadata

        warnings_seen = 0
        completed = None
        while completed is None:
            message = ws.receive()
            text_payload = message.get("text")
            if text_payload is not None:
                payload = json.loads(text_payload)
                if payload["type"] == "warning":
                    warnings_seen += 1
                    assert payload["code"] == "SIMULATED_BUFFER_UNDERFLOW"
                elif payload["type"] == "completed":
                    completed = payload
        assert warnings_seen == 1


def test_ping_pong(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/synthesis/stream/ws-ping") as ws:
        ws.receive_json()
        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"


def test_invalid_client_event_returns_structured_error(client: TestClient) -> None:
    with client.websocket_connect("/api/v1/synthesis/stream/ws-invalid") as ws:
        ws.receive_json()
        ws.send_json({"type": "not-a-real-event"})
        error = ws.receive_json()
        assert error["type"] == "error"
        assert error["code"] == "VALIDATION_ERROR"
