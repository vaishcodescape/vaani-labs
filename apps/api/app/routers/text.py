from __future__ import annotations

from fastapi import APIRouter, Depends
from indic_text.tokenizer import tokenize

from app.deps import ProviderRegistry, get_registry
from app.schemas.text import (
    AnalyseTextRequest,
    AnalyseTextResponse,
    NormalizeTextRequest,
    NormalizeTextResponse,
)
from app.services.analysis_service import analyse, to_response
from app.validation import validate_analysable_text

router = APIRouter(prefix="/api/v1/text", tags=["text"])


@router.post("/analyse", response_model=AnalyseTextResponse)
def analyse_text_endpoint(
    body: AnalyseTextRequest, registry: ProviderRegistry = Depends(get_registry)
) -> AnalyseTextResponse:
    text = validate_analysable_text(body.text)
    result = analyse(text, registry)
    return to_response(result)


@router.post("/normalize", response_model=NormalizeTextResponse)
def normalize_text_endpoint(
    body: NormalizeTextRequest, registry: ProviderRegistry = Depends(get_registry)
) -> NormalizeTextResponse:
    text = validate_analysable_text(body.text)
    tokens = tokenize(text)
    if not tokens:
        return NormalizeTextResponse(text=text, normalized=text, token_type="word")
    first = tokens[0]
    normalized = registry.normalizer.normalize(first.surface, first.token_type)
    return NormalizeTextResponse(text=text, normalized=normalized, token_type=first.token_type.value)
