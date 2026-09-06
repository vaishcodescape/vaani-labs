from __future__ import annotations

from itertools import pairwise

from indic_text.models import TokenType
from indic_text.tokenizer import tokenize


def test_empty_input_returns_no_tokens() -> None:
    assert tokenize("") == []


def test_tokens_cover_text_contiguously() -> None:
    text = "मुझे कल 5 बजे meeting है।"
    tokens = tokenize(text)
    assert tokens[0].start_offset == 0
    assert tokens[-1].end_offset == len(text)
    for a, b in pairwise(tokens):
        assert a.end_offset == b.start_offset
    assert "".join(t.surface for t in tokens) == text


def test_number_token_type() -> None:
    tokens = tokenize("5 बजे")
    assert tokens[0].token_type is TokenType.NUMBER
    assert tokens[0].surface == "5"


def test_date_token_type() -> None:
    tokens = tokenize("06/09/2026")
    assert len(tokens) == 1
    assert tokens[0].token_type is TokenType.DATE


def test_abbreviation_token_type() -> None:
    tokens = tokenize("e.g. Dr.")
    types = [t.token_type for t in tokens if t.token_type is not TokenType.WHITESPACE]
    assert TokenType.ABBREVIATION in types


def test_very_long_input_does_not_crash() -> None:
    text = "नमस्ते संसार " * 5000
    tokens = tokenize(text)
    assert len(tokens) > 0
    assert "".join(t.surface for t in tokens) == text


def test_punctuation_and_whitespace_split_out() -> None:
    tokens = tokenize("hai।")
    kinds = [t.token_type for t in tokens]
    assert TokenType.WORD in kinds
    assert TokenType.PUNCTUATION in kinds
