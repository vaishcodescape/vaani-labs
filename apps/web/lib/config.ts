export const API_BASE_URL: string =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const WS_BASE_URL: string = process.env.NEXT_PUBLIC_WS_BASE_URL ?? "ws://localhost:8000";

export function apiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export function wsStreamUrl(sessionId: string): string {
  return `${WS_BASE_URL}/api/v1/synthesis/stream/${encodeURIComponent(sessionId)}`;
}
