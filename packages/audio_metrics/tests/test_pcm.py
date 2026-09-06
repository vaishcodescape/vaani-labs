from __future__ import annotations

import pytest

from audio_metrics.pcm import (
    HEADER_SIZE,
    chunk_pcm16,
    generate_sine_wave_pcm16,
    pack_chunk_frame,
    pcm_duration_ms,
    unpack_chunk_frame,
)


def test_sine_wave_length_matches_duration() -> None:
    pcm = generate_sine_wave_pcm16(frequency_hz=220, duration_ms=1000, sample_rate=16000)
    assert len(pcm) == 16000 * 2


def test_sine_wave_deterministic() -> None:
    a = generate_sine_wave_pcm16(frequency_hz=440, duration_ms=100)
    b = generate_sine_wave_pcm16(frequency_hz=440, duration_ms=100)
    assert a == b


def test_sine_wave_within_amplitude_bounds() -> None:
    import struct

    pcm = generate_sine_wave_pcm16(frequency_hz=440, duration_ms=50, amplitude=0.5)
    samples = struct.unpack(f"<{len(pcm)//2}h", pcm)
    assert max(samples) <= 32767 * 0.5 + 1
    assert min(samples) >= -32767 * 0.5 - 1


def test_chunking_covers_all_samples() -> None:
    pcm = generate_sine_wave_pcm16(frequency_hz=100, duration_ms=505, sample_rate=1000)
    chunks = chunk_pcm16(pcm, chunk_size_ms=100, sample_rate=1000)
    assert b"".join(chunks) == pcm
    assert len(chunks) == 6  # 500ms of full chunks + 5ms remainder


def test_chunk_size_must_be_positive() -> None:
    with pytest.raises(ValueError):
        chunk_pcm16(b"\x00\x00", chunk_size_ms=0)


def test_pack_unpack_roundtrip() -> None:
    pcm = generate_sine_wave_pcm16(frequency_hz=300, duration_ms=20)
    frame = pack_chunk_frame(revision_id=3, sequence=7, pcm=pcm)
    revision_id, sequence, unpacked_pcm = unpack_chunk_frame(frame)
    assert revision_id == 3
    assert sequence == 7
    assert unpacked_pcm == pcm
    assert len(frame) == HEADER_SIZE + len(pcm)


def test_unpack_rejects_short_frame() -> None:
    with pytest.raises(ValueError):
        unpack_chunk_frame(b"\x00\x00")


def test_pcm_duration_ms() -> None:
    pcm = generate_sine_wave_pcm16(frequency_hz=440, duration_ms=250, sample_rate=8000)
    assert abs(pcm_duration_ms(pcm, sample_rate=8000) - 250) < 1
