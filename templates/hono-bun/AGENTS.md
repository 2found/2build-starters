# AGENTS.md

**__PROJECT_NAME__** — Bun + Hono REST API, TypeScript and Zod. One deployable
service at the repo root:

- **api** — `src/` — [docs/ARCHITECTURE-API.md](docs/ARCHITECTURE-API.md): read before
  adding a module, route, middleware, database or external service.
- **Verification** — [docs/VERIFY.md](docs/VERIFY.md): read before declaring a task done.
- **Design** — N/A: API only, no UI. Establish `DESIGN.md` and link it here before
  adding one.

## Hard Constraints

- **Layers stay layers.** `routes → use-case → repo`, composed only in the module's
  `index.ts`. Routes validate and map HTTP; use cases hold behavior and know no
  Hono or SQL; repos own data access. See
  [Layout](docs/ARCHITECTURE-API.md#layout).
- **Validate at the boundary, fail with the envelope.** Every external input is
  parsed by Zod in the route; every error is
  `{ error: { code, message, requestId } }` via `errorResponse`. Never return
  stack traces or internal messages.
- **Mount deliberately.** Product-agnostic modules mount at host root; only routes
  owned by one product surface nest under its prefix — see
  [Choosing a route mount level](docs/ARCHITECTURE-API.md#choosing-a-route-mount-level).
- **Operational data is served, never compiled into a client.** Prices, quotas,
  limits and their copy live in this API; clients render what it returns. A fee
  is quoted by the API, never computed by a client.
- **Lists are paginated and queries index-backed.** No unbounded list endpoint, no
  full scan or client-side filter over an unbounded set. User-facing search is
  fuzzy *and* index-backed (e.g. Postgres `pg_trgm` GIN over a normalized key).
- **Migrations must not rewrite a big table** once a database exists: no
  `ADD COLUMN … GENERATED … STORED`, no `NOT NULL DEFAULT <volatile>`; nullable
  column + batched backfill, and `SET lock_timeout` first — see
  [Database](docs/ARCHITECTURE-API.md#database-when-you-add-one).
- **Credentials:** never commit `.env` files, keys, tokens or database URLs; only
  `.env.example` placeholders. New env vars are declared in `src/lib/env.ts`.
- **Dev runs `bun --watch`, not `--hot`** (`--hot` keeps stale module generations).

## Run

```bash
bun install --frozen-lockfile
bun run dev                     # http://localhost:3000 (PORT overrides)
```

Bun loads a local `.env` if present; copy `.env.example` only to override defaults.
No database, secret or external service is required.

## Verify

```bash
bun run typecheck
bun run test
bun run build
```

CI ([.github/workflows/check.yml](.github/workflows/check.yml)) runs the same list.
Then probe the local API, one success and one rejection:

```bash
curl -H 'Content-Type: application/json' -d '{"name":"Ada"}' http://localhost:3000/greetings
curl -i -H 'Content-Type: application/json' -d '{"name":""}' http://localhost:3000/greetings   # 400 envelope
```

## Deploy and release

N/A until the product picks a target: there is no deploy runbook, registry or
release profile yet. When one is added, write the runbook (environments, command +
cwd, migrations, rollback) and a `RELEASE.md` profile, then link both here.

## Starter updates

Provenance lives in `.babysit/starter.lock.yaml`. Run `bbs starter check --json`
when starting work if the skill preamble has not already. A newer release is
advisory: read its upgrade guide, preserve product changes, verify, then update
the lock's `release` / `template_revision` / `revision` to what was applied. Never
copy the latest starter over the project or edit the lock to silence a notice.

## 2build

This repo is configured for 2build autonomous runs.

- Git: autopilot leaves work uncommitted; the lead commits once per phase and lands it on the base branch
- QA harness: `.babysit/qa.yaml` (API-only: verify with HTTP requests, no browser or login)
- Default run: `/goal "STATUS: DONE or STATUS: BLOCKED appears" /bbs:autopilot "<task>"`
- Search: use `rg`, never `grep`. `rg -uu` includes gitignored and hidden files; skip noise with `-g '!node_modules' -g '!.git'`. List files with `rg --files -uu`.
- Machine paths and workspace registration live in `~/.babysit/config.yaml`, never a committed `.babysit/config.yaml`. Install 2build: <https://github.com/2found/2build/blob/main/docs/install.md>.

QA must prove the local target or name the blocker, and must include at least one non-happy-path case before PASS.
