"use client";

import { useSynthesisSession } from "@/lib/hooks/useSynthesisSession";
import { useSessionStore } from "@/lib/store/sessionStore";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";

export default function DiagnosticsPage() {
  const sessionId = useSessionStore((state) => state.sessionId);
  const revisionId = useSessionStore((state) => state.revisionId);
  const status = useSessionStore((state) => state.status);
  const connectionOpen = useSessionStore((state) => state.connectionOpen);
  const lastPongAt = useSessionStore((state) => state.lastPongAt);
  const warnings = useSessionStore((state) => state.warnings);
  const chunkMetrics = useSessionStore((state) => state.chunkMetrics);
  const errorMessage = useSessionStore((state) => state.errorMessage);
  const { ping, resetSession } = useSynthesisSession();

  return (
    <div className="flex flex-col gap-3 p-4">
      <Card>
        <CardHeader
          title="Connection"
          action={<Badge tone={connectionOpen ? "success" : "danger"}>{connectionOpen ? "open" : "closed"}</Badge>}
        />
        <CardBody className="flex flex-col gap-2">
          <dl className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
            <div>
              <dt className="text-xs text-slate-400">Session ID</dt>
              <dd className="truncate font-mono text-xs">{sessionId ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-xs text-slate-400">Revision</dt>
              <dd className="font-medium">{revisionId}</dd>
            </div>
            <div>
              <dt className="text-xs text-slate-400">Status</dt>
              <dd className="font-medium">{status}</dd>
            </div>
            <div>
              <dt className="text-xs text-slate-400">Last pong</dt>
              <dd className="font-medium">{lastPongAt ? new Date(lastPongAt).toLocaleTimeString() : "—"}</dd>
            </div>
          </dl>
          {errorMessage && <p className="text-sm text-rose-600">Last error: {errorMessage}</p>}
          <div className="flex gap-2">
            <Button variant="secondary" onClick={ping}>
              Send ping
            </Button>
            <Button variant="ghost" onClick={resetSession}>
              Hard reset session
            </Button>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title={`Warnings (${warnings.length})`} />
        <CardBody>
          {warnings.length === 0 ? (
            <p className="text-sm text-slate-400">No warnings this session.</p>
          ) : (
            <ul className="flex flex-col gap-1 text-sm">
              {warnings.map((w, i) => (
                <li key={i} className="flex items-center gap-2">
                  <Badge tone="warning">{w.code}</Badge>
                  <span className="text-slate-600">{w.message}</span>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>

      <Card className="flex min-h-0 flex-1 flex-col">
        <CardHeader title={`Chunk log (${chunkMetrics.length})`} />
        <CardBody className="overflow-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="text-slate-400">
                <th className="px-2 py-1">Seq</th>
                <th className="px-2 py-1">Acoustic ms</th>
                <th className="px-2 py-1">Vocoder ms</th>
                <th className="px-2 py-1">Total ms</th>
                <th className="px-2 py-1">First audio</th>
              </tr>
            </thead>
            <tbody>
              {chunkMetrics.map((c) => (
                <tr key={c.sequence} className="border-t border-slate-100">
                  <td className="px-2 py-1 tabular-nums">{c.sequence}</td>
                  <td className="px-2 py-1 tabular-nums">{c.acousticMs.toFixed(1)}</td>
                  <td className="px-2 py-1 tabular-nums">{c.vocoderMs.toFixed(1)}</td>
                  <td className="px-2 py-1 tabular-nums">{c.chunkLatencyMs.toFixed(1)}</td>
                  <td className="px-2 py-1">{c.isFirstAudio ? "✓" : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
