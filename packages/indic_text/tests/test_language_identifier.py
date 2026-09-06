from __future__ import annotations

from indic_text.mock.language_identifier import MockLanguageIdentifier
from indic_text.mock.script_detector import MockScriptDetector


def _identify(text: str) -> list[str]:
    scripts = MockScriptDetector().detect(text)
    spans = MockLanguageIdentifier().identify(text, scripts)
    return [s.language for s in spans]


def test_devanagari_defaults_to_hindi() -> None:
    assert _identify("नमस्ते")[0] == "hi"


def test_devanagari_marathi_marker() -> None:
    assert _identify("मी मराठी आहे")[0] == "mr"


def test_gujarati_is_always_gujarati() -> None:
    assert _identify("નમસ્તે")[0] == "gu"


def test_latin_defaults_to_english() -> None:
    assert _identify("hello world")[0] == "en"


def test_romanized_hindi_marker() -> None:
    assert _identify("mujhe kal jana hai")[0] == "hi"


def test_romanized_marathi_marker() -> None:
    assert _identify("mala marathi yete")[0] == "mr"
