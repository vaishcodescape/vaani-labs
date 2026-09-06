"""Deterministic mock implementations of every indic_text provider interface."""

from __future__ import annotations

from indic_text.mock.code_switch_detector import MockCodeSwitchDetector
from indic_text.mock.g2p import MockGraphemeToPhoneme
from indic_text.mock.language_identifier import MockLanguageIdentifier
from indic_text.mock.normalizer import MockTextNormalizer
from indic_text.mock.ranker import MockPronunciationRanker
from indic_text.mock.script_detector import MockScriptDetector
from indic_text.mock.transliterator import MockTransliterator

__all__ = [
    "MockCodeSwitchDetector",
    "MockGraphemeToPhoneme",
    "MockLanguageIdentifier",
    "MockPronunciationRanker",
    "MockScriptDetector",
    "MockTextNormalizer",
    "MockTransliterator",
]
