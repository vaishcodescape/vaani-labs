/**
 * Browser-side PCM playback: an AudioContext + AudioWorkletNode pair
 * fronting the ring buffer implemented in
 * public/worklets/pcm-player-processor.js. This module owns the only
 * AudioContext in the app; callers push already-decoded Float32 PCM
 * and never touch Web Audio primitives directly.
 */

export interface PcmPlayerStatus {
  bufferedMs: number;
  underrun: boolean;
}

export type PcmPlayerStatusListener = (status: PcmPlayerStatus) => void;

export class PcmPlayer {
  private context: AudioContext | null = null;
  private node: AudioWorkletNode | null = null;
  private sampleRate: number;
  private statusListener: PcmPlayerStatusListener | null = null;

  constructor(sampleRate: number) {
    this.sampleRate = sampleRate;
  }

  async init(): Promise<void> {
    if (this.context) return;
    const AudioContextCtor = window.AudioContext;
    const context = new AudioContextCtor({ sampleRate: this.sampleRate });
    await context.audioWorklet.addModule("/worklets/pcm-player-processor.js");
    const node = new AudioWorkletNode(context, "pcm-player-processor", {
      numberOfInputs: 0,
      numberOfOutputs: 1,
      outputChannelCount: [1],
    });
    node.port.onmessage = (event: MessageEvent) => {
      const message = event.data as { type: string; bufferedSamples: number; underrun: boolean };
      if (message.type === "status" && this.statusListener) {
        this.statusListener({
          bufferedMs: (message.bufferedSamples / this.sampleRate) * 1000,
          underrun: message.underrun,
        });
      }
    };
    node.connect(context.destination);
    this.context = context;
    this.node = node;
  }

  onStatus(listener: PcmPlayerStatusListener): void {
    this.statusListener = listener;
  }

  /** Push mono PCM16 (little-endian) samples for immediate playback. */
  pushInt16(samples: Int16Array): void {
    if (!this.node) return;
    const floatSamples = new Float32Array(samples.length);
    for (let i = 0; i < samples.length; i++) {
      const raw = samples[i] ?? 0;
      floatSamples[i] = raw / 32768;
    }
    this.node.port.postMessage({ type: "push", samples: floatSamples }, [floatSamples.buffer]);
  }

  /** Discard all buffered-but-unplayed audio (cancel, or a stale revision). */
  reset(): void {
    this.node?.port.postMessage({ type: "reset" });
  }

  async resume(): Promise<void> {
    if (this.context && this.context.state === "suspended") {
      await this.context.resume();
    }
  }

  async close(): Promise<void> {
    this.node?.disconnect();
    await this.context?.close();
    this.context = null;
    this.node = null;
  }
}
