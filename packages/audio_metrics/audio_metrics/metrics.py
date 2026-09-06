"""Streaming latency and real-time-factor bookkeeping.

Kept independent of any specific model/vocoder: it only consumes
timestamps and durations that the caller (tts_runtime's streaming
session) already knows, so it works identically for mock and real
providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ChunkRecord:
    sequence: int
    acoustic_ms: float
    vocoder_ms: float
    chunk_latency_ms: float
    produced_at_ms: float


@dataclass(frozen=True, slots=True)
class MetricsSummary:
    total_chunks: int
    total_duration_ms: float
    rtf: float
    first_audio_latency_ms: float
    p50_chunk_latency_ms: float
    p95_chunk_latency_ms: float
    p99_chunk_latency_ms: float


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * p
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = rank - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


@dataclass
class AudioMetricCalculator:
    """Stateful per-revision metric accumulator.

    One instance is created per streaming revision by
    `tts_runtime.session.StreamingSynthesisSession`.
    """

    provider_id: str = field(default="in-process-audio-metrics", init=False)
    _start_time_ms: float | None = field(default=None, init=False)
    _records: list[ChunkRecord] = field(default_factory=list, init=False)
    _audio_duration_ms: float = field(default=0.0, init=False)

    def start(self, start_time_ms: float) -> None:
        self._start_time_ms = start_time_ms
        self._records = []
        self._audio_duration_ms = 0.0

    def record_chunk(
        self,
        *,
        sequence: int,
        acoustic_ms: float,
        vocoder_ms: float,
        produced_at_ms: float,
        chunk_duration_ms: float,
    ) -> ChunkRecord:
        record = ChunkRecord(
            sequence=sequence,
            acoustic_ms=acoustic_ms,
            vocoder_ms=vocoder_ms,
            chunk_latency_ms=acoustic_ms + vocoder_ms,
            produced_at_ms=produced_at_ms,
        )
        self._records.append(record)
        self._audio_duration_ms += chunk_duration_ms
        return record

    @property
    def chunk_count(self) -> int:
        return len(self._records)

    def summary(self) -> MetricsSummary:
        if not self._records or self._start_time_ms is None:
            return MetricsSummary(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        latencies = [r.chunk_latency_ms for r in self._records]
        first_audio_latency_ms = self._records[0].produced_at_ms - self._start_time_ms
        total_processing_ms = self._records[-1].produced_at_ms - self._start_time_ms
        rtf = (total_processing_ms / self._audio_duration_ms) if self._audio_duration_ms else 0.0
        return MetricsSummary(
            total_chunks=len(self._records),
            total_duration_ms=self._audio_duration_ms,
            rtf=rtf,
            first_audio_latency_ms=first_audio_latency_ms,
            p50_chunk_latency_ms=_percentile(latencies, 0.50),
            p95_chunk_latency_ms=_percentile(latencies, 0.95),
            p99_chunk_latency_ms=_percentile(latencies, 0.99),
        )
