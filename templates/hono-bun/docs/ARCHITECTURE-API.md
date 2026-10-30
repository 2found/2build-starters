# api — Architecture

Bun runs the API, Hono owns HTTP routing, Zod validates external input. No
database, auth, CORS policy or deploy target yet — each is an explicit decision
recorded here when added.

## Layout

- `src/index.ts` — process entry: parses env, binds `Bun.serve`. Nothing else.
- `src/app.ts` — `createApp()`: middleware, health routes, module mounts, 404 and
  error handlers. Independent of the listener, so tests call `app.request()`
  without a port.
- `src/lib/` — leaves; never import `modules/`. `env.ts` (Zod env, the only
  reader of `process.env`), `errors.ts` (`AppEnv`, `errorResponse`).
- `src/modules/<feature>/` — one folder per feature:
  - `domain.ts` — types and pure invariants; no I/O.
  - `repo.ts` — port interface + adapter(s); the only place that touches storage.
  - `use-case.ts` — `create<Verb>(repo)` factories; no Hono, no SQL.
  - `routes.ts` — `<feature>Routes(useCases)`: validate, call, map to HTTP.
  - `index.ts` — composition root, the only cross-layer importer.

  Past ~3 use cases or ~150 lines, split into `domain/`, `repo/`,
  `use-cases/<verb>-<entity>.ts`, `schema/`. A use case is a command (through
  repo + domain) or a query (may read a DTO shape directly) — never both.
- `tests/` — in-process request tests against `createApp()`, plus pure tests for
  use cases with a fake repo.

`src/modules/greetings/` is the reference module; its static repo adapter shows
where a database adapter would go without changing route or use-case contracts.

## Choosing a route mount level

Mount in `src/app.ts` with `app.route('/<prefix>', <feature>())`.

- **Host root** (`/x`) — default for anything not owned by a single product
  surface: identity, messaging, preferences, notifications, anything with a
  `product` column.
- **Under a product prefix** (`/<product>/x`) — only routes that belong to that
  product's surface.
- **Keep legacy paths** owned by an external integration (OAuth callbacks,
  payment webhooks) where the integration expects them.

Test: *would this route make sense without the product word if a second product
launched tomorrow?* Yes → host root. Don't copy a neighbour's prefix.

## Errors, request IDs and readiness

- Every response carries `x-request-id`; every error body is
  `{ error: { code, message, requestId } }` with the same ID. Use
  `errorResponse(c, status, CODE, message)`; codes are `UPPER_SNAKE`.
- Validation failures are `400 INVALID_INPUT` with a human message; malformed
  bodies are `400 INVALID_REQUEST`; unknown routes `404 NOT_FOUND`; anything
  unexpected is logged server-side with the request ID and returned as
  `500 INTERNAL_ERROR` without details.
- `/healthz` is liveness only. `/readyz` checks process readiness today; add a
  probe for each required dependency (database, queue) when one is introduced.

## Operational data belongs to the API, not to a client

Prices, quotas, limits, plan benefits and their copy are served by this API —
a shipped mobile build or cached web bundle can't change without a release.

- One owning module per kind of data; other modules import views of it, never
  retype literals (tier lists, prices) in a second place.
- Clients read it from an endpoint (e.g. `GET /app-config`) at runtime or build
  time; a generated client file is regenerated and committed with the change.
- A fee-bearing action answers a **quote** from the server (`price`, `reason`,
  what funds it, whether it can settle). Quote and charge share one function; a
  client renders the quote and never sends a price back.

## Database (when you add one)

Pick the driver, ORM and migration tool explicitly and record the choice here.
Until then the starter has no migration system to reuse.

- All access goes through the repo adapter; one query style (ORM/query builder),
  no ad-hoc string SQL at call sites.
- Migrations are generated from the schema file and committed; never hand-edit
  generated migration output.
- Every list is paginated (keyset preferred) and every query path has an index;
  user-facing text search is fuzzy *and* index-backed (Postgres: `pg_trgm` GIN
  over a normalized key, queried with `%` / `similarity()`).
- Migrations run against the live database at deploy time. On a big table never
  `ADD COLUMN … GENERATED ALWAYS AS (…) STORED`, `NOT NULL DEFAULT <volatile>`,
  most `ALTER COLUMN TYPE`, or an index whose expression de-toasts large text.
  Instead: nullable column → trigger or app write → resumable batched backfill.
  Open such migrations with `SET lock_timeout = '5s'`; a failed deploy is the
  good outcome — re-run it.
- Add the database probe to `/readyz` and a graceful shutdown that closes the pool.

## Configuration and secrets

`src/lib/env.ts` is the single Zod schema for environment variables, with local
defaults where safe and no default for secrets. Document every variable in
`.env.example` with a placeholder. Real values live in ignored `.env` files or
the deploy target's secret store.
