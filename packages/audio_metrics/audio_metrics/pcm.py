"""Deterministic PCM16 sine-wave fixture generation and WS binary framing.

The binary frame layout implemented here (`pack_chunk_frame` /
`unpack_chunk_frame`) is the wire format documented in
docs/websocket-protocol.md: a 12-byte big-endian header
(revision_id, sequence, sample_count) followed by little-endian PCM16
mono samples.
"""

from __future__ import annotations

import math
import struct

DEFAULT_SAMPLE_RATE = 22050
BIT_DEPTH = 16
CHANNELS = 1
_HEADER_FORMAT = ">III"
HEADER_SIZE = struct.calcsize(_HEADER_FORMAT)


def generate_sine_wave_pcm16(
    *,
    frequency_hz: float,
    duration_ms: float,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    amplitude: float = 0.6,
) -> bytes:
    """Generate a mono PCM16LE sine wave. Pure function of its arguments."""
    num_samples = max(0, int(sample_rate * duration_ms / 1000))
    peak = int(amplitude * 32767)
    out = bytearray(num_samples * 2)
    angular_step = 2 * math.pi * frequency_hz / sample_rate
    for i in range(num_samples):
        value = int(peak * math.sin(angular_step * i))
        struct.pack_into("<h", out, i * 2, value)
    return bytes(out)


def chunk_pcm16(pcm: bytes, chunk_size_ms: int, sample_rate: int = DEFAULT_SAMPLE_RATE) -> list[bytes]:
    """Split raw PCM16LE bytes into fixed-duration chunks (last chunk may be shorter)."""
    if chunk_size_ms <= 0:
        raise ValueError("chunk_size_ms must be positive")
    samples_per_chunk = max(1, int(sample_rate * chunk_size_ms / 1000))
    chunk_byte_size = samples_per_chunk * 2
    return [pcm[i : i + chunk_byte_size] for i in range(0, len(pcm), chunk_byte_size)] or [b""]


def pack_chunk_frame(*, revision_id: int, sequence: int, pcm: bytes) -> bytes:
    """Pack one audio chunk into the binary WS wire format."""
    sample_count = len(pcm) // 2
    header = struct.pack(_HEADER_FORMAT, revision_id, sequence, sample_count)
    return header + pcm


def unpack_chunk_frame(frame: bytes) -> tuple[int, int, bytes]:
    """Inverse of pack_chunk_frame. Returns (revision_id, sequence, pcm_bytes)."""
    if len(frame) < HEADER_SIZE:
        raise ValueError("frame shorter than header")
    revision_id, sequence, sample_count = struct.unpack(_HEADER_FORMAT, frame[:HEADER_SIZE])
    pcm = frame[HEADER_SIZE : HEADER_SIZE + sample_count * 2]
    return revision_id, sequence, pcm


def pcm_duration_ms(pcm: bytes, sample_rate: int = DEFAULT_SAMPLE_RATE) -> float:
    num_samples = len(pcm) // 2
    return (num_samples / sample_rate) * 1000
