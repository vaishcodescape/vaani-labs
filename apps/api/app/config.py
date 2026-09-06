"""Application settings, loaded from environment / .env.

Only infrastructure knobs live here (paths, CORS). Provider *selection*
(mock vs. real) is intentionally not yet configurable — Phase 1 always
uses mock providers; see docs/model-adapter.md for how Phase 2 should
extend this file with provider-selection env vars.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="VAANILAB_", extra="ignore")

    api_version: str = "0.1.0"
    lexicon_db_path: Path = _REPO_ROOT / "data" / "lexicons" / "lexicon.db"
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
