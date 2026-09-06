"use client";

import { useSessionStore } from "@/lib/store/sessionStore";
import { scriptColorClasses } from "@/components/studio/scriptColors";
import type { TokenType } from "@/lib/schemas/text";

const DISPLAYED_TYPES: TokenType[] = ["word", "number", "date", "abbreviation"];

export function TokenChips() {
  const tokens = useSessionStore((state) => state.tokens);
  const selectedTokenIndex = useSessionStore((state) => state.selectedTokenIndex);
  const selectToken = useSessionStore((state) => state.selectToken);

  const visible = tokens.filter((t) => DISPLAYED_TYPES.includes(t.token_type));

  if (visible.length === 0) {
    return <p className="text-sm text-slate-400">Analyse some text to see token chips here.</p>;
  }

  return (
    <div className="flex flex-wrap gap-1.5" role="group" aria-label="Analysed tokens">
      {visible.map((token) => {
        const selected = selectedTokenIndex === token.index;
        return (
          <button
            key={token.index}
            onClick={() => selectToken(selected ? null : token.index)}
            aria-pressed={selected}
            title={`${token.script} · ${token.language} · normalized: ${token.normalized}`}
            className={`focus-ring group relative rounded-md border px-2 py-1 text-sm transition-shadow ${scriptColorClasses(
              token.script,
            )} ${selected ? "ring-2 ring-sky-500" : ""} ${
              token.pronunciation.is_uncertain ? "border-b-2 border-b-amber-500 border-dashed" : ""
            }`}
          >
            <span>{token.surface}</span>
            <span className="ml-1.5 align-super text-[9px] font-semibold uppercase text-current/70">
              {token.language}
            </span>
            {token.pronunciation.is_uncertain && (
              <span
                className="ml-1 inline-block h-1.5 w-1.5 rounded-full bg-amber-500 align-middle"
                aria-label="Uncertain pronunciation"
                title="Uncertain pronunciation"
              />
            )}
          </button>
        );
      })}
    </div>
  );
}
