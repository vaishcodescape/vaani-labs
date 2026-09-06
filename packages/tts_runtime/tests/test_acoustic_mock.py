from __future__ import annotations

from tts_runtime.interfaces import SynthesisControls
from tts_runtime.mock.acoustic import MockAcousticModelAdapter


def test_plan_is_deterministic(analysed_tokens) -> None:
    tokens = analysed_tokens("मुझे कल 5 बजे meeting है।")
    controls = SynthesisControls(voice_id="hi-female-1")
    adapter = MockAcousticModelAdapter()
    plan_a = adapter.plan(tokens, controls)
    plan_b = adapter.plan(tokens, controls)
    assert plan_a.estimated_duration_ms == plan_b.estimated_duration_ms
    assert plan_a.token_durations_ms == plan_b.token_durations_ms


def test_higher_speed_shortens_duration(analysed_tokens) -> None:
    tokens = analysed_tokens("नमस्ते दुनिया")
    adapter = MockAcousticModelAdapter()
    slow = adapter.plan(tokens, SynthesisControls(voice_id="v1", speed=0.5))
    fast = adapter.plan(tokens, SynthesisControls(voice_id="v1", speed=2.0))
    assert fast.estimated_duration_ms < slow.estimated_duration_ms


def test_token_durations_align_with_tokens(analysed_tokens) -> None:
    tokens = analysed_tokens("hi there")
    adapter = MockAcousticModelAdapter()
    plan = adapter.plan(tokens, SynthesisControls(voice_id="v1"))
    assert len(plan.token_durations_ms) == len(tokens)
    assert all(d >= 0 for d in plan.token_durations_ms)


def test_empty_tokens_yields_zero_duration() -> None:
    adapter = MockAcousticModelAdapter()
    plan = adapter.plan([], SynthesisControls(voice_id="v1"))
    assert plan.estimated_duration_ms == 0
    assert plan.token_durations_ms == ()
