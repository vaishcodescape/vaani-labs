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
from indic_text.models import AnalysedToken
from indic_text.pipeline import analyse_text


@pytest.fixture
def lexicon() -> Iterator[SqliteLexicon]:
    with tempfile.TemporaryDirectory() as tmp:
        lex = SqliteLexicon(Path(tmp) / "lexicon.db")
        yield lex
        lex.close()


@pytest.fixture
def analysed_tokens(lexicon: SqliteLexicon):
    def _analyse(text: str) -> list[AnalysedToken]:
        result = analyse_text(
            text,
            script_detector=MockScriptDetector(),
            language_identifier=MockLanguageIdentifier(),
            normalizer=MockTextNormalizer(),
            g2p=MockGraphemeToPhoneme(),
            ranker=MockPronunciationRanker(),
            lexicon=lexicon,
            code_switch_detector=MockCodeSwitchDetector(),
        )
        return result.tokens

    return _analyse
