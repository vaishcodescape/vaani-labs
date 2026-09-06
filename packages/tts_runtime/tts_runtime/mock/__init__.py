"""Deterministic mock acoustic model and vocoder."""

from __future__ import annotations

from tts_runtime.mock.acoustic import MockAcousticModelAdapter
from tts_runtime.mock.vocoder import MockStreamingVocoderAdapter

__all__ = ["MockAcousticModelAdapter", "MockStreamingVocoderAdapter"]
