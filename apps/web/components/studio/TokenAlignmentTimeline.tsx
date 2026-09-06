"use client";

import { useSessionStore } from "@/lib/store/sessionStore";
import { scriptColorClasses } from "@/components/studio/scriptColors";

export function TokenAlignmentTimeline() {
  const tokens = useSessionStore((state) => state.tokens);
  const tokenDurationsMs = useSessionStore((state) => state.tokenDurationsMs);
  const chunkMetrics = useSessionStore((state) => state.chunkMetrics);
  const controls = useSessionStore((state) => state.controls);

  if (tokenDurationsMs.length === 0) {
    return (
      <p className="text-sm text-slate-400">
        Token alignment appears once synthesis starts (durations come from the acoustic plan).
      </p>
    );
  }

  const totalMs = tokenDurationsMs.reduce((a, b) => a + b, 0) || 1;
  const producedMs = chunkMetrics.length * controls.chunkSizeMs;

  return (
    <div className="relative h-10 w-full overflow-hidden rounded-md border border-slate-200">
      <div className="flex h-full w-full">
        {tokens.map((token, i) => {
          const durationMs = tokenDurationsMs[i] ?? 0;
          if (durationMs <= 0) return null;
          const widthPct = (durationMs / totalMs) * 100;
          return (
            <div
              key={token.index}
              style={{ width: `${widthPct}%` }}
              title={`${token.surface} (${Math.round(durationMs)}ms)`}
              className={`flex items-center justify-center overflow-hidden border-r border-white/60 text-[10px] ${scriptColorClasses(
                token.script,
              )}`}
            >
              <span className="truncate px-0.5">{token.surface}</span>
            </div>
          );
        })}
      </div>
      <div
        className="pointer-events-none absolute inset-y-0 border-l-2 border-rose-500"
        style={{ left: `${Math.min((producedMs / totalMs) * 100, 100)}%` }}
        aria-label="Synthesis playhead"
      />
    </div>
  );
}
