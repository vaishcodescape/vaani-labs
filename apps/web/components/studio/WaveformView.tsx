"use client";

import { useEffect, useRef } from "react";

import { useSessionStore } from "@/lib/store/sessionStore";

export function WaveformView() {
  const peaks = useSessionStore((state) => state.waveformPeaks);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const { width, height } = canvas;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#f8fafc";
    ctx.fillRect(0, 0, width, height);

    if (peaks.length === 0) {
      ctx.strokeStyle = "#cbd5e1";
      ctx.beginPath();
      ctx.moveTo(0, height / 2);
      ctx.lineTo(width, height / 2);
      ctx.stroke();
      return;
    }

    const barWidth = width / peaks.length;
    ctx.fillStyle = "#0284c7";
    peaks.forEach((peak, i) => {
      const barHeight = Math.max(2, peak * height);
      ctx.fillRect(i * barWidth, (height - barHeight) / 2, Math.max(1, barWidth - 1), barHeight);
    });
  }, [peaks]);

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={80}
      role="img"
      aria-label="Waveform of generated audio"
      className="w-full rounded-md border border-slate-200"
    />
  );
}
