from __future__ import annotations

import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

from indic_text.lexicon_sqlite import SqliteLexicon
from indic_text.mock import (
    MockCodeSwitchDetector,
    MockGraphemeToPhoneme,
    MockLanguageIdentifier,
    MockPronunciationRanker,
    MockScriptDetector,
    MockTextNormalizer,
)


@pytest.fixture
def script_detector() -> MockScriptDetector:
    return MockScriptDetector()


@pytest.fixture
def language_identifier() -> MockLanguageIdentifier:
    return MockLanguageIdentifier()


@pytest.fixture
def normalizer() -> MockTextNormalizer:
    return MockTextNormalizer()


@pytest.fixture
def g2p() -> MockGraphemeToPhoneme:
    return MockGraphemeToPhoneme()


@pytest.fixture
def ranker() -> MockPronunciationRanker:
    return MockPronunciationRanker()


@pytest.fixture
def code_switch_detector() -> MockCodeSwitchDetector:
    return MockCodeSwitchDetector()


@pytest.fixture
def lexicon() -> Iterator[SqliteLexicon]:
    with tempfile.TemporaryDirectory() as tmp:
        lex = SqliteLexicon(Path(tmp) / "lexicon.db")
        yield lex
        lex.close()
