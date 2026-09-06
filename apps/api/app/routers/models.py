from __future__ import annotations

from fastapi import APIRouter

from app.schemas.system import ModelsResponse
from app.static_data import ACOUSTIC_MODELS, VOCODERS

router = APIRouter(prefix="/api/v1", tags=["catalog"])


@router.get("/models", response_model=ModelsResponse)
def list_models() -> ModelsResponse:
    return ModelsResponse(acoustic_models=ACOUSTIC_MODELS, vocoders=VOCODERS)
