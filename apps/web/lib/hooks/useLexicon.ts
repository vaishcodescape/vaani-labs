"use client";

import { useCallback, useEffect, useState } from "react";

import { api } from "@/lib/api/client";
import { ApiError } from "@/lib/api/errors";
import type { LexiconCreateRequest, LexiconEntry, LexiconUpdateRequest } from "@/lib/schemas/lexicon";

export function useLexicon() {
  const [entries, setEntries] = useState<LexiconEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.listLexicon({
        q: query || undefined,
        language: language || undefined,
      });
      setEntries(result.entries);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load lexicon.");
    } finally {
      setLoading(false);
    }
  }, [query, language]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const create = useCallback(
    async (body: LexiconCreateRequest) => {
      await api.createLexiconEntry(body);
      await refresh();
    },
    [refresh],
  );

  const update = useCallback(
    async (entryId: string, body: LexiconUpdateRequest) => {
      await api.updateLexiconEntry(entryId, body);
      await refresh();
    },
    [refresh],
  );

  const remove = useCallback(
    async (entryId: string) => {
      await api.deleteLexiconEntry(entryId);
      await refresh();
    },
    [refresh],
  );

  return { entries, loading, error, query, setQuery, language, setLanguage, create, update, remove };
}
