"use client";

import { useCallback, useState } from "react";

import { api } from "@/lib/api/client";
import { ApiError } from "@/lib/api/errors";
import { useSessionStore } from "@/lib/store/sessionStore";

export function useTextAnalysis() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyse = useCallback(async (text: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.analyseText(text);
      useSessionStore.getState().setAnalysisResult({
        text: result.text,
        tokens: result.tokens,
        codeSwitchSpans: result.code_switch_spans,
      });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to analyse text.");
    } finally {
      setLoading(false);
    }
  }, []);

  return { analyse, loading, error };
}
