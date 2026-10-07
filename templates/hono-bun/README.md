# __PROJECT_NAME__

Bun/Hono API created with 2build starters. Read AGENTS.md before changing code.
Requires Bun 1.3.14 or later. No database, secret or external service is required.

```bash
bun install --frozen-lockfile
bun run dev
```

The API defaults to http://localhost:3000. Bun loads a local `.env` if present;
copy `.env.example` only if you need to override the defaults.

```bash
curl http://localhost:3000/healthz
curl -H 'Content-Type: application/json' -d '{"name":"Long","locale":"vi"}' http://localhost:3000/greetings
curl -H 'Content-Type: application/json' -d '{"name":""}' http://localhost:3000/greetings
```

The last request must return 400 with the standard error envelope.

```bash
bun run typecheck
bun run test
bun run build
bun run start
```

Stop the dev server before `start`; both use the same port. `start` runs the built
bundle. Architecture and verification contracts live in `docs/`.

Starter source/version: `.babysit/starter.lock.yaml`. `bbs starter check --json`
reports newer relevant releases without changing this project. Dependency updates
are reviewed separately through package.json and bun.lock.
