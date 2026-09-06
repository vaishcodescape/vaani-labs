"""Deterministic code-switch span detector.

Operates on already-LID'd word tokens: the "matrix" language is the most
common language among word tokens, and any contiguous run of word
tokens (allowing intervening punctuation/whitespace) in a different,
determined language is reported as a code-switch span.
"""

from __future__ import annotations

from collections import Counter

from indic_text.models import AnalysedToken, CodeSwitchSpan, TokenType


class MockCodeSwitchDetector:
    provider_id = "mock-heuristic-csd"

    def detect(self, tokens: list[AnalysedToken]) -> list[CodeSwitchSpan]:
        word_tokens = [t for t in tokens if t.token_type is TokenType.WORD]
        if not word_tokens:
            return []
        counts = Counter(t.language for t in word_tokens if t.language != "und")
        if not counts:
            return []
        matrix_language = counts.most_common(1)[0][0]

        spans: list[CodeSwitchSpan] = []
        run_start: int | None = None
        run_end: int | None = None
        run_language: str | None = None

        def flush() -> None:
            if run_start is not None and run_end is not None and run_language is not None:
                spans.append(CodeSwitchSpan(run_start, run_end, run_language))

        for token in word_tokens:
            if token.language != "und" and token.language != matrix_language:
                if run_language == token.language:
                    run_end = token.end_offset
                else:
                    flush()
                    run_start = token.start_offset
                    run_end = token.end_offset
                    run_language = token.language
            else:
                flush()
                run_start = run_end = run_language = None
        flush()
        return spans
