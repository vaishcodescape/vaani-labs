"use client";

import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { TextEditor } from "@/components/studio/TextEditor";
import { TokenChips } from "@/components/studio/TokenChips";
import { PronunciationPanel } from "@/components/studio/PronunciationPanel";
import { ControlPanel } from "@/components/studio/ControlPanel";
import { EditResumeBar } from "@/components/studio/EditResumeBar";
import { WaveformView } from "@/components/studio/WaveformView";
import { TokenAlignmentTimeline } from "@/components/studio/TokenAlignmentTimeline";
import { MetricsPanel } from "@/components/studio/MetricsPanel";
import { BufferIndicator } from "@/components/studio/BufferIndicator";
import { useSessionStore } from "@/lib/store/sessionStore";

function StatusBadge() {
  const status = useSessionStore((state) => state.status);
  const tone =
    status === "error"
      ? "danger"
      : status === "running"
        ? "success"
        : status === "completed"
          ? "info"
          : "neutral";
  return <Badge tone={tone}>{status}</Badge>;
}

export default function StudioPage() {
  return (
    <div className="grid h-full grid-cols-1 gap-3 p-3 lg:grid-cols-[1fr_320px]">
      <div className="flex min-h-0 flex-col gap-3">
        <Card>
          <CardHeader title="Text" action={<StatusBadge />} />
          <CardBody className="flex flex-col gap-3">
            <TextEditor />
            <EditResumeBar />
          </CardBody>
        </Card>

        <div className="grid min-h-0 flex-1 grid-cols-1 gap-3 md:grid-cols-2">
          <Card className="flex min-h-0 flex-col">
            <CardHeader title="Token chips" />
            <CardBody className="overflow-auto">
              <TokenChips />
            </CardBody>
          </Card>
          <Card className="flex min-h-0 flex-col">
            <CardHeader title="Pronunciation" />
            <CardBody className="overflow-auto">
              <PronunciationPanel />
            </CardBody>
          </Card>
        </div>

        <Card>
          <CardHeader title="Waveform" action={<BufferIndicator />} />
          <CardBody className="flex flex-col gap-3">
            <WaveformView />
            <TokenAlignmentTimeline />
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Latency metrics" />
          <CardBody>
            <MetricsPanel />
          </CardBody>
        </Card>
      </div>

      <Card className="flex min-h-0 flex-col">
        <CardHeader title="Controls" />
        <CardBody className="overflow-auto">
          <ControlPanel />
        </CardBody>
      </Card>
    </div>
  );
}
