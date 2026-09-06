from __future__ import annotations

from audio_metrics.metrics import AudioMetricCalculator


def test_empty_summary_is_zeroed() -> None:
    calc = AudioMetricCalculator()
    summary = calc.summary()
    assert summary.total_chunks == 0
    assert summary.rtf == 0.0


def test_first_audio_latency() -> None:
    calc = AudioMetricCalculator()
    calc.start(start_time_ms=1000.0)
    calc.record_chunk(
        sequence=0, acoustic_ms=5, vocoder_ms=3, produced_at_ms=1050.0, chunk_duration_ms=200
    )
    summary = calc.summary()
    assert summary.first_audio_latency_ms == 50.0


def test_rtf_below_one_means_faster_than_real_time() -> None:
    calc = AudioMetricCalculator()
    calc.start(start_time_ms=0.0)
    calc.record_chunk(
        sequence=0, acoustic_ms=10, vocoder_ms=10, produced_at_ms=20.0, chunk_duration_ms=200
    )
    calc.record_chunk(
        sequence=1, acoustic_ms=10, vocoder_ms=10, produced_at_ms=40.0, chunk_duration_ms=200
    )
    summary = calc.summary()
    assert summary.total_duration_ms == 400
    assert summary.rtf == 40.0 / 400.0
    assert summary.rtf < 1.0


def test_percentiles_monotonic() -> None:
    calc = AudioMetricCalculator()
    calc.start(start_time_ms=0.0)
    for i in range(100):
        calc.record_chunk(
            sequence=i,
            acoustic_ms=float(i),
            vocoder_ms=0.0,
            produced_at_ms=float(i * 10),
            chunk_duration_ms=100,
        )
    summary = calc.summary()
    assert summary.p50_chunk_latency_ms <= summary.p95_chunk_latency_ms
    assert summary.p95_chunk_latency_ms <= summary.p99_chunk_latency_ms


def test_chunk_count_tracks_records() -> None:
    calc = AudioMetricCalculator()
    calc.start(start_time_ms=0.0)
    assert calc.chunk_count == 0
    calc.record_chunk(sequence=0, acoustic_ms=1, vocoder_ms=1, produced_at_ms=1, chunk_duration_ms=1)
    assert calc.chunk_count == 1
