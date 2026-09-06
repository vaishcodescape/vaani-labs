"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api/client";
import type { PronunciationCandidate } from "@/lib/schemas/pronunciation";

export function usePronunciationCandidates(
  surface: string | null,
  language: string | null,
  script: string | null,
) {
  const [candidates, setCandidates] = useState<PronunciationCandidate[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!surface || !language || !script) {
      setCandidates([]);
      return;
    }
    let cancelled = false;
    setLoading(true);
    api
      .pronunciationCandidates(surface, language, script)
      .then((result) => {
        if (!cancelled) setCandidates(result.candidates);
      })
      .catch(() => {
        if (!cancelled) setCandidates([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [surface, language, script]);

  return { candidates, loading };
}
