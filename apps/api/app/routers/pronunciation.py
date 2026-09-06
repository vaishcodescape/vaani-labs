from __future__ import annotations

import base64

from fastapi import APIRouter, Depends
from indic_text.models import AnalysedToken, PronunciationSource, TokenPronunciation, TokenType
from tts_runtime.interfaces import SynthesisControls

from app.deps import ProviderRegistry, get_registry
from app.schemas.pronunciation import (
    PronunciationCandidateSchema,
    PronunciationCandidatesRequest,
    PronunciationCandidatesResponse,
    PronunciationPreviewRequest,
    PronunciationPreviewResponse,
)
from app.validation import validate_analysable_text

router = APIRouter(prefix="/api/v1/pronunciation", tags=["pronunciation"])


@router.post("/candidates", response_model=PronunciationCandidatesResponse)
def get_candidates(
    body: PronunciationCandidatesRequest, registry: ProviderRegistry = Depends(get_registry)
) -> PronunciationCandidatesResponse:
    surface = validate_analysable_text(body.surface)
    candidates = registry.ranker.rank(registry.g2p.to_phonemes(surface, body.language, body.script))
    return PronunciationCandidatesResponse(
        surface=surface,
        candidates=[
            PronunciationCandidateSchema(
                phonemes=c.phonemes, confidence=c.confidence, source=c.source.value
            )
            for c in candidates
        ],
    )


@router.post("/preview", response_model=PronunciationPreviewResponse)
def preview_pronunciation(
    body: PronunciationPreviewRequest, registry: ProviderRegistry = Depends(get_registry)
) -> PronunciationPreviewResponse:
    surface = validate_analysable_text(body.surface)
    token = AnalysedToken(
        index=0,
        surface=surface,
        start_offset=0,
        end_offset=len(surface),
        script="Latin",
        language="en",
        normalized=surface,
        token_type=TokenType.WORD,
        codepoints=(),
        pronunciation=TokenPronunciation(
            phonemes=body.phonemes,
            confidence=1.0,
            is_uncertain=False,
            source=PronunciationSource.G2P,
        ),
    )
    controls = SynthesisControls(voice_id=body.voice_id, chunk_size_ms=10_000)
    plan = registry.acoustic_model.plan([token], controls)
    pcm = b"".join(chunk.pcm for chunk in registry.vocoder.stream(plan))
    return PronunciationPreviewResponse(
        sample_rate=plan.sample_rate,
        channels=1,
        bit_depth=16,
        pcm_base64=base64.b64encode(pcm).decode("ascii"),
    )
