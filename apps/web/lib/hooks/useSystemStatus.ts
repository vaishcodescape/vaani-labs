"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api/client";
import type { ModelsResponse, SystemResponse } from "@/lib/schemas/system";

interface SystemStatusState {
  system: SystemResponse | null;
  models: ModelsResponse | null;
  loading: boolean;
  error: string | null;
}

export function useSystemStatus() {
  const [state, setState] = useState<SystemStatusState>({
    system: null,
    models: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;
    Promise.all([api.system(), api.models()])
      .then(([system, models]) => {
        if (!cancelled) setState({ system, models, loading: false, error: null });
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setState({
            system: null,
            models: null,
            loading: false,
            error: err instanceof Error ? err.message : "Failed to reach backend.",
          });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}
