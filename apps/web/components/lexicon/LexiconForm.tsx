"use client";

import { useState } from "react";

import type { LexiconCreateRequest } from "@/lib/schemas/lexicon";
import { Button } from "@/components/ui/Button";

interface LexiconFormProps {
  onCreate: (body: LexiconCreateRequest) => Promise<void>;
}

const EMPTY: LexiconCreateRequest = { surface: "", language: "en", phonemes: "", notes: "" };

export function LexiconForm({ onCreate }: LexiconFormProps) {
  const [form, setForm] = useState<LexiconCreateRequest>(EMPTY);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      await onCreate(form);
      setForm(EMPTY);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create entry.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
      className="grid grid-cols-1 gap-2 sm:grid-cols-5 sm:items-end"
    >
      <div className="sm:col-span-1">
        <label htmlFor="new-surface" className="text-xs font-medium text-slate-600">
          Surface
        </label>
        <input
          id="new-surface"
          required
          value={form.surface}
          onChange={(e) => setForm({ ...form, surface: e.target.value })}
          className="focus-ring mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        />
      </div>
      <div className="sm:col-span-1">
        <label htmlFor="new-language" className="text-xs font-medium text-slate-600">
          Language
        </label>
        <input
          id="new-language"
          required
          value={form.language}
          onChange={(e) => setForm({ ...form, language: e.target.value })}
          className="focus-ring mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        />
      </div>
      <div className="sm:col-span-1">
        <label htmlFor="new-phonemes" className="text-xs font-medium text-slate-600">
          Phonemes
        </label>
        <input
          id="new-phonemes"
          required
          value={form.phonemes}
          onChange={(e) => setForm({ ...form, phonemes: e.target.value })}
          className="focus-ring mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 font-mono text-sm"
        />
      </div>
      <div className="sm:col-span-1">
        <label htmlFor="new-notes" className="text-xs font-medium text-slate-600">
          Notes
        </label>
        <input
          id="new-notes"
          value={form.notes}
          onChange={(e) => setForm({ ...form, notes: e.target.value })}
          className="focus-ring mt-1 w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm"
        />
      </div>
      <Button type="submit" disabled={submitting}>
        Add entry
      </Button>
      {error && (
        <span role="alert" className="text-xs text-rose-600 sm:col-span-5">
          {error}
        </span>
      )}
    </form>
  );
}
