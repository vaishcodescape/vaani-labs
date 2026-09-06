"use client";

import { useState } from "react";

import type { LexiconEntry } from "@/lib/schemas/lexicon";
import { Button } from "@/components/ui/Button";

interface LexiconTableProps {
  entries: LexiconEntry[];
  onUpdate: (entryId: string, body: { phonemes?: string; notes?: string }) => Promise<void>;
  onDelete: (entryId: string) => Promise<void>;
}

function EditableRow({ entry, onUpdate, onDelete }: { entry: LexiconEntry } & Omit<LexiconTableProps, "entries">) {
  const [phonemes, setPhonemes] = useState(entry.phonemes);
  const [notes, setNotes] = useState(entry.notes);
  const dirty = phonemes !== entry.phonemes || notes !== entry.notes;

  return (
    <tr className="border-b border-slate-100 last:border-0">
      <td className="px-3 py-2 font-medium text-slate-800">{entry.surface}</td>
      <td className="px-3 py-2 text-slate-500">{entry.language}</td>
      <td className="px-3 py-2">
        <input
          value={phonemes}
          onChange={(e) => setPhonemes(e.target.value)}
          aria-label={`Phonemes for ${entry.surface}`}
          className="focus-ring w-full rounded border border-transparent px-1.5 py-1 font-mono text-sm hover:border-slate-200"
        />
      </td>
      <td className="px-3 py-2">
        <input
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          aria-label={`Notes for ${entry.surface}`}
          className="focus-ring w-full rounded border border-transparent px-1.5 py-1 text-sm hover:border-slate-200"
        />
      </td>
      <td className="px-3 py-2 text-right">
        <div className="flex justify-end gap-1.5">
          <Button
            variant="secondary"
            disabled={!dirty}
            onClick={() => void onUpdate(entry.id, { phonemes, notes })}
          >
            Save
          </Button>
          <Button variant="danger" onClick={() => void onDelete(entry.id)}>
            Delete
          </Button>
        </div>
      </td>
    </tr>
  );
}

export function LexiconTable({ entries, onUpdate, onDelete }: LexiconTableProps) {
  if (entries.length === 0) {
    return <p className="text-sm text-slate-400">No lexicon entries yet.</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
            <th className="px-3 py-2">Surface</th>
            <th className="px-3 py-2">Language</th>
            <th className="px-3 py-2">Phonemes</th>
            <th className="px-3 py-2">Notes</th>
            <th className="px-3 py-2" />
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <EditableRow key={entry.id} entry={entry} onUpdate={onUpdate} onDelete={onDelete} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
