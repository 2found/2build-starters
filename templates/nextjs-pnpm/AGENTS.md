# AGENTS.md

**__PROJECT_NAME__** — Next.js web app (App Router, React, Tailwind v4, TanStack
Query), Node.js + pnpm. One deployable service at the repo root:

- **web** — `app/`, `modules/`, `lib/` — [docs/ARCHITECT-WEB.md](docs/ARCHITECT-WEB.md):
  read before adding a route, module, data fetch, cache or global state.
- **Design** — [DESIGN.md](DESIGN.md): read before any visual or UI change.
- **Verification** — [docs/VERIFY.md](docs/VERIFY.md): read before declaring a task done.

Next.js changes quickly: before using a framework API you are unsure of, read the
matching guide in `node_modules/next/dist/docs/` for the installed version.

## Hard Constraints

- **Route folders mirror the URL.** `app/` files stay thin; feature code lives in
  `modules/<route>/` — see
  [Module Layout Convention](docs/ARCHITECT-WEB.md#module-layout-convention).
- **Tokens only.** Colors, radii and fonts are defined once in `app/globals.css`;
  reuse `modules/shared/ui/` before building a component. Never hardcode a hex,
  radius or font.
- **Cacheable pages are viewer-independent.** A server component that may be
  cached never reads `cookies()`, `headers()` or forwarded auth; viewer state is
  a client island — see
  [Cacheable pages](docs/ARCHITECT-WEB.md#cacheable-pages-render-the-same-bytes-for-every-viewer).
- **TanStack Query is client-only and its defaults are load limits.** Server
  pages fetch via `apiFetch`; never loosen `lib/query/client.ts` globally; keys
  come from `qk`; an SPA-style login/logout must `queryClient.clear()`.
- **Operational data is served, never compiled into the client.** Prices, quotas,
  limits and their copy come from the API; a fee is quoted by the API and only
  rendered here.
- **Search is fuzzy and index-backed in the API**; never filter an unbounded list
  in the browser.
- **Credentials:** never commit `.env*` files or secrets; only `.env.example`
  placeholders. Nothing secret goes in `NEXT_PUBLIC_*`.
- **pnpm only** for this app; keep `pnpm-lock.yaml` committed and in sync.

## Run

```bash
pnpm install --frozen-lockfile
pnpm dev                        # http://localhost:3100 (PORT overrides)
```

The app renders without a backend. `API_URL` (default `http://localhost:3000`,
the hono-bun starter) is read by `apiFetch`; copy `.env.example` to `.env.local`
to override it.

## Verify

```bash
pnpm run lint
pnpm run typecheck
pnpm test
pnpm run build
```

CI ([.github/workflows/check.yml](.github/workflows/check.yml)) runs the same list.
UI changes are then checked in a real browser on the local target with
`/bbs:browse`, including a not-found or error state.

## Deploy and release

N/A until the product picks a target: there is no deploy runbook, hosting config
or release profile yet. When one is added, write the runbook (environments,
command + cwd, rollback, any CDN cache rules) and a `RELEASE.md` profile, then
link both here.

## Starter updates

Provenance lives in `.babysit/starter.lock.yaml`. Run `bbs starter check --json`
when starting work if the skill preamble has not already. A newer release is
advisory: read its upgrade guide, preserve product changes, verify, then update
the lock's `release` / `template_revision` / `revision` to what was applied. Never
copy the latest starter over the project or edit the lock to silence a notice.

## 2build

This repo is configured for 2build autonomous runs.

- Git: autopilot leaves work uncommitted; the lead commits once per phase and lands it on the base branch
- QA harness: `.babysit/qa.yaml`
- Browser: for any UI check — open a URL, click a flow, read console errors, screenshot — invoke `/bbs:browse` (or `/bbs:qa` for a full loop). These drive a real Chromium via `agent-browser`; there is no separate browser *tool* to look for, and `WebFetch` is not a substitute. One-time: `npm install -g agent-browser cloakbrowser`.
- Browser hygiene: automation uses its own browser (Chrome for Testing, Playwright or cloakbrowser), never the installed Chrome. End every browser run with the tool's own close (`agent-browser --session "$AGENT_BROWSER_SESSION" close`), never `kill`/`pkill`/`close --all`, and check what still uses a stale browser or profile clone before reaping it. See `/bbs:browse` § Browser hygiene.
- Default run: `/goal "STATUS: DONE or STATUS: BLOCKED appears" /bbs:autopilot "<task>"`
- Search: use `rg`, never `grep`. `rg -uu` includes gitignored and hidden files; skip noise with `-g '!node_modules' -g '!.git' -g '!.next'`. List files with `rg --files -uu`.
- Machine paths and workspace registration live in `~/.babysit/config.yaml`, never a committed `.babysit/config.yaml`. Install 2build: <https://github.com/2found/2build/blob/main/docs/install.md>.

QA must prove the local target or name the blocker, and must include at least one non-happy-path case before PASS.
