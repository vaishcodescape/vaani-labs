#!/usr/bin/env python3
"""Export JSON Schemas from the API's Pydantic models into schemas/.

Run via `make schemas` whenever a wire-format Pydantic model changes
(AGENTS.md: "Any wire-format change -> regenerate schemas/"). The
frontend's zod schemas should be kept in sync with these by hand for
now — see docs/architecture.md for why schemas/ exists.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

from app.schemas.common import ErrorResponse  # noqa: E402
from app.schemas.lexicon import (  # noqa: E402
    LexiconCreateRequest,
    LexiconEntrySchema,
    LexiconListResponse,
    LexiconUpdateRequest,
)
from app.schemas.pronunciation import (  # noqa: E402
    PronunciationCandidatesRequest,
    PronunciationCandidatesResponse,
    PronunciationPreviewRequest,
    PronunciationPreviewResponse,
)
from app.schemas.synthesis import OfflineSynthesisRequest, OfflineSynthesisResponse  # noqa: E402
from app.schemas.system import (  # noqa: E402
    HealthResponse,
    LanguagesResponse,
    ModelsResponse,
    SystemResponse,
    VoicesResponse,
)
from app.schemas.text import (  # noqa: E402
    AnalyseTextRequest,
    AnalyseTextResponse,
    NormalizeTextRequest,
    NormalizeTextResponse,
)
from app.schemas.ws import (  # noqa: E402
    CancelEvent,
    EditEvent,
    PauseEvent,
    PingEvent,
    ResetEvent,
    ResumeEvent,
    StartEvent,
)

MODELS = {
    "AnalyseTextRequest": AnalyseTextRequest,
    "AnalyseTextResponse": AnalyseTextResponse,
    "NormalizeTextRequest": NormalizeTextRequest,
    "NormalizeTextResponse": NormalizeTextResponse,
    "PronunciationCandidatesRequest": PronunciationCandidatesRequest,
    "PronunciationCandidatesResponse": PronunciationCandidatesResponse,
    "PronunciationPreviewRequest": PronunciationPreviewRequest,
    "PronunciationPreviewResponse": PronunciationPreviewResponse,
    "LexiconCreateRequest": LexiconCreateRequest,
    "LexiconEntry": LexiconEntrySchema,
    "LexiconListResponse": LexiconListResponse,
    "LexiconUpdateRequest": LexiconUpdateRequest,
    "OfflineSynthesisRequest": OfflineSynthesisRequest,
    "OfflineSynthesisResponse": OfflineSynthesisResponse,
    "HealthResponse": HealthResponse,
    "SystemResponse": SystemResponse,
    "ModelsResponse": ModelsResponse,
    "VoicesResponse": VoicesResponse,
    "LanguagesResponse": LanguagesResponse,
    "ErrorResponse": ErrorResponse,
    "ws.StartEvent": StartEvent,
    "ws.EditEvent": EditEvent,
    "ws.CancelEvent": CancelEvent,
    "ws.PauseEvent": PauseEvent,
    "ws.ResumeEvent": ResumeEvent,
    "ws.ResetEvent": ResetEvent,
    "ws.PingEvent": PingEvent,
}


def main() -> None:
    out_dir = REPO_ROOT / "schemas"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, model in MODELS.items():
        schema = model.model_json_schema()
        out_path = out_dir / f"{name}.schema.json"
        out_path.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"wrote {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
