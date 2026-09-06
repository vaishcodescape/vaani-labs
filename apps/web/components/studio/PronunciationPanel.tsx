"use client";

import { useState } from "react";

import { api } from "@/lib/api/client";
import { usePronunciationCandidates } from "@/lib/hooks/usePronunciationCandidates";
import { useSessionStore } from "@/lib/store/sessionStore";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { PhonemeEditor } from "@/components/studio/PhonemeEditor";

export function PronunciationPanel() {
  const selectedTokenIndex = useSessionStore((state) => state.selectedTokenIndex);
  const token = useSessionStore((state) =>
    state.selectedTokenIndex === null ? null : state.tokens[state.selectedTokenIndex] ?? null,
  );
  const updateTokenPronunciation = useSessionStore((state) => state.updateTokenPronunciation);
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  const { candidates, loading } = usePronunciationCandidates(
    token?.surface ?? null,
    token?.language ?? null,
    token?.script ?? null,
  );

  if (selectedTokenIndex === null || !token) {
    return (
      <p className="text-sm text-slate-400">
        Select a token above to compare and correct its pronunciation.
      </p>
    );
  }

  const saveToLexicon = async () => {
    setSavedMessage(null);
    try {
      await api.createLexiconEntry({
        surface: token.surface,
        language: token.language,
        phonemes: token.pronunciation.phonemes,
        notes: "",
      });
      setSavedMessage("Saved to lexicon.");
    } catch {
      setSavedMessage("Could not save (see Pronunciation Lexicon tab for details).");
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div>
        <div className="flex items-center gap-2">
          <span className="text-lg font-medium">{token.surface}</span>
          <Badge tone="info">{token.script}</Badge>
          <Badge tone="neutral">{token.language}</Badge>
          {token.pronunciation.is_uncertain && <Badge tone="warning">uncertain</Badge>}
        </div>
        <p className="mt-1 text-xs text-slate-500">Normalized: {token.normalized}</p>
      </div>

      <div>
        <h3 className="mb-1 text-xs font-medium text-slate-600">Candidates</h3>
        {loading && <p className="text-xs text-slate-400">Loading candidates…</p>}
        <ul className="flex flex-col gap-1.5">
          {candidates.map((candidate) => {
            const active = candidate.phonemes === token.pronunciation.phonemes;
            return (
              <li key={candidate.phonemes}>
                <button
                  onClick={() =>
                    updateTokenPronunciation(
                      selectedTokenIndex,
                      candidate.phonemes,
                      candidate.confidence,
                      candidate.source,
                    )
                  }
                  className={`focus-ring flex w-full items-center justify-between rounded-md border px-2.5 py-1.5 text-left text-sm ${
                    active ? "border-sky-400 bg-sky-50" : "border-slate-200 hover:bg-slate-50"
                  }`}
                >
                  <span className="font-mono">{candidate.phonemes || "∅"}</span>
                  <span className="flex items-center gap-2 text-xs text-slate-500">
                    {candidate.source}
                    <span className="tabular-nums">{(candidate.confidence * 100).toFixed(0)}%</span>
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>

      <PhonemeEditor
        tokenIndex={selectedTokenIndex}
        surface={token.surface}
        phonemes={token.pronunciation.phonemes}
      />

      <div className="flex items-center gap-2 border-t border-slate-100 pt-3">
        <Button variant="secondary" onClick={() => void saveToLexicon()}>
          Save to Lexicon
        </Button>
        {savedMessage && <span className="text-xs text-slate-500">{savedMessage}</span>}
      </div>
    </div>
  );
}
