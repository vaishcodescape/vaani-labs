from __future__ import annotations

import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
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
from tts_runtime.mock import MockAcousticModelAdapter, MockStreamingVocoderAdapter

from app.deps import ProviderRegistry, override_registry_for_tests, reset_registry_for_tests
from app.main import app
from app.services.session_registry import reset_all_for_tests


@pytest.fixture
def registry() -> Iterator[ProviderRegistry]:
    with tempfile.TemporaryDirectory() as tmp:
        test_registry = ProviderRegistry(
            script_detector=MockScriptDetector(),
            language_identifier=MockLanguageIdentifier(),
            normalizer=MockTextNormalizer(),
            code_switch_detector=MockCodeSwitchDetector(),
            transliterator=MockTransliterator(),
            g2p=MockGraphemeToPhoneme(),
            ranker=MockPronunciationRanker(),
            lexicon=SqliteLexicon(Path(tmp) / "lexicon.db"),
            acoustic_model=MockAcousticModelAdapter(),
            vocoder=MockStreamingVocoderAdapter(),
        )
        override_registry_for_tests(test_registry)
        reset_all_for_tests()
        yield test_registry
        reset_registry_for_tests()
        reset_all_for_tests()


@pytest.fixture
def client(registry: ProviderRegistry) -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
