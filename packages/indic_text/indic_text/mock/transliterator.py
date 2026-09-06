"""Naive character-map transliterator between Devanagari and Latin.

This is intentionally not linguistically precise (no context-sensitive
schwa deletion, no conjunct handling) — it exists to exercise the
Transliterator interface end-to-end and to support romanized-Indic
lexicon lookups in the mock pipeline. See docs/model-adapter.md for
what a real transliterator needs to preserve.
"""

from __future__ import annotations

_DEVANAGARI_TO_LATIN: dict[str, str] = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ii", "उ": "u", "ऊ": "uu",
    "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au",
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ng",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "ny",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
    "ं": "n", "ँ": "n", "ः": "h", "़": "", "्": "",
    "ा": "a", "ि": "i", "ी": "ii", "ु": "u", "ू": "uu",
    "े": "e", "ै": "ai", "ो": "o", "ौ": "au",
    "।": ".", "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
}

_LATIN_TO_DEVANAGARI: dict[str, str] = {v: k for k, v in _DEVANAGARI_TO_LATIN.items() if v}
# Prefer single-character Devanagari vowel signs over independent vowels
# when reversing multi-key collisions (e.g. "a" -> "ा" is more common
# mid-word than "अ"); independent-vowel forms remain reachable via the
# forward map and are only used for word-initial transliteration by
# real implementations.


class MockTransliterator:
    provider_id = "mock-charmap-transliterator"

    def transliterate(self, text: str, source_script: str, target_script: str) -> str:
        if source_script == target_script:
            return text
        if source_script == "Devanagari" and target_script == "Latin":
            return "".join(_DEVANAGARI_TO_LATIN.get(ch, ch) for ch in text)
        if source_script == "Latin" and target_script == "Devanagari":
            out: list[str] = []
            i = 0
            lowered = text.lower()
            # Greedy longest-match over 1-3 char Latin chunks against the
            # reverse table, longest first, so multi-letter digraphs like
            # "kh"/"chh"/"aa" win over their single-letter prefixes.
            keys_by_length = sorted(_LATIN_TO_DEVANAGARI.keys(), key=len, reverse=True)
            while i < len(lowered):
                matched = False
                for key in keys_by_length:
                    if lowered.startswith(key, i):
                        out.append(_LATIN_TO_DEVANAGARI[key])
                        i += len(key)
                        matched = True
                        break
                if not matched:
                    out.append(text[i])
                    i += 1
            return "".join(out)
        return text
