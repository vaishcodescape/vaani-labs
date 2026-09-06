"""Static catalog data for /models, /voices, /languages.

Not a provider concern (these lists don't vary by mock vs. real
provider in Phase 1) so they live here rather than behind DI. If voice
catalogs later come from a real TTS provider, move this into a
`VoiceCatalog` provider interface at that point.
"""

from __future__ import annotations

from app.schemas.system import LanguageInfo, ModelInfo, VoiceInfo

VOICES: list[VoiceInfo] = [
    VoiceInfo(id="hi-female-1", language="hi", label="Hindi — Female 1", gender="female"),
    VoiceInfo(id="hi-male-1", language="hi", label="Hindi — Male 1", gender="male"),
    VoiceInfo(id="gu-female-1", language="gu", label="Gujarati — Female 1", gender="female"),
    VoiceInfo(id="mr-female-1", language="mr", label="Marathi — Female 1", gender="female"),
    VoiceInfo(id="en-female-1", language="en", label="English — Female 1", gender="female"),
]

LANGUAGES: list[LanguageInfo] = [
    LanguageInfo(code="hi", name="Hindi", script="Devanagari"),
    LanguageInfo(code="gu", name="Gujarati", script="Gujarati"),
    LanguageInfo(code="mr", name="Marathi", script="Devanagari"),
    LanguageInfo(code="en", name="English", script="Latin"),
]

ACOUSTIC_MODELS: list[ModelInfo] = [
    ModelInfo(id="mock-duration-acoustic", kind="mock", is_default=True),
]

VOCODERS: list[ModelInfo] = [
    ModelInfo(id="mock-sine-mrss-vocos", kind="mock", is_default=True),
]
