from __future__ import annotations

from fastapi import APIRouter

from app.schemas.system import LanguagesResponse
from app.static_data import LANGUAGES

router = APIRouter(prefix="/api/v1", tags=["catalog"])


@router.get("/languages", response_model=LanguagesResponse)
def list_languages() -> LanguagesResponse:
    return LanguagesResponse(languages=LANGUAGES)
