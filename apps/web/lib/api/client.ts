import { z } from "zod";

import { toApiError } from "@/lib/api/errors";
import { apiUrl } from "@/lib/config";
import {
  LexiconCreateRequestSchema,
  LexiconEntrySchema,
  LexiconListResponseSchema,
  LexiconUpdateRequestSchema,
  type LexiconCreateRequest,
  type LexiconEntry,
  type LexiconListResponse,
  type LexiconUpdateRequest,
} from "@/lib/schemas/lexicon";
import {
  PronunciationCandidatesResponseSchema,
  PronunciationPreviewResponseSchema,
  type PronunciationCandidatesResponse,
  type PronunciationPreviewResponse,
} from "@/lib/schemas/pronunciation";
import {
  HealthResponseSchema,
  LanguagesResponseSchema,
  ModelsResponseSchema,
  SystemResponseSchema,
  VoicesResponseSchema,
  type HealthResponse,
  type LanguagesResponse,
  type ModelsResponse,
  type SystemResponse,
  type VoicesResponse,
} from "@/lib/schemas/system";
import {
  OfflineSynthesisRequestSchema,
  OfflineSynthesisResponseSchema,
  type OfflineSynthesisRequest,
  type OfflineSynthesisResponse,
} from "@/lib/schemas/synthesis";
import { AnalyseTextResponseSchema, type AnalyseTextResponse } from "@/lib/schemas/text";

async function request<T>(
  path: string,
  schema: z.ZodType<T>,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(apiUrl(path), {
    ...init,
    headers: { "content-type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    throw await toApiError(response);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  const body: unknown = await response.json();
  return schema.parse(body);
}

function postJson(path: string, body: unknown): RequestInit {
  return { method: "POST", body: JSON.stringify(body) };
}

export const api = {
  health: (): Promise<HealthResponse> => request("/api/v1/health", HealthResponseSchema),

  system: (): Promise<SystemResponse> => request("/api/v1/system", SystemResponseSchema),

  models: (): Promise<ModelsResponse> => request("/api/v1/models", ModelsResponseSchema),

  voices: (): Promise<VoicesResponse> => request("/api/v1/voices", VoicesResponseSchema),

  languages: (): Promise<LanguagesResponse> =>
    request("/api/v1/languages", LanguagesResponseSchema),

  analyseText: (text: string): Promise<AnalyseTextResponse> =>
    request("/api/v1/text/analyse", AnalyseTextResponseSchema, postJson("/api/v1/text/analyse", { text })),

  pronunciationCandidates: (
    surface: string,
    language: string,
    script: string,
  ): Promise<PronunciationCandidatesResponse> =>
    request(
      "/api/v1/pronunciation/candidates",
      PronunciationCandidatesResponseSchema,
      postJson("/api/v1/pronunciation/candidates", { surface, language, script }),
    ),

  pronunciationPreview: (
    surface: string,
    phonemes: string,
    voiceId: string,
  ): Promise<PronunciationPreviewResponse> =>
    request(
      "/api/v1/pronunciation/preview",
      PronunciationPreviewResponseSchema,
      postJson("/api/v1/pronunciation/preview", { surface, phonemes, voice_id: voiceId }),
    ),

  listLexicon: (params?: { q?: string; language?: string }): Promise<LexiconListResponse> => {
    const search = new URLSearchParams();
    if (params?.q) search.set("q", params.q);
    if (params?.language) search.set("language", params.language);
    const qs = search.toString();
    return request(`/api/v1/lexicon${qs ? `?${qs}` : ""}`, LexiconListResponseSchema);
  },

  createLexiconEntry: (body: LexiconCreateRequest): Promise<LexiconEntry> =>
    request(
      "/api/v1/lexicon",
      LexiconEntrySchema,
      postJson("/api/v1/lexicon", LexiconCreateRequestSchema.parse(body)),
    ),

  updateLexiconEntry: (entryId: string, body: LexiconUpdateRequest): Promise<LexiconEntry> =>
    request("/api/v1/lexicon/" + encodeURIComponent(entryId), LexiconEntrySchema, {
      method: "PATCH",
      body: JSON.stringify(LexiconUpdateRequestSchema.parse(body)),
    }),

  deleteLexiconEntry: (entryId: string): Promise<void> =>
    request(`/api/v1/lexicon/${encodeURIComponent(entryId)}`, z.void(), { method: "DELETE" }),

  synthesizeOffline: (body: OfflineSynthesisRequest): Promise<OfflineSynthesisResponse> =>
    request(
      "/api/v1/synthesis/offline",
      OfflineSynthesisResponseSchema,
      postJson("/api/v1/synthesis/offline", OfflineSynthesisRequestSchema.parse(body)),
    ),
};
