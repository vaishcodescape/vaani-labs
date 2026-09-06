from __future__ import annotations

from indic_text.mock.code_switch_detector import MockCodeSwitchDetector
from indic_text.models import AnalysedToken, PronunciationSource, TokenPronunciation, TokenType


def _word(index: int, surface: str, language: str, start: int, end: int) -> AnalysedToken:
    return AnalysedToken(
        index=index,
        surface=surface,
        start_offset=start,
        end_offset=end,
        script="Devanagari",
        language=language,
        normalized=surface,
        token_type=TokenType.WORD,
        codepoints=(),
        pronunciation=TokenPronunciation("", 1.0, False, PronunciationSource.G2P),
    )


def test_no_switch_when_single_language() -> None:
    tokens = [_word(0, "मुझे", "hi", 0, 4), _word(1, "कल", "hi", 5, 7)]
    assert MockCodeSwitchDetector().detect(tokens) == []


def test_detects_single_token_switch() -> None:
    tokens = [
        _word(0, "मुझे", "hi", 0, 4),
        _word(1, "meeting", "en", 5, 12),
        _word(2, "है", "hi", 13, 15),
    ]
    spans = MockCodeSwitchDetector().detect(tokens)
    assert len(spans) == 1
    assert spans[0].language == "en"
    assert spans[0].start_offset == 5
    assert spans[0].end_offset == 12


def test_empty_tokens() -> None:
    assert MockCodeSwitchDetector().detect([]) == []
