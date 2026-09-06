# AGENTS.md — Repository-Wide Engineering Rules

This file governs how any contributor (human or AI agent) works in this
repository. Read `docs/architecture.md` before making structural
changes.

## Non-negotiable constraints

1. **Monorepo.** `apps/web`, `apps/api`, `packages/*` stay in this one
   repository.
2. **Explicit contracts.** The wire format between frontend and backend
   is defined in `docs/api-contract.md` and `docs/websocket-protocol.md`
   first; code follows the doc, not the other way around. If you change
   a contract, update the doc and `schemas/` in the same change.
3. **No model logic in routers.** `apps/api/app/routers/*.py` may only:
   parse/validate request models, call a service or provider via `Depends`,
   shape the response model. Business logic belongs in
   `packages/indic_text`, `packages/tts_runtime`, `packages/audio_metrics`,
   or `apps/api/app/services/*.py` (orchestration only, still no model
   internals).
4. **No API logic in React components.** Components render and dispatch;
   all fetch/WebSocket logic lives in `apps/web/lib/api` and
   `apps/web/lib/ws`, and all cross-cutting streaming state lives in
   `apps/web/lib/store` (Zustand). A component should never call
   `fetch`/`WebSocket` directly.
5. **Dependency injection for providers.** Every NLP/TTS provider is
   constructed once in `apps/api/app/deps.py` and obtained via
   `Depends(...)`. Do not `import` a concrete mock/real provider class
   into a router or service directly — depend on the interface.
6. **Every external provider has a mock.** If you add a new provider
   interface, add a deterministic mock implementation and a unit test
   for it before wiring it into the API.
7. **Streaming sessions are stateful and explicit.** All mutable
   streaming state lives in `tts_runtime.session.StreamingSynthesisSession`.
   Do not scatter session state into router-level globals or module
   dicts outside `app/services/session_registry.py`.
8. **Session IDs and revision IDs are load-bearing.** Every session has
   a unique ID; every edit increments a revision. The browser must be
   able to discard stale-revision chunks using only data present in the
   chunk/event itself — never rely on message arrival order across
   separate event types as the sole staleness signal.
9. **No base64 for streamed PCM.** Binary audio on the WebSocket path is
   sent as raw bytes in binary frames (see `websocket-protocol.md`).
   Base64 is permitted only for the two REST endpoints that return a
   complete, bounded audio buffer in one JSON response
   (`/pronunciation/preview`, `/synthesis/offline`).
10. **Never commit model checkpoints, `.env`, or SQLite data files.**
    Check `.gitignore` before adding any new binary/data file type.
11. **No auth in the MVP.** Do not add login, sessions-as-cookies, API
    keys, or per-user scoping. If a future task requires it, it will say
    so explicitly.
12. **No new infrastructure ahead of a measured need.** Do not add
    Redis, Celery, task queues, or Kubernetes manifests speculatively.
13. **Type annotations are mandatory.** Every public Python function/method
    has full type annotations; `mypy --strict`-clean where practical (see
    `apps/api/pyproject.toml` / `packages/*/pyproject.toml` for the
    configured strictness). TypeScript runs with `strict: true`; no `any`
    without a `// justified: ...` comment.
14. **Validate all external input.** Every REST body and WebSocket client
    event is parsed through a Pydantic model (backend) or zod schema
    (frontend) before use. Reject invalid Unicode explicitly rather than
    letting it propagate.
15. **Structured errors only.** Backend errors use the envelope in
    `docs/api-contract.md`; never return a bare stack trace or an
    unstructured string body.
16. **Tests accompany logic.** New business logic (anything in
    `packages/*` or `app/services`) ships with a unit test in the same
    change. New user-facing workflow steps get at least one Playwright
    assertion if they are part of the primary workflow.
17. **Determinism in mocks.** Every mock provider must be a pure/deterministic
    function of its input (plus explicit, fixed seeds if randomness is
    used for chunk timing simulation). Conference demos and tests both
    depend on this.

## Tooling conventions

- Python: 3.12+ target, formatted/linted with `ruff`, type-checked with
  `mypy`, tested with `pytest`. Package manager: `pip` + `pyproject.toml`
  (no Poetry/PDM — keep the dependency surface small).
- TypeScript: Node 20+, `npm` workspaces, formatted/linted with `eslint`,
  type-checked with `tsc --noEmit`, unit-tested with `vitest` + React
  Testing Library, E2E-tested with `playwright`.
- Commit messages and PRs describe *why*, not just *what* — this
  repository is read by future agents who will not have this
  conversation's context.

## When you touch...

- `packages/indic_text` → run `pytest packages/indic_text`.
- `packages/tts_runtime` → run `pytest packages/tts_runtime`, and if you
  changed chunk timing/ordering, re-check
  `docs/websocket-protocol.md`'s framing section still matches.
- `apps/api` → run `pytest apps/api`, `ruff check apps/api`,
  `mypy apps/api`.
- `apps/web` → run `npm run lint -w apps/web`, `npm run typecheck -w apps/web`,
  `npm run test -w apps/web`.
- Any wire-format change → regenerate `schemas/` via
  `python scripts/export_schemas.py` and update both docs above.

## Repository structure additions beyond the original spec

- `schemas/` (top-level): shared JSON Schema, generated from backend
  Pydantic models, consumed by frontend zod schemas. Added to satisfy
  the "shared JSON schemas" constraint, which had no other assigned
  location.

Any further structural deviation from the originally requested layout
must be documented here, with a one-line rationale, in the same change
that introduces it.
