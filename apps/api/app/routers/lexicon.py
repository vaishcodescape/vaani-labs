from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from indic_text.lexicon_sqlite import LexiconConflictError
from indic_text.models import LexiconEntry

from app.deps import ProviderRegistry, get_registry
from app.errors import ConflictError, NotFoundError
from app.schemas.lexicon import (
    LexiconCreateRequest,
    LexiconEntrySchema,
    LexiconListResponse,
    LexiconUpdateRequest,
)

router = APIRouter(prefix="/api/v1/lexicon", tags=["lexicon"])


def _to_schema(entry: LexiconEntry) -> LexiconEntrySchema:
    return LexiconEntrySchema(
        id=entry.id,
        surface=entry.surface,
        language=entry.language,
        phonemes=entry.phonemes,
        notes=entry.notes,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


@router.get("", response_model=LexiconListResponse)
def list_entries(
    q: str | None = None,
    language: str | None = None,
    registry: ProviderRegistry = Depends(get_registry),
) -> LexiconListResponse:
    entries = registry.lexicon.list(query=q, language=language)
    return LexiconListResponse(entries=[_to_schema(e) for e in entries])


@router.post("", response_model=LexiconEntrySchema, status_code=201)
def create_entry(
    body: LexiconCreateRequest, registry: ProviderRegistry = Depends(get_registry)
) -> LexiconEntrySchema:
    try:
        entry = registry.lexicon.create(body.surface, body.language, body.phonemes, body.notes)
    except LexiconConflictError as exc:
        raise ConflictError(str(exc)) from exc
    return _to_schema(entry)


@router.patch("/{entry_id}", response_model=LexiconEntrySchema)
def update_entry(
    entry_id: str,
    body: LexiconUpdateRequest,
    registry: ProviderRegistry = Depends(get_registry),
) -> LexiconEntrySchema:
    entry = registry.lexicon.update(entry_id, phonemes=body.phonemes, notes=body.notes)
    if entry is None:
        raise NotFoundError(f"lexicon entry {entry_id!r} not found")
    return _to_schema(entry)


@router.delete("/{entry_id}", status_code=204, response_class=Response)
def delete_entry(entry_id: str, registry: ProviderRegistry = Depends(get_registry)) -> Response:
    if not registry.lexicon.delete(entry_id):
        raise NotFoundError(f"lexicon entry {entry_id!r} not found")
    return Response(status_code=204)
