"use client";

import { useLexicon } from "@/lib/hooks/useLexicon";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { LexiconForm } from "@/components/lexicon/LexiconForm";
import { LexiconTable } from "@/components/lexicon/LexiconTable";

export default function LexiconPage() {
  const { entries, loading, error, query, setQuery, language, setLanguage, create, update, remove } =
    useLexicon();

  return (
    <div className="flex flex-col gap-3 p-4">
      <Card>
        <CardHeader title="Add correction" />
        <CardBody>
          <LexiconForm onCreate={create} />
        </CardBody>
      </Card>

      <Card>
        <CardHeader
          title="Entries"
          action={
            <div className="flex gap-2">
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search surface…"
                aria-label="Search lexicon"
                className="focus-ring rounded-md border border-slate-300 px-2 py-1 text-sm"
              />
              <input
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                placeholder="Language filter…"
                aria-label="Filter by language"
                className="focus-ring w-32 rounded-md border border-slate-300 px-2 py-1 text-sm"
              />
            </div>
          }
        />
        <CardBody>
          {loading && <p className="text-sm text-slate-400">Loading…</p>}
          {error && (
            <p role="alert" className="text-sm text-rose-600">
              {error}
            </p>
          )}
          {!loading && !error && (
            <LexiconTable entries={entries} onUpdate={update} onDelete={remove} />
          )}
        </CardBody>
      </Card>
    </div>
  );
}
