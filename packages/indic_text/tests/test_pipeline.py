from __future__ import annotations

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
from indic_text.models import TokenType
from indic_text.pipeline import analyse_text


@pytest.fixture
def providers(lexicon: SqliteLexicon) -> dict:
    return {
        "script_detector": MockScriptDetector(),
        "language_identifier": MockLanguageIdentifier(),
        "normalizer": MockTextNormalizer(),
        "g2p": MockGraphemeToPhoneme(),
        "ranker": MockPronunciationRanker(),
        "lexicon": lexicon,
        "code_switch_detector": MockCodeSwitchDetector(),
    }


def test_empty_input(providers: dict) -> None:
    result = analyse_text("", **providers)
    assert result.tokens == []
    assert result.code_switch_spans == []


def test_mixed_devanagari_and_latin(providers: dict) -> None:
    result = analyse_text("मुझे कल 5 बजे meeting है।", **providers)
    languages = {t.language for t in result.tokens if t.token_type is TokenType.WORD}
    assert "hi" in languages
    assert "en" in languages
    meeting = next(t for t in result.tokens if t.surface == "meeting")
    assert meeting.pronunciation.source.value in {"g2p", "g2p-alt"}


def test_mixed_gujarati_and_latin(providers: dict) -> None:
    result = analyse_text("હું office જાઉં છું", **providers)
    languages = {t.language for t in result.tokens if t.token_type is TokenType.WORD}
    assert "gu" in languages
    assert "en" in languages


def test_marathi_text(providers: dict) -> None:
    result = analyse_text("मी मराठी आहे", **providers)
    assert all(
        t.language == "mr" for t in result.tokens if t.token_type is TokenType.WORD
    )


def test_numbers_are_normalized(providers: dict) -> None:
    result = analyse_text("5 बजे", **providers)
    number_token = result.tokens[0]
    assert number_token.token_type is TokenType.NUMBER
    assert number_token.normalized == "पाँच"


def test_dates_are_normalized(providers: dict) -> None:
    result = analyse_text("06/09/2026", **providers)
    assert result.tokens[0].token_type is TokenType.DATE
    assert "सितंबर" in result.tokens[0].normalized


def test_abbreviations_are_normalized(providers: dict) -> None:
    result = analyse_text("Dr. Sharma", **providers)
    abbrev = result.tokens[0]
    assert abbrev.token_type is TokenType.ABBREVIATION
    assert abbrev.normalized == "डॉक्टर"


def test_very_long_input(providers: dict) -> None:
    result = analyse_text("नमस्ते संसार " * 500, **providers)
    assert len(result.tokens) > 0


def test_lexicon_override_takes_precedence(providers: dict) -> None:
    providers["lexicon"].create("meeting", "en", "MY CUSTOM PHONEMES", "")
    result = analyse_text("meeting", **providers)
    token = result.tokens[0]
    assert token.pronunciation.phonemes == "MY CUSTOM PHONEMES"
    assert token.pronunciation.source.value == "lexicon"
    assert token.pronunciation.is_uncertain is False


def test_uncertain_flag_set_for_low_confidence(providers: dict) -> None:
    result = analyse_text("meeting", **providers)
    token = result.tokens[0]
    assert token.pronunciation.confidence < 1.0
    assert token.pronunciation.is_uncertain == (token.pronunciation.confidence < 0.7)


def test_offsets_reconstruct_original_text(providers: dict) -> None:
    text = "मुझे कल 5 बजे meeting है।"
    result = analyse_text(text, **providers)
    assert "".join(text[t.start_offset : t.end_offset] for t in result.tokens) == text
