from __future__ import annotations

from tts_runtime.interfaces import SynthesisControls
from tts_runtime.mock.acoustic import MockAcousticModelAdapter
from tts_runtime.mock.vocoder import MockStreamingVocoderAdapter


def _plan(analysed_tokens, text: str, **control_overrides):
    tokens = analysed_tokens(text)
    controls = SynthesisControls(voice_id="hi-female-1", **control_overrides)
    return MockAcousticModelAdapter().plan(tokens, controls)


def test_chunks_are_sequential(analysed_tokens) -> None:
    plan = _plan(analysed_tokens, "नमस्ते दुनिया कैसे हो")
    chunks = list(MockStreamingVocoderAdapter().stream(plan))
    assert [c.sequence for c in chunks] == list(range(len(chunks)))


def test_last_chunk_flagged(analysed_tokens) -> None:
    plan = _plan(analysed_tokens, "नमस्ते दुनिया")
    chunks = list(MockStreamingVocoderAdapter().stream(plan))
    assert chunks[-1].is_last is True
    assert all(not c.is_last for c in chunks[:-1])


def test_deterministic_pcm(analysed_tokens) -> None:
    plan = _plan(analysed_tokens, "नमस्ते")
    a = [c.pcm for c in MockStreamingVocoderAdapter().stream(plan)]
    b = [c.pcm for c in MockStreamingVocoderAdapter().stream(plan)]
    assert a == b


def test_smaller_chunk_size_yields_more_chunks(analysed_tokens) -> None:
    plan_small = _plan(analysed_tokens, "नमस्ते दुनिया कैसे हो आप", chunk_size_ms=100)
    plan_large = _plan(analysed_tokens, "नमस्ते दुनिया कैसे हो आप", chunk_size_ms=500)
    small_chunks = list(MockStreamingVocoderAdapter().stream(plan_small))
    large_chunks = list(MockStreamingVocoderAdapter().stream(plan_large))
    assert len(small_chunks) >= len(large_chunks)


def test_slow_update_rate_affects_some_chunks(analysed_tokens) -> None:
    plan = _plan(
        analysed_tokens, "नमस्ते दुनिया कैसे हो आप सब", chunk_size_ms=100, mrss_slow_update_rate=3
    )
    chunks = list(MockStreamingVocoderAdapter().stream(plan))
    vocoder_costs = {c.vocoder_ms for c in chunks}
    assert len(vocoder_costs) == 2  # base cost and base+slow-update-extra cost


def test_empty_plan_yields_no_chunks() -> None:
    from tts_runtime.interfaces import SynthesisPlan

    plan = SynthesisPlan(
        tokens=(), controls=SynthesisControls(voice_id="v1"),
        estimated_duration_ms=0, sample_rate=22050, planning_ms=0, token_durations_ms=(),
    )
    assert list(MockStreamingVocoderAdapter().stream(plan)) == []
