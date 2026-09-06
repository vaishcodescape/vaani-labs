"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useRef } from "react";
import type { ReactNode } from "react";

import { PcmPlayer } from "@/lib/audio/pcmPlayer";
import { useSessionStore } from "@/lib/store/sessionStore";
import { StreamingClient } from "@/lib/ws/streamingClient";

function generateSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

interface SynthesisSessionActions {
  start: () => Promise<void>;
  cancel: () => void;
  pause: () => void;
  resume: () => void;
  editUnsynthesizedTail: (unsynthesizedText: string, editOffsetMs: number) => void;
  resetSession: () => void;
  ping: () => void;
}

const SynthesisSessionContext = createContext<SynthesisSessionActions | null>(null);

/**
 * Owns the single WebSocket connection + AudioWorklet player for the
 * whole app (one browser tab == one Synthesis Studio session). Mounted
 * once in app/layout.tsx so every screen (Studio, Diagnostics) that
 * calls `useSynthesisSession()` shares the same live connection instead
 * of each opening its own (AGENTS.md rule #4/#7/#8: one session, one
 * WebSocket, state lives in one place).
 */
export function SynthesisSessionProvider({ children }: { children: ReactNode }) {
  const clientRef = useRef<StreamingClient | null>(null);
  const playerRef = useRef<PcmPlayer | null>(null);

  useEffect(() => {
    const sessionId = generateSessionId();
    useSessionStore.getState().setSessionId(sessionId);

    const client = new StreamingClient(sessionId, {
      onOpen: () => useSessionStore.getState().setConnectionOpen(true),
      onClose: () => useSessionStore.getState().setConnectionOpen(false),
      onServerEvent: (event) => {
        useSessionStore.getState().applyServerEvent(event);
      },
      onBinaryChunk: (revisionId, _sequence, pcm) => {
        const accepted = useSessionStore.getState().acceptBinaryChunk(revisionId, pcm);
        if (accepted) {
          playerRef.current?.pushInt16(pcm);
        }
      },
    });
    client.connect();
    clientRef.current = client;

    return () => {
      client.close();
      clientRef.current = null;
      void playerRef.current?.close();
      playerRef.current = null;
    };
  }, []);

  const ensurePlayer = useCallback(async (): Promise<PcmPlayer> => {
    if (!playerRef.current) {
      playerRef.current = new PcmPlayer(useSessionStore.getState().sampleRate);
    }
    await playerRef.current.init();
    await playerRef.current.resume();
    playerRef.current.onStatus(({ bufferedMs, underrun }) => {
      useSessionStore.getState().setBufferStatus(bufferedMs, underrun);
    });
    return playerRef.current;
  }, []);

  const start = useCallback(async () => {
    const { text, controls } = useSessionStore.getState();
    await ensurePlayer();
    playerRef.current?.reset();
    clientRef.current?.send({
      type: "start",
      text,
      voice_id: controls.voiceId,
      speed: controls.speed,
      pitch: controls.pitch,
      energy: controls.energy,
      streaming: controls.streaming,
      chunk_size_ms: controls.chunkSizeMs,
      mrss_slow_update_rate: controls.mrssSlowUpdateRate,
    });
  }, [ensurePlayer]);

  const cancel = useCallback(() => {
    clientRef.current?.send({ type: "cancel" });
    playerRef.current?.reset();
  }, []);

  const pause = useCallback(() => {
    clientRef.current?.send({ type: "pause" });
  }, []);

  const resume = useCallback(() => {
    clientRef.current?.send({ type: "resume" });
  }, []);

  const editUnsynthesizedTail = useCallback((unsynthesizedText: string, editOffsetMs: number) => {
    const { revisionId } = useSessionStore.getState();
    clientRef.current?.send({
      type: "edit",
      revision_id: revisionId + 1,
      unsynthesized_text: unsynthesizedText,
      edit_offset_ms: editOffsetMs,
    });
  }, []);

  const resetSession = useCallback(() => {
    clientRef.current?.send({ type: "reset" });
    playerRef.current?.reset();
    useSessionStore.getState().resetForNewSession();
  }, []);

  const ping = useCallback(() => {
    clientRef.current?.send({ type: "ping" });
  }, []);

  const actions = useMemo<SynthesisSessionActions>(
    () => ({ start, cancel, pause, resume, editUnsynthesizedTail, resetSession, ping }),
    [start, cancel, pause, resume, editUnsynthesizedTail, resetSession, ping],
  );

  return (
    <SynthesisSessionContext.Provider value={actions}>{children}</SynthesisSessionContext.Provider>
  );
}

export function useSynthesisSession(): SynthesisSessionActions {
  const context = useContext(SynthesisSessionContext);
  if (!context) {
    throw new Error("useSynthesisSession must be used within a SynthesisSessionProvider");
  }
  return context;
}
