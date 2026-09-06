"use client";

import { useCallback } from "react";

import { api } from "@/lib/api/client";
import { playPcmOnce } from "@/lib/audio/playPcmOnce";
import { useSessionStore } from "@/lib/store/sessionStore";

export function useOfflineSynthesis() {
  const synthesize = useCallback(async () => {
    const { text, controls, setOfflineLoading, setOfflineResult } = useSessionStore.getState();
    setOfflineLoading(true);
    setOfflineResult(null);
    try {
      const result = await api.synthesizeOffline({
        text,
        voice_id: controls.voiceId,
        speed: controls.speed,
        pitch: controls.pitch,
        energy: controls.energy,
      });
      setOfflineResult({
        durationMs: result.duration_ms,
        rtf: result.rtf,
        sampleRate: result.sample_rate,
      });
      await playPcmOnce(result.pcm_base64, result.sample_rate);
    } finally {
      setOfflineLoading(false);
    }
  }, []);

  return { synthesize };
}
