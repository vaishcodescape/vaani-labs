from __future__ import annotations

from fastapi import APIRouter

from app.schemas.system import VoicesResponse
from app.static_data import VOICES

router = APIRouter(prefix="/api/v1", tags=["catalog"])


@router.get("/voices", response_model=VoicesResponse)
def list_voices() -> VoicesResponse:
    return VoicesResponse(voices=VOICES)
