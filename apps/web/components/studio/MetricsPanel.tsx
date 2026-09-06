"use client";

import { useSessionStore } from "@/lib/store/sessionStore";

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col">
      <span className="text-[11px] uppercase tracking-wide text-slate-400">{label}</span>
      <span className="tabular-nums text-lg font-semibold text-slate-800">{value}</span>
    </div>
  );
}

export function MetricsPanel() {
  const completion = useSessionStore((state) => state.completion);
  const chunkMetrics = useSessionStore((state) => state.chunkMetrics);
  const offlineResult = useSessionStore((state) => state.offlineResult);

  const latestChunk = chunkMetrics.at(-1);

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat
          label="First-audio latency"
          value={
            completion
              ? `${completion.firstAudioLatencyMs.toFixed(0)}ms`
              : chunkMetrics[0]
                ? `${chunkMetrics[0].chunkLatencyMs.toFixed(0)}ms`
                : "—"
          }
        />
        <Stat label="RTF" value={completion ? completion.rtf.toFixed(3) : "—"} />
        <Stat
          label="P50 chunk latency"
          value={completion ? `${completion.p50ChunkLatencyMs.toFixed(0)}ms` : "—"}
        />
        <Stat
          label="P95 / P99 chunk latency"
          value={
            completion
              ? `${completion.p95ChunkLatencyMs.toFixed(0)} / ${completion.p99ChunkLatencyMs.toFixed(0)}ms`
              : "—"
          }
        />
      </div>

      {latestChunk && !completion && (
        <p className="text-xs text-slate-400">
          Latest chunk #{latestChunk.sequence}: acoustic {latestChunk.acousticMs.toFixed(1)}ms +
          vocoder {latestChunk.vocoderMs.toFixed(1)}ms
        </p>
      )}

      {offlineResult && (
        <div className="rounded-md border border-slate-200 bg-slate-50 p-2.5 text-xs text-slate-600">
          <span className="font-medium text-slate-700">Offline comparison:</span> duration{" "}
          {offlineResult.durationMs.toFixed(0)}ms, RTF {offlineResult.rtf.toFixed(3)} — no partial
          playback, audio arrives only once fully synthesized.
        </div>
      )}
    </div>
  );
}
