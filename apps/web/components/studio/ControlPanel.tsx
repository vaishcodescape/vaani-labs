"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api/client";
import { useOfflineSynthesis } from "@/lib/hooks/useOfflineSynthesis";
import { useSynthesisSession } from "@/lib/hooks/useSynthesisSession";
import { useSessionStore } from "@/lib/store/sessionStore";
import type { VoiceInfo } from "@/lib/schemas/system";
import { Button } from "@/components/ui/Button";
import { Select } from "@/components/ui/Select";
import { Slider } from "@/components/ui/Slider";
import { Toggle } from "@/components/ui/Toggle";

export function ControlPanel() {
  const [voices, setVoices] = useState<VoiceInfo[]>([]);
  const controls = useSessionStore((state) => state.controls);
  const setControls = useSessionStore((state) => state.setControls);
  const status = useSessionStore((state) => state.status);
  const offlineLoading = useSessionStore((state) => state.offlineLoading);
  const text = useSessionStore((state) => state.text);

  const { start, cancel, pause, resume } = useSynthesisSession();
  const { synthesize } = useOfflineSynthesis();

  useEffect(() => {
    api
      .voices()
      .then((result) => setVoices(result.voices))
      .catch(() => setVoices([]));
  }, []);

  const running = status === "running" || status === "analysing";
  const paused = status === "paused";

  const handleStart = () => {
    if (controls.streaming) {
      void start();
    } else {
      void synthesize();
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <Select
        id="voice-select"
        label="Speaker"
        value={controls.voiceId}
        onChange={(voiceId) => setControls({ voiceId })}
        options={voices.map((voice) => ({ value: voice.id, label: voice.label }))}
      />

      <Slider
        id="speed-slider"
        label="Speed"
        min={0.5}
        max={2.0}
        step={0.05}
        value={controls.speed}
        unit="x"
        onChange={(speed) => setControls({ speed })}
      />
      <Slider
        id="pitch-slider"
        label="Pitch"
        min={-12}
        max={12}
        step={1}
        value={controls.pitch}
        unit=" st"
        onChange={(pitch) => setControls({ pitch })}
      />
      <Slider
        id="energy-slider"
        label="Energy"
        min={0.25}
        max={2.0}
        step={0.05}
        value={controls.energy}
        onChange={(energy) => setControls({ energy })}
      />

      <Toggle
        id="streaming-toggle"
        label="Streaming (vs. offline)"
        checked={controls.streaming}
        onChange={(streaming) => setControls({ streaming })}
      />

      {controls.streaming && (
        <>
          <Slider
            id="chunk-size-slider"
            label="Chunk size"
            min={20}
            max={1000}
            step={20}
            value={controls.chunkSizeMs}
            unit=" ms"
            onChange={(chunkSizeMs) => setControls({ chunkSizeMs })}
          />
          <Slider
            id="mrss-slow-update-slider"
            label="MRSS slow-update rate"
            min={1}
            max={20}
            step={1}
            value={controls.mrssSlowUpdateRate}
            unit=" chunks"
            onChange={(mrssSlowUpdateRate) => setControls({ mrssSlowUpdateRate })}
          />
        </>
      )}

      <div className="flex flex-wrap gap-2 border-t border-slate-100 pt-3">
        <Button onClick={handleStart} disabled={text.length === 0 || offlineLoading}>
          {offlineLoading ? "Synthesizing…" : "Start"}
        </Button>
        {controls.streaming && (
          <>
            <Button variant="danger" onClick={cancel} disabled={!running && !paused}>
              Cancel
            </Button>
            {paused ? (
              <Button variant="secondary" onClick={resume}>
                Resume
              </Button>
            ) : (
              <Button variant="secondary" onClick={pause} disabled={!running}>
                Pause
              </Button>
            )}
          </>
        )}
      </div>
    </div>
  );
}
