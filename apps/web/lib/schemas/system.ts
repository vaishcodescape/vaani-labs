import { z } from "zod";

export const HealthResponseSchema = z.object({
  status: z.string(),
  version: z.string(),
});
export type HealthResponse = z.infer<typeof HealthResponseSchema>;

export const SystemResponseSchema = z.object({
  status: z.string(),
  version: z.string(),
  uptime_seconds: z.number(),
  providers: z.record(z.string(), z.string()),
  active_sessions: z.number(),
  lexicon_entry_count: z.number(),
});
export type SystemResponse = z.infer<typeof SystemResponseSchema>;

export const ModelInfoSchema = z.object({
  id: z.string(),
  kind: z.string(),
  is_default: z.boolean(),
});
export const ModelsResponseSchema = z.object({
  acoustic_models: z.array(ModelInfoSchema),
  vocoders: z.array(ModelInfoSchema),
});
export type ModelsResponse = z.infer<typeof ModelsResponseSchema>;

export const VoiceInfoSchema = z.object({
  id: z.string(),
  language: z.string(),
  label: z.string(),
  gender: z.string(),
});
export type VoiceInfo = z.infer<typeof VoiceInfoSchema>;
export const VoicesResponseSchema = z.object({ voices: z.array(VoiceInfoSchema) });
export type VoicesResponse = z.infer<typeof VoicesResponseSchema>;

export const LanguageInfoSchema = z.object({
  code: z.string(),
  name: z.string(),
  script: z.string(),
});
export type LanguageInfo = z.infer<typeof LanguageInfoSchema>;
export const LanguagesResponseSchema = z.object({ languages: z.array(LanguageInfoSchema) });
export type LanguagesResponse = z.infer<typeof LanguagesResponseSchema>;
