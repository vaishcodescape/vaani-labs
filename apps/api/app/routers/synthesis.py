from __future__ import annotations

import base64
import time

from audio_metrics.pcm import pcm_duration_ms
from fastapi import APIRouter, Depends
from tts_runtime.interfaces import SynthesisControls

from app.deps import ProviderRegistry, get_registry
from app.schemas.synthesis import OfflineSynthesisRequest, OfflineSynthesisResponse
from app.services.analysis_service import analyse
from app.validation import validate_analysable_text

router = APIRouter(prefix="/api/v1/synthesis", tags=["synthesis"])

_OFFLINE_CHUNK_SIZE_MS = 60 * 60 * 1000
"""One giant "chunk" — offline synthesis returns the whole utterance in one response."""


@router.post("/offline", response_model=OfflineSynthesisResponse)
def synthesize_offline(
    body: OfflineSynthesisRequest, registry: ProviderRegistry = Depends(get_registry)
) -> OfflineSynthesisResponse:
    text = validate_analysable_text(body.text)
    result = analyse(text, registry)
    controls = SynthesisControls(
        voice_id=body.voice_id,
        speed=body.speed,
        pitch=body.pitch,
        energy=body.energy,
        chunk_size_ms=_OFFLINE_CHUNK_SIZE_MS,
    )

    wall_clock_start = time.monotonic()
    plan = registry.acoustic_model.plan(result.tokens, controls)
    pcm = b"".join(chunk.pcm for chunk in registry.vocoder.stream(plan))
    elapsed_ms = (time.monotonic() - wall_clock_start) * 1000 + plan.planning_ms

    duration_ms = pcm_duration_ms(pcm, plan.sample_rate)
    rtf = (elapsed_ms / duration_ms) if duration_ms else 0.0

    return OfflineSynthesisResponse(
        sample_rate=plan.sample_rate,
        channels=1,
        bit_depth=16,
        duration_ms=duration_ms,
        rtf=rtf,
        pcm_base64=base64.b64encode(pcm).decode("ascii"),
    )
