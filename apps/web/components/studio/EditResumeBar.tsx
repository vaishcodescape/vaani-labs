"use client";

import { useState } from "react";

import { useSynthesisSession } from "@/lib/hooks/useSynthesisSession";
import { useSessionStore } from "@/lib/store/sessionStore";
import { Button } from "@/components/ui/Button";

/**
 * Mid-stream edit workflow (requirement #12/#7 in the task brief): while
 * a revision is running or paused, the user can edit the *unsynthesized*
 * remainder and resume without replaying already-produced audio.
 *
 * Phase-1 simplification: rather than computing an exact per-character
 * "already spoken" boundary from token alignment + playback position,
 * the whole visible text is treated as the editable "tail" and resumed
 * as a new revision. Already-buffered/played audio is never reset on
 * `edit` (see lib/hooks/useSynthesisSession.ts), so nothing already
 * heard is replayed — only the precise prefix-locking UI is deferred.
 * See docs/demo-script.md and README limitations.
 */
export function EditResumeBar() {
  const status = useSessionStore((state) => state.status);
  const text = useSessionStore((state) => state.text);
  const controls = useSessionStore((state) => state.controls);
  const chunkMetrics = useSessionStore((state) => state.chunkMetrics);
  const { editUnsynthesizedTail } = useSynthesisSession();
  const [draft, setDraft] = useState(text);
  const [open, setOpen] = useState(false);

  if (status !== "running" && status !== "paused") return null;

  const approxElapsedMs = chunkMetrics.length * controls.chunkSizeMs;

  if (!open) {
    return (
      <Button variant="secondary" onClick={() => { setDraft(text); setOpen(true); }}>
        Edit remaining text…
      </Button>
    );
  }

  return (
    <div className="flex flex-col gap-2 rounded-md border border-amber-200 bg-amber-50 p-3">
      <label htmlFor="edit-tail" className="text-xs font-medium text-amber-800">
        Edit unsynthesized text and resume (~{approxElapsedMs}ms already produced will not be
        replayed)
      </label>
      <textarea
        id="edit-tail"
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        className="focus-ring h-20 resize-none rounded-md border border-amber-300 p-2 text-sm"
      />
      <div className="flex gap-2">
        <Button
          onClick={() => {
            editUnsynthesizedTail(draft, approxElapsedMs);
            setOpen(false);
          }}
        >
          Resume with edits
        </Button>
        <Button variant="ghost" onClick={() => setOpen(false)}>
          Cancel edit
        </Button>
      </div>
    </div>
  );
}
