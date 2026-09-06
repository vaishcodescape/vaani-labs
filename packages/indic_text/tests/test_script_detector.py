from __future__ import annotations

from indic_text.mock.script_detector import MockScriptDetector


def test_empty_text() -> None:
    assert MockScriptDetector().detect("") == []


def test_pure_devanagari() -> None:
    spans = MockScriptDetector().detect("नमस्ते")
    assert len(spans) == 1
    assert spans[0].script == "Devanagari"


def test_pure_gujarati() -> None:
    spans = MockScriptDetector().detect("નમસ્તે")
    assert len(spans) == 1
    assert spans[0].script == "Gujarati"


def test_mixed_devanagari_and_latin() -> None:
    text = "मुझे meeting है"
    spans = MockScriptDetector().detect(text)
    scripts = [s.script for s in spans]
    assert "Devanagari" in scripts
    assert "Latin" in scripts
    # Spans reconstruct the original text exactly.
    assert "".join(text[s.start_offset : s.end_offset] for s in spans) == text


def test_mixed_gujarati_and_latin() -> None:
    text = "હું office જાઉં છું"
    spans = MockScriptDetector().detect(text)
    scripts = {s.script for s in spans}
    assert "Gujarati" in scripts
    assert "Latin" in scripts
