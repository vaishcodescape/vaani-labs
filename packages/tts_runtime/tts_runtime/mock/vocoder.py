"""Deterministic sine-wave streaming vocoder mock ("MRSS-Vocos" stand-in).

Concatenates a short sine tone per token (frequency derived from voice
+ token content, so the audio audibly changes token to token rather
than being a flat drone), then slices the full utterance into
fixed-duration chunks. Per-chunk `acoustic_ms`/`vocoder_ms` are
simulated costs, not real compute time — the caller (StreamingSynthesisSession)
decides whether to actually sleep for that long.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator

from audio_metrics.pcm import (
    DEFAULT_SAMPLE_RATE,
    chunk_pcm16,
    generate_sine_wave_pcm16,
    pcm_duration_ms,
)

from tts_runtime.interfaces import AudioChunk, SynthesisPlan

_BASE_FREQUENCY_HZ = 180.0
_VOCODER_BASE_MS = 8.0
_VOCODER_SLOW_UPDATE_EXTRA_MS = 12.0
"""Extra simulated cost when MRSS recomputes slow-path conditioning."""
_ACOUSTIC_BASE_MS = 5.0


def _digest_int(text: str, salt: str) -> int:
    h = hashlib.sha256(f"{salt}:{text}".encode()).hexdigest()
    return int(h[:8], 16)


def _token_frequency_hz(surface: str, voice_id: str, pitch_semitones: float) -> float:
    voice_offset = (_digest_int(voice_id, "voice") % 60) - 30  # -30..+29 Hz
    token_offset = (_digest_int(surface, "token") % 120) - 60  # -60..+59 Hz
    base = _BASE_FREQUENCY_HZ + voice_offset + token_offset
    pitch_ratio = 2 ** (pitch_semitones / 12.0)
    return max(base * pitch_ratio, 40.0)


class MockStreamingVocoderAdapter:
    provider_id = "mock-sine-mrss-vocos"

    def stream(self, plan: SynthesisPlan) -> Iterator[AudioChunk]:
        sample_rate = plan.sample_rate or DEFAULT_SAMPLE_RATE
        amplitude = min(max(plan.controls.energy, 0.0), 2.0) * 0.4
        amplitude = min(amplitude, 0.9)

        pcm_parts: list[bytes] = []
        for token, duration_ms in zip(plan.tokens, plan.token_durations_ms):
            if duration_ms <= 0:
                continue
            frequency = _token_frequency_hz(token.surface, plan.controls.voice_id, plan.controls.pitch)
            pcm_parts.append(
                generate_sine_wave_pcm16(
                    frequency_hz=frequency,
                    duration_ms=duration_ms,
                    sample_rate=sample_rate,
                    amplitude=amplitude,
                )
            )
        full_pcm = b"".join(pcm_parts)

        chunk_size_ms = max(plan.controls.chunk_size_ms, 20)
        chunks = chunk_pcm16(full_pcm, chunk_size_ms, sample_rate=sample_rate) if full_pcm else []

        slow_update_rate = max(plan.controls.mrss_slow_update_rate, 1)
        for i, chunk_bytes in enumerate(chunks):
            is_slow_update = i % slow_update_rate == 0
            vocoder_ms = _VOCODER_BASE_MS + (_VOCODER_SLOW_UPDATE_EXTRA_MS if is_slow_update else 0.0)
            acoustic_ms = _ACOUSTIC_BASE_MS + 0.01 * (len(chunk_bytes) / 2)
            yield AudioChunk(
                sequence=i,
                pcm=chunk_bytes,
                duration_ms=pcm_duration_ms(chunk_bytes, sample_rate=sample_rate),
                acoustic_ms=acoustic_ms,
                vocoder_ms=vocoder_ms,
                is_last=(i == len(chunks) - 1),
            )
