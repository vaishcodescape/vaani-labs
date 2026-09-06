import { describe, expect, it } from "vitest";

import { parseChunkFrame } from "@/lib/ws/frame";

function buildFrame(revisionId: number, sequence: number, samples: number[]): ArrayBuffer {
  const buffer = new ArrayBuffer(12 + samples.length * 2);
  const view = new DataView(buffer);
  view.setUint32(0, revisionId, false);
  view.setUint32(4, sequence, false);
  view.setUint32(8, samples.length, false);
  samples.forEach((sample, i) => view.setInt16(12 + i * 2, sample, true));
  return buffer;
}

describe("parseChunkFrame", () => {
  it("parses header fields and PCM payload", () => {
    const frame = buildFrame(3, 7, [100, -200, 32767, -32768]);
    const parsed = parseChunkFrame(frame);
    expect(parsed.revisionId).toBe(3);
    expect(parsed.sequence).toBe(7);
    expect(Array.from(parsed.pcm)).toEqual([100, -200, 32767, -32768]);
  });

  it("handles an empty PCM payload", () => {
    const frame = buildFrame(1, 0, []);
    const parsed = parseChunkFrame(frame);
    expect(parsed.pcm.length).toBe(0);
  });
});
