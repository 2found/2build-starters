# Frontend Architecture — __PROJECT_NAME__

Next.js App Router, React, Tailwind v4, TanStack Query, Zod; Node.js + pnpm.
Framework files (`next.config.ts`, `tsconfig.json`, `eslint.config.mjs`) come from
`create-next-app`; tokens live in `app/globals.css` (read [DESIGN.md](../DESIGN.md)
first).

## Module Layout Convention

`app/` holds only route files — `page.tsx`, `layout.tsx`, `not-found.tsx`, route
handlers — each a thin re-export or a few lines of composition. Feature code lives
in `modules/`:

- `modules/shared/` — primitives used across features (`shared/ui/` components).
- `modules/app/` — global providers and app-wide state.
- `modules/<route>/` — **route folders mirror URL segments exactly**, each owning a
  `page.tsx` section component exported via `index.ts`, with `models/`, `hooks/`,
  `lib/{utils,api}/` and `components/` beside it.

Examples: `/` → `modules/home/page.tsx`; `/settings/profile` →
`modules/settings/profile/page.tsx`; `/posts/[slug]` → `modules/posts/[slug]/page.tsx`.
Use `[slug]` / `[id]` folders directly; no `detail/` unless it is in the URL.
Query-param UI (sheet, drawer, modal, tabs) lives under the owning route folder,
not as a fake segment. A sheet opened from several routes belongs in
`components/`.

Size targets: `page.tsx` and leaf components ≤ 150 lines, `lib/utils` / `models`
≤ 100, `hooks` ≤ 200; split past 200, named after what it does.

`lib/` is for framework-free leaves: `env.ts` (Zod env), `api.ts` (`apiFetch`,
`ApiError`), `query/` (client defaults and keys). It never imports `modules/`.

## Data fetching

- **Server components** read through `apiFetch` (`lib/api.ts`). It maps the API's
  `{ error: { code, message, requestId } }` envelope to `ApiError`. Don't add a
  second fetch wrapper.
- **Client components** wrap the same calls in TanStack Query hooks under the
  feature's `hooks/`.
- Validate untrusted response shapes with Zod at the feature's `lib/api/` boundary
  when the API is not under your control.
- Operational data — prices, quotas, limits, plan benefits and their copy — is
  served by the API. A client renders it and never hardcodes, recomputes or sends
  a price back. Generated client files (if any) are regenerated and committed with
  the API change.

## State Management

Server state in `hooks/` (TanStack Query); auth/session in one app-wide store
under `modules/app/` when auth is added; UI-local and form state in `useState`.
Never copy server responses into a global store.

## Cacheable pages render the same bytes for every viewer

A page that may be cached (by Next, a CDN, or both) renders **identical output for
guest and member**. Viewer-dependent data — entitlement, saved state, progress,
plan — is a client island that fetches after hydration.

- A cacheable server component never reads identity: no `cookies()`, `headers()`
  or forwarded auth. Reading them silently turns the route dynamic, and a CDN rule
  that ignores that leaks one viewer's page to another.
- Pages whose content genuinely depends on the viewer (account, inbox, admin)
  read identity on the server, forward it to the API, and are excluded from any
  shared cache by path.
- When an edge cache is introduced, its allowlist has one owner (a module plus the
  CDN rule that mirrors it) and a test keeps the two in sync; freshness after an
  edit comes from purge on write, not a short TTL. Record it here.

## TanStack Query — client-only, and its defaults are load limits

`lib/query/` serves client components only. Server-rendered pages stay RSC via
`apiFetch`; no `HydrationBoundary` on cacheable pages.

- Defaults in `lib/query/client.ts` (`refetchOnWindowFocus: false`, `staleTime:
  60s`, no 4xx retry) exist because read amplification takes APIs down. Fresher
  data is a per-query opt-in, never a global change.
- Keys only from `qk` (`lib/query/keys.ts`).
- Polling with a high-water mark (chat deltas, job progress) is a dedicated hook,
  not a refetch interval on a list query.
- Login/logout should be full document loads, which discard viewer-scoped cache.
  **An SPA-style login/logout must call `queryClient.clear()`.**

## Search and lists

User-facing search is fuzzy and served by an API index; never `.includes()` over a
client-side list of unbounded size. Lists render pages from the API (cursor or
page params in the URL) instead of fetching everything and slicing.

## Configuration

`lib/env.ts` is the single Zod schema for server env (`API_URL`). Anything exposed
to the browser must be `NEXT_PUBLIC_*`, is public by definition, and is added to the
schema and `.env.example`. Never put a secret in a `NEXT_PUBLIC_*` variable.
