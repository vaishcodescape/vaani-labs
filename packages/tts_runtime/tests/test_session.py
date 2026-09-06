from __future__ import annotations

import asyncio

from tts_runtime.interfaces import SynthesisControls
from tts_runtime.mock.acoustic import MockAcousticModelAdapter
from tts_runtime.mock.vocoder import MockStreamingVocoderAdapter
from tts_runtime.session import BinaryChunkEvent, JsonEvent, SessionState, StreamingSynthesisSession


def make_session(**kwargs) -> StreamingSynthesisSession:
    return StreamingSynthesisSession(
        "sess-1",
        acoustic_model=MockAcousticModelAdapter(),
        vocoder=MockStreamingVocoderAdapter(),
        real_time=False,
        **kwargs,
    )


async def collect(gen):
    return [event async for event in gen]


async def test_start_emits_expected_event_sequence(analysed_tokens) -> None:
    tokens = analysed_tokens("नमस्ते दुनिया")
    session = make_session()
    events = await collect(
        session.start(tokens, SynthesisControls(voice_id="v1", chunk_size_ms=200))
    )
    types = [e.type for e in events if isinstance(e, JsonEvent)]
    assert types[0] == "synthesis_started"
    assert types[1] == "audio_metadata"
    assert types[-1] == "completed"
    assert session.state is SessionState.COMPLETED
    assert any(isinstance(e, BinaryChunkEvent) for e in events)


async def test_binary_frames_carry_current_revision(analysed_tokens) -> None:
    from audio_metrics.pcm import unpack_chunk_frame

    tokens = analysed_tokens("नमस्ते दुनिया")
    session = make_session()
    events = await collect(session.start(tokens, SynthesisControls(voice_id="v1")))
    for event in events:
        if isinstance(event, BinaryChunkEvent):
            revision_id, _sequence, _pcm = unpack_chunk_frame(event.frame)
            assert revision_id == 1


async def test_revision_increments_on_edit(analysed_tokens) -> None:
    tokens = analysed_tokens("नमस्ते")
    session = make_session()
    await collect(session.start(tokens, SynthesisControls(voice_id="v1")))
    assert session.revision_id == 1
    await collect(session.edit(tokens, SynthesisControls(voice_id="v1")))
    assert session.revision_id == 2


async def test_cancel_stops_stream_gracefully(analysed_tokens) -> None:
    tokens = analysed_tokens("नमस्ते दुनिया कैसे हो आप सब लोग यहाँ पर")
    session = make_session()
    events = []
    gen = session.start(tokens, SynthesisControls(voice_id="v1", chunk_size_ms=50))
    async for event in gen:
        events.append(event)
        if isinstance(event, JsonEvent) and event.type == "chunk_metric":
            session.cancel()
    types = [e.type for e in events if isinstance(e, JsonEvent)]
    assert "cancelled" in types
    assert "completed" not in types
    assert session.state is SessionState.CANCELLED


async def test_buffer_underflow_triggered_once(analysed_tokens) -> None:
    tokens = analysed_tokens("नमस्ते दुनिया कैसे हो आप सब लोग यहाँ पर आज")
    session = make_session(trigger_underflow_once=True)
    events = await collect(
        session.start(tokens, SynthesisControls(voice_id="v1", chunk_size_ms=50))
    )
    warnings = [e for e in events if isinstance(e, JsonEvent) and e.type == "warning"]
    assert len(warnings) == 1
    assert warnings[0].payload["code"] == "SIMULATED_BUFFER_UNDERFLOW"
    underflow_statuses = [
        e
        for e in events
        if isinstance(e, JsonEvent) and e.type == "buffer_status" and e.payload["underflow"]
    ]
    assert len(underflow_statuses) == 1


async def test_pause_blocks_and_resume_continues(analysed_tokens) -> None:
    tokens = analysed_tokens("नमस्ते दुनिया कैसे हो आप सब लोग यहाँ पर आज")
    session = make_session()
    gen = session.start(tokens, SynthesisControls(voice_id="v1", chunk_size_ms=50))
    events = []
    resumed = asyncio.Event()

    async def resume_after_pause() -> None:
        while session.state is not SessionState.PAUSED:
            await asyncio.sleep(0)
        session.resume()
        resumed.set()

    resumer_task = asyncio.create_task(resume_after_pause())
    already_paused = False
    async for event in gen:
        events.append(event)
        if not already_paused and isinstance(event, JsonEvent) and event.type == "chunk_metric":
            session.pause()
            already_paused = True
    await resumer_task
    assert resumed.is_set()
    types = [e.type for e in events if isinstance(e, JsonEvent)]
    assert "completed" in types


async def test_reset_returns_to_idle(analysed_tokens) -> None:
    tokens = analysed_tokens("नमस्ते")
    session = make_session()
    await collect(session.start(tokens, SynthesisControls(voice_id="v1")))
    session.reset()
    assert session.state is SessionState.IDLE
    assert session.revision_id == 0
