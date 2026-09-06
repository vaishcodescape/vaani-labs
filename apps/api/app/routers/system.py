from __future__ import annotations

import time

from fastapi import APIRouter, Depends

from app.config import get_settings
from app.deps import ProviderRegistry, get_registry
from app.schemas.system import SystemResponse
from app.services.session_registry import count_active_sessions

router = APIRouter(prefix="/api/v1", tags=["system"])


@router.get("/system", response_model=SystemResponse)
def system_status(registry: ProviderRegistry = Depends(get_registry)) -> SystemResponse:
    return SystemResponse(
        status="ok",
        version=get_settings().api_version,
        uptime_seconds=time.monotonic() - registry.started_at,
        providers=registry.provider_ids(),
        active_sessions=count_active_sessions(),
        lexicon_entry_count=len(registry.lexicon.list()),
    )
