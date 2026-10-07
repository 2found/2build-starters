# Architecture

Bun runs the API; Hono owns HTTP routing; Zod validates external inputs. Development
uses `bun --watch` for process restarts. `src/app.ts` is independent of the listener
so request tests can exercise the real app without binding a port.

The sample module follows `routes → use-case → repo`, with domain types shared by
the module. `index.ts` composes its dependencies. Routes validate and map HTTP;
use cases implement behavior; repos own data access. The static greetings adapter
is intentionally stateless and needs no database or credentials.

For a new feature, add `src/modules/<feature>/` and mount it in `src/app.ts`. Choose
the route namespace from product ownership rather than copying another product.
Reuse `errorResponse` and request validation conventions. Keep list endpoints
paginated. If a database is needed, select its adapter/migration workflow explicitly
and keep queries index-backed; this starter has no migration system to reuse.

Every error has `{ error: { code, message, requestId } }`. Responses include an
`x-request-id` header. Unexpected details are logged server-side, never returned.
`/readyz` currently checks process readiness only; add required dependency probes
when introducing external services. There is no auth, CORS policy or deployment
target until the product requires and configures one.
