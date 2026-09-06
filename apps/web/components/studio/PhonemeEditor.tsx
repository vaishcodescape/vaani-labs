"use client";

import { useState } from "react";

import { api } from "@/lib/api/client";
import { playPcmOnce } from "@/lib/audio/playPcmOnce";
import { useSessionStore } from "@/lib/store/sessionStore";
import { Button } from "@/components/ui/Button";

interface PhonemeEditorProps {
  tokenIndex: number;
  surface: string;
  phonemes: string;
}

export function PhonemeEditor({ tokenIndex, surface, phonemes }: PhonemeEditorProps) {
  const [draft, setDraft] = useState(phonemes);
  const [previewing, setPreviewing] = useState(false);
  const voiceId = useSessionStore((state) => state.controls.voiceId);
  const updateTokenPronunciation = useSessionStore((state) => state.updateTokenPronunciation);

  const preview = async () => {
    setPreviewing(true);
    try {
      const result = await api.pronunciationPreview(surface, draft, voiceId);
      await playPcmOnce(result.pcm_base64, result.sample_rate);
    } finally {
      setPreviewing(false);
    }
  };

  const apply = () => {
    updateTokenPronunciation(tokenIndex, draft, 1.0, "g2p");
  };

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={`phoneme-editor-${tokenIndex}`} className="text-xs font-medium text-slate-600">
        Manual phoneme editor (IPA-ish, space-separated)
      </label>
      <input
        id={`phoneme-editor-${tokenIndex}`}
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        className="focus-ring rounded-md border border-slate-300 px-2 py-1.5 font-mono text-sm"
      />
      <div className="flex gap-2">
        <Button variant="secondary" onClick={() => void preview()} disabled={previewing}>
          {previewing ? "Playing…" : "Preview"}
        </Button>
        <Button variant="secondary" onClick={apply}>
          Apply
        </Button>
      </div>
    </div>
  );
}
