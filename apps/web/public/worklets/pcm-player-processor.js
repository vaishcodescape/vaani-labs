/**
 * Ring-buffer PCM player AudioWorkletProcessor.
 *
 * Receives mono Float32 PCM chunks over the message port (already
 * revision-filtered and endianness-converted by lib/audio/ringBuffer.ts
 * on the main thread — this processor only ever sees audio it should
 * actually play) and drains them sample-by-sample into each 128-frame
 * render quantum. Underrun (buffer empty mid-utterance) plays silence
 * rather than glitching, and is reported to the main thread so the UI
 * can flag it.
 */
class PcmPlayerProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._chunks = [];
    this._readOffset = 0;
    this._bufferedSamples = 0;
    this._framesSinceReport = 0;
    this._reportEveryFrames = Math.round(sampleRate / 20); // ~50ms
    this._underrun = false;

    this.port.onmessage = (event) => {
      const message = event.data;
      if (message.type === "push") {
        this._chunks.push(message.samples);
        this._bufferedSamples += message.samples.length;
      } else if (message.type === "reset") {
        this._chunks = [];
        this._readOffset = 0;
        this._bufferedSamples = 0;
      }
    };
  }

  process(_inputs, outputs) {
    const output = outputs[0][0];
    for (let i = 0; i < output.length; i++) {
      if (this._chunks.length === 0) {
        output[i] = 0;
        if (this._bufferedSamples === 0 && !this._underrun) {
          this._underrun = true;
        }
        continue;
      }
      const chunk = this._chunks[0];
      output[i] = chunk[this._readOffset];
      this._readOffset++;
      this._bufferedSamples--;
      this._underrun = false;
      if (this._readOffset >= chunk.length) {
        this._chunks.shift();
        this._readOffset = 0;
      }
    }

    this._framesSinceReport += output.length;
    if (this._framesSinceReport >= this._reportEveryFrames) {
      this._framesSinceReport = 0;
      this.port.postMessage({
        type: "status",
        bufferedSamples: this._bufferedSamples,
        underrun: this._underrun,
      });
    }

    return true;
  }
}

registerProcessor("pcm-player-processor", PcmPlayerProcessor);
