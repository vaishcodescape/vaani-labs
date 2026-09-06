"use client";

import { useSessionStore } from "@/lib/store/sessionStore";

export function BufferIndicator() {
  const bufferedMs = useSessionStore((state) => state.bufferedMs);
  const underrun = useSessionStore((state) => state.bufferUnderrun);
  const status = useSessionStore((state) => state.status);

  const level = Math.min(bufferedMs / 1000, 1); // 1s = "full" for the bar

  return (
    <div className="flex items-center gap-2" aria-label="Streaming buffer indicator">
      <div className="h-2 w-32 overflow-hidden rounded-full bg-slate-200">
        <div
          className={`h-full transition-all ${underrun ? "bg-rose-500" : "bg-emerald-500"}`}
          style={{ width: `${level * 100}%` }}
        />
      </div>
      <span className="text-xs tabular-nums text-slate-500">{Math.round(bufferedMs)}ms buffered</span>
      {underrun && status === "running" && (
        <span role="alert" className="text-xs font-medium text-rose-600">
          buffer underflow
        </span>
      )}
    </div>
  );
}
