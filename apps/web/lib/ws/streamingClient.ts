import { wsStreamUrl } from "@/lib/config";
import { parseChunkFrame } from "@/lib/ws/frame";
import { ServerEventSchema, type ClientEvent, type ServerEvent } from "@/lib/schemas/ws";

export interface StreamingClientCallbacks {
  onOpen?: () => void;
  onClose?: () => void;
  onServerEvent: (event: ServerEvent) => void;
  onBinaryChunk: (revisionId: number, sequence: number, pcm: Int16Array) => void;
}

/**
 * Thin native-WebSocket wrapper: validates every inbound frame
 * (constraint #14) and hands typed events/chunks to its callbacks. No
 * business logic and no React here — see lib/hooks/useSynthesisSession.ts
 * for the layer that wires this into the Zustand store and audio player.
 */
export class StreamingClient {
  private ws: WebSocket | null = null;

  constructor(
    private readonly sessionId: string,
    private readonly callbacks: StreamingClientCallbacks,
  ) {}

  connect(): void {
    const ws = new WebSocket(wsStreamUrl(this.sessionId));
    ws.binaryType = "arraybuffer";

    ws.onopen = () => this.callbacks.onOpen?.();
    ws.onclose = () => this.callbacks.onClose?.();
    ws.onmessage = (event: MessageEvent<string | ArrayBuffer>) => {
      if (typeof event.data === "string") {
        this.handleTextFrame(event.data);
      } else {
        this.handleBinaryFrame(event.data);
      }
    };

    this.ws = ws;
  }

  private handleTextFrame(raw: string): void {
    let parsedJson: unknown;
    try {
      parsedJson = JSON.parse(raw);
    } catch {
      return;
    }
    const result = ServerEventSchema.safeParse(parsedJson);
    if (result.success) {
      this.callbacks.onServerEvent(result.data);
    }
  }

  private handleBinaryFrame(buffer: ArrayBuffer): void {
    const { revisionId, sequence, pcm } = parseChunkFrame(buffer);
    this.callbacks.onBinaryChunk(revisionId, sequence, pcm);
  }

  send(event: ClientEvent): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(event));
    }
  }

  close(): void {
    this.ws?.close();
    this.ws = null;
  }
}
