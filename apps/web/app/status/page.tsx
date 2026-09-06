"use client";

import { useSystemStatus } from "@/lib/hooks/useSystemStatus";
import { Badge } from "@/components/ui/Badge";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";

export default function StatusPage() {
  const { system, models, loading, error } = useSystemStatus();

  return (
    <div className="flex flex-col gap-3 p-4">
      <Card>
        <CardHeader
          title="Backend health"
          action={
            loading ? (
              <Badge>checking…</Badge>
            ) : error ? (
              <Badge tone="danger">unreachable</Badge>
            ) : (
              <Badge tone="success">{system?.status}</Badge>
            )
          }
        />
        <CardBody>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          {system && (
            <dl className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
              <div>
                <dt className="text-xs text-slate-400">Version</dt>
                <dd className="font-medium">{system.version}</dd>
              </div>
              <div>
                <dt className="text-xs text-slate-400">Uptime</dt>
                <dd className="font-medium">{system.uptime_seconds.toFixed(0)}s</dd>
              </div>
              <div>
                <dt className="text-xs text-slate-400">Active sessions</dt>
                <dd className="font-medium">{system.active_sessions}</dd>
              </div>
              <div>
                <dt className="text-xs text-slate-400">Lexicon entries</dt>
                <dd className="font-medium">{system.lexicon_entry_count}</dd>
              </div>
            </dl>
          )}
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Providers" />
        <CardBody>
          {system && (
            <ul className="grid grid-cols-1 gap-1.5 text-sm sm:grid-cols-2">
              {Object.entries(system.providers).map(([key, value]) => (
                <li key={key} className="flex items-center justify-between rounded border border-slate-100 px-2 py-1">
                  <span className="text-slate-500">{key}</span>
                  <span className="font-mono text-xs text-slate-700">{value}</span>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Models" />
        <CardBody>
          {models && (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div>
                <h3 className="mb-1 text-xs font-medium text-slate-500">Acoustic models</h3>
                {models.acoustic_models.map((m) => (
                  <div key={m.id} className="flex items-center gap-2 text-sm">
                    <span>{m.id}</span>
                    <Badge>{m.kind}</Badge>
                    {m.is_default && <Badge tone="info">default</Badge>}
                  </div>
                ))}
              </div>
              <div>
                <h3 className="mb-1 text-xs font-medium text-slate-500">Vocoders</h3>
                {models.vocoders.map((m) => (
                  <div key={m.id} className="flex items-center gap-2 text-sm">
                    <span>{m.id}</span>
                    <Badge>{m.kind}</Badge>
                    {m.is_default && <Badge tone="info">default</Badge>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
