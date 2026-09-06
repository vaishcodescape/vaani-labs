"""Deterministic rule-based grapheme-to-phoneme mock.

Native-script (Devanagari/Gujarati) tokens get a per-character IPA-ish
mapping with high, coverage-derived confidence. Latin-script tokens
(English or romanized Indic) use a much rougher letter->phone table with
lower confidence, reflecting genuine real-world G2P ambiguity for
code-switched Latin text. All "randomness" (confidence jitter, alt
candidates) is derived from a SHA-256 digest of the surface form so the
same word always produces the same output, independent of process,
run, or PYTHONHASHSEED.
"""

from __future__ import annotations

import hashlib

from indic_text.models import PronunciationCandidate, PronunciationSource

_DEVANAGARI_PHONEMES: dict[str, str] = {
    "अ": "ə", "आ": "aː", "इ": "ɪ", "ई": "iː", "उ": "ʊ", "ऊ": "uː",
    "ए": "eː", "ऐ": "ɛː", "ओ": "oː", "औ": "ɔː",
    "क": "k", "ख": "kʰ", "ग": "g", "घ": "gʱ", "ङ": "ŋ",
    "च": "tʃ", "छ": "tʃʰ", "ज": "dʒ", "झ": "dʒʱ", "ञ": "ɲ",
    "ट": "ʈ", "ठ": "ʈʰ", "ड": "ɖ", "ढ": "ɖʱ", "ण": "ɳ",
    "त": "t̪", "थ": "t̪ʰ", "द": "d̪", "ध": "d̪ʱ", "न": "n",
    "प": "p", "फ": "pʰ", "ब": "b", "भ": "bʱ", "म": "m",
    "य": "j", "र": "r", "ल": "l", "व": "ʋ",
    "श": "ʃ", "ष": "ʂ", "स": "s", "ह": "ɦ",
    "ा": "aː", "ि": "ɪ", "ी": "iː", "ु": "ʊ", "ू": "uː",
    "े": "eː", "ै": "ɛː", "ो": "oː", "ौ": "ɔː",
    "ं": "ŋ", "ँ": "̃", "ः": "h", "्": "",
}

_GUJARATI_OFFSET = 0x0A80 - 0x0900
_LATIN_PHONEMES: dict[str, str] = {
    "a": "æ", "b": "b", "c": "k", "d": "d", "e": "ɛ", "f": "f", "g": "g",
    "h": "h", "i": "ɪ", "j": "dʒ", "k": "k", "l": "l", "m": "m", "n": "n",
    "o": "ɒ", "p": "p", "q": "k", "r": "r", "s": "s", "t": "t", "u": "ʌ",
    "v": "v", "w": "w", "x": "ks", "y": "j", "z": "z",
}
_LATIN_DIGRAPHS: dict[str, str] = {
    "sh": "ʃ", "ch": "tʃ", "th": "θ", "ph": "f", "ee": "iː", "oo": "uː",
    "ng": "ŋ", "ck": "k", "ai": "eɪ", "ea": "iː",
}


def _digest_int(surface: str, salt: str) -> int:
    h = hashlib.sha256(f"{salt}:{surface}".encode()).hexdigest()
    return int(h[:8], 16)


def _devanagari_or_gujarati_phonemes(surface: str, script: str) -> tuple[str, float]:
    phones: list[str] = []
    known = 0
    total = 0
    for ch in surface:
        total += 1
        lookup_ch = ch
        if script == "Gujarati":
            # Gujarati is a near-linear Unicode shift of Devanagari for the
            # letters this mock table covers; shift back before lookup.
            shifted = chr(ord(ch) - _GUJARATI_OFFSET) if ord(ch) >= 0x0A80 else ch
            lookup_ch = shifted
        phone = _DEVANAGARI_PHONEMES.get(lookup_ch)
        if phone is not None:
            known += 1
            if phone:
                phones.append(phone)
        elif not ch.isspace():
            phones.append(ch)
    coverage = known / total if total else 0.0
    confidence = 0.75 + 0.24 * coverage
    return " ".join(phones), min(confidence, 0.99)


def _latin_phonemes(surface: str) -> tuple[str, float]:
    lowered = surface.lower()
    phones: list[str] = []
    known = 0
    total_units = 0
    i = 0
    while i < len(lowered):
        digraph = lowered[i : i + 2]
        if digraph in _LATIN_DIGRAPHS:
            phones.append(_LATIN_DIGRAPHS[digraph])
            known += 1
            total_units += 1
            i += 2
            continue
        ch = lowered[i]
        total_units += 1
        phone = _LATIN_PHONEMES.get(ch)
        if phone is not None:
            known += 1
            phones.append(phone)
        elif not ch.isspace():
            phones.append(ch)
        i += 1
    coverage = known / total_units if total_units else 0.0
    jitter = (_digest_int(surface, "latin-conf") % 21) / 100.0  # 0.00-0.20
    confidence = 0.35 + 0.35 * coverage + jitter
    return " ".join(phones), min(confidence, 0.93)


def _alt_candidate(phonemes: str, surface: str) -> str:
    symbols = phonemes.split(" ")
    if not symbols:
        return phonemes
    idx = _digest_int(surface, "alt-swap") % len(symbols)
    swap_table = {
        "ə": "a", "ɪ": "i", "ʊ": "u", "eː": "e", "oː": "o",
        "æ": "a", "ɛ": "e", "ɒ": "o", "ʌ": "u", "ʃ": "s", "tʃ": "ch",
    }
    symbols[idx] = swap_table.get(symbols[idx], symbols[idx] + "̆")
    return " ".join(symbols)


class MockGraphemeToPhoneme:
    provider_id = "mock-rule-g2p"

    def to_phonemes(
        self, surface: str, language: str, script: str
    ) -> list[PronunciationCandidate]:
        if script in ("Devanagari", "Gujarati"):
            phonemes, confidence = _devanagari_or_gujarati_phonemes(surface, script)
        else:
            phonemes, confidence = _latin_phonemes(surface)

        candidates = [
            PronunciationCandidate(
                phonemes=phonemes, confidence=confidence, source=PronunciationSource.G2P
            )
        ]

        num_alts = 1 + (_digest_int(surface, "num-alts") % 2)  # 1 or 2 extra candidates
        alt_confidence = confidence
        alt_phonemes = phonemes
        for n in range(num_alts):
            alt_phonemes = _alt_candidate(alt_phonemes, surface + str(n))
            alt_confidence = max(alt_confidence * 0.55, 0.05)
            candidates.append(
                PronunciationCandidate(
                    phonemes=alt_phonemes,
                    confidence=alt_confidence,
                    source=PronunciationSource.G2P_ALT,
                )
            )
        return candidates
