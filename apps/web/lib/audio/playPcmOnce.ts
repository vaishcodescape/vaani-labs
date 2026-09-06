/**
 * One-shot PCM16 playback for pronunciation previews — deliberately
 * separate from lib/audio/pcmPlayer.ts's streaming ring buffer, since a
 * preview is a single short, complete buffer rather than a live stream.
 */
export async function playPcmOnce(pcmBase64: string, sampleRate: number): Promise<void> {
  const binary = atob(pcmBase64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  const view = new DataView(bytes.buffer);
  const sampleCount = bytes.length / 2;
  const floatSamples = new Float32Array(sampleCount);
  for (let i = 0; i < sampleCount; i++) {
    floatSamples[i] = view.getInt16(i * 2, true) / 32768;
  }

  const context = new AudioContext({ sampleRate });
  const buffer = context.createBuffer(1, sampleCount, sampleRate);
  buffer.copyToChannel(floatSamples, 0);
  const source = context.createBufferSource();
  source.buffer = buffer;
  source.connect(context.destination);
  source.start();
  await new Promise<void>((resolve) => {
    source.onended = () => {
      void context.close();
      resolve();
    };
  });
}
