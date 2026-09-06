"use client";

import { useSessionStore } from "@/lib/store/sessionStore";
import { useTextAnalysis } from "@/lib/hooks/useTextAnalysis";
import { SAMPLE_SENTENCES } from "@/lib/samples";
import { Button } from "@/components/ui/Button";

export function TextEditor() {
  const text = useSessionStore((state) => state.text);
  const setText = useSessionStore((state) => state.setText);
  const { analyse, loading, error } = useTextAnalysis();

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap gap-1.5" role="group" aria-label="Sample sentences">
        {SAMPLE_SENTENCES.map((sample) => (
          <button
            key={sample.id}
            onClick={() => setText(sample.text)}
            className="focus-ring rounded-full border border-slate-300 bg-white px-2.5 py-1 text-xs text-slate-600 hover:border-sky-400 hover:text-sky-700"
          >
            {sample.label}
          </button>
        ))}
      </div>

      <textarea
        aria-label="Multilingual text editor"
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="Type Hindi, Gujarati, Marathi, romanized Indic, or Indic-English code-switched text…"
        className="focus-ring h-32 w-full resize-none rounded-md border border-slate-300 p-3 text-lg leading-relaxed"
        lang="und"
      />

      <div className="flex items-center gap-2">
        <Button onClick={() => void analyse(text)} disabled={loading || text.length === 0}>
          {loading ? "Analysing…" : "Analyse Text"}
        </Button>
        {error && (
          <span role="alert" className="text-xs text-rose-600">
            {error}
          </span>
        )}
      </div>
    </div>
  );
}
