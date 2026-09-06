from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.schemas.system import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=get_settings().api_version)
