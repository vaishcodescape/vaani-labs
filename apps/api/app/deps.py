"""Dependency-injection wiring for every NLP/TTS provider.

This is the *only* place a concrete mock (or, later, real) provider
class is imported and instantiated. Routers and services depend on the
`indic_text`/`tts_runtime` Protocol types via `Depends(get_registry)`,
never on a concrete class. See docs/model-adapter.md for how Phase 2
swaps a mock for a real provider here.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from indic_text.interfaces import (
    CodeSwitchDetector,
    GraphemeToPhoneme,
    LanguageIdentifier,
    PronunciationLexicon,
    PronunciationRanker,
    ScriptDetector,
    TextNormalizer,
    Transliterator,
)
from indic_text.lexicon_sqlite import SqliteLexicon
from indic_text.mock import (
    MockCodeSwitchDetector,
    MockGraphemeToPhoneme,
    MockLanguageIdentifier,
    MockPronunciationRanker,
    MockScriptDetector,
    MockTextNormalizer,
    MockTransliterator,
)
from tts_runtime.interfaces import AcousticModelAdapter, StreamingVocoderAdapter
from tts_runtime.mock import MockAcousticModelAdapter, MockStreamingVocoderAdapter

from app.config import get_settings


@dataclass(slots=True)
class ProviderRegistry:
    script_detector: ScriptDetector
    language_identifier: LanguageIdentifier
    normalizer: TextNormalizer
    code_switch_detector: CodeSwitchDetector
    transliterator: Transliterator
    g2p: GraphemeToPhoneme
    ranker: PronunciationRanker
    lexicon: PronunciationLexicon
    acoustic_model: AcousticModelAdapter
    vocoder: StreamingVocoderAdapter
    started_at: float = field(default_factory=time.monotonic)

    def provider_ids(self) -> dict[str, str]:
        return {
            "script_detector": getattr(self.script_detector, "provider_id", "unknown"),
            "language_identifier": getattr(self.language_identifier, "provider_id", "unknown"),
            "normalizer": getattr(self.normalizer, "provider_id", "unknown"),
            "code_switch_detector": getattr(self.code_switch_detector, "provider_id", "unknown"),
            "transliterator": getattr(self.transliterator, "provider_id", "unknown"),
            "g2p": getattr(self.g2p, "provider_id", "unknown"),
            "pronunciation_ranker": getattr(self.ranker, "provider_id", "unknown"),
            "lexicon": getattr(self.lexicon, "provider_id", "unknown"),
            "acoustic_model": getattr(self.acoustic_model, "provider_id", "unknown"),
            "vocoder": getattr(self.vocoder, "provider_id", "unknown"),
            "audio_metrics": "in-process-audio-metrics",
        }


def build_provider_registry() -> ProviderRegistry:
    settings = get_settings()
    return ProviderRegistry(
        script_detector=MockScriptDetector(),
        language_identifier=MockLanguageIdentifier(),
        normalizer=MockTextNormalizer(),
        code_switch_detector=MockCodeSwitchDetector(),
        transliterator=MockTransliterator(),
        g2p=MockGraphemeToPhoneme(),
        ranker=MockPronunciationRanker(),
        lexicon=SqliteLexicon(settings.lexicon_db_path),
        acoustic_model=MockAcousticModelAdapter(),
        vocoder=MockStreamingVocoderAdapter(),
    )


_registry: ProviderRegistry | None = None


def get_registry() -> ProviderRegistry:
    """FastAPI dependency: returns the process-wide provider registry singleton."""
    global _registry
    if _registry is None:
        _registry = build_provider_registry()
    return _registry


def override_registry_for_tests(registry: ProviderRegistry) -> None:
    global _registry
    _registry = registry


def reset_registry_for_tests() -> None:
    global _registry
    _registry = None
