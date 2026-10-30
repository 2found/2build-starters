# AGENTS.md

**2build starters** — versioned project templates that `bbs bootstrap` turns into a
verified project already passing 2build's `harness-audit`. This repo owns starter
files and `catalog.json`; `2found/2build` owns the CLI (`internal/starter/`), the
skills and the audit contract. Never copy CLI code or skills here.

- **`catalog.json`** — release `version`, `min_cli_version`, and per template its
  `path`, integer `revision`, `summary`, `upgrade` guide, `scaffold` / `dev` / `verify`
  argv arrays (no shell; `__PROJECT_NAME__` is substituted).
- **`common/`** — stack-neutral files copied into every project: `CLAUDE.md`
  (points at AGENTS.md), `docs/VERIFY.md`, `.gitignore`, `LICENSE`.
- **`templates/<id>/`** — stack files plus the project's own `AGENTS.md` (the
  entrypoint is stack-specific: service map, Run, Verify):
  - `hono-bun` — Bun + Hono API, files vendored here. Architecture:
    [templates/hono-bun/docs/ARCHITECTURE-API.md](templates/hono-bun/docs/ARCHITECTURE-API.md).
  - `nextjs-pnpm` — Next.js web app; `scaffold` runs `create-next-app@latest` at
    bootstrap and this folder is only the overlay. Architecture:
    [templates/nextjs-pnpm/docs/ARCHITECT-WEB.md](templates/nextjs-pnpm/docs/ARCHITECT-WEB.md);
    design: [templates/nextjs-pnpm/DESIGN.md](templates/nextjs-pnpm/DESIGN.md).
- **`upgrades/<id>.md`** — cumulative, actionable upgrade guide per template.
- **`tests/`** — `harness.py` (harness-audit contract), `verify.py` (real
  generation + live probes), `test_release.py` (publication guards).

Both template docs are seeded from the Lohi reference docs (`docs/ARCHITECTURE-API.md`,
`docs/ARCHITECT-WEB.md` in kiem-lai): carry over rules that transfer to any product,
never Lohi-specific paths, products or numbers.

## Hard Constraints

- **A generated project must pass `harness-audit` as-is.** Its `AGENTS.md` links
  the architecture doc and `docs/VERIFY.md`; links `DESIGN.md` when there is a UI
  (or states Design N/A); has **Run** and **Verify** blocks identical to the
  catalog `verify` list, CI and `.babysit/qa.yaml` `check`; states deploy/release
  as an owner link or explicit N/A; carries the `## 2build` pointer bullets from
  2build's `setup-project/references/project-pointers.md` (browser bullets only for
  UI templates) and the closing QA sentence. `tests/harness.py` enforces this —
  extend it rather than weakening it when the 2build contract changes.
- **Collisions.** `common/` and a template must not share a path (generation
  fails). Starter files may replace scaffold output; that is how the overlay
  owns `AGENTS.md`, `README.md`, `.gitignore` and the app shell.
- **`__PROJECT_NAME__` is the only token.** It applies to file contents and
  `scaffold` arguments.
- **Secrets:** only `.env.example` ships. A `.env*` file or a
  `.babysit/starter.lock.yaml` in the source is rejected by the generator.
- **Docs describe what the code does.** A rule in a template doc needs code that
  follows it (e.g. `lib/query/client.ts` defaults, `errorResponse`) or is
  explicitly framed as "when you add X". No dangling links, no invented deploy
  targets: the starters have no database, auth, UI kit or deploy dependency.
- **Revisions.** Increment a template's `revision` whenever its files, its
  `scaffold`/`verify` arrays or the `common/` files it consumes change; leave
  unaffected templates alone so their projects get no notice. Add the matching
  entry to `upgrades/<id>.md`; projects own generated code, so upgrades preserve
  local changes.
- **Dependencies.** Vendored templates bump versions only with a regenerated,
  committed lockfile (`bun.lock`). Scaffolded templates resolve `@latest` at
  bootstrap and the generated lockfile records what was used.
- **CLI capability gates the catalog.** A catalog using a new generator feature
  (e.g. `scaffold`, CLI 1.118.0+) raises `min_cli_version`; publish that 2build
  release first.

## Run

```bash
# From the directory containing this checkout, with an installed bbs:
bbs bootstrap my-api --source ./2build-starters --template hono-bun
bbs bootstrap my-web --source ./2build-starters --template nextjs-pnpm
```

Bootstrap refuses an existing target, runs `scaffold`, overlays `common/` +
template, runs `verify`, then publishes; failure leaves nothing behind. To test an
unreleased CLI, build it from 2build:
`go build -ldflags "-X github.com/2found/2build/internal/cmd.version=<X.Y.Z>" -o /tmp/bbs ./cmd/bbs`.

## Verify

```bash
python3 tests/harness.py                                    # static contract, no bbs needed
python3 tests/test_release.py                               # release guards
BBS_BIN=/absolute/path/to/bbs python3 tests/verify.py       # real generation + live probes
```

`verify.py` needs Bun 1.3.14+, Node.js 22+, pnpm 10+, registry access and a `bbs`
meeting `min_cli_version`. It generates every template, runs its checks, applies
`harness.py` to the real output, probes the running app (API: success, 400s, 404;
web: home page, 404 page) and checks overwrite refusal and read-only update
reporting. CI ([.github/workflows/check.yml](.github/workflows/check.yml)) runs all
three; integration waits until the required CLI release exists.

## Release

Bump `catalog.json.version` and push to `main`. CI verifies, creates the stable
`vX.Y.Z` tag on the verified commit and publishes the GitHub release
([scripts/release.sh](scripts/release.sh)). Retry via workflow dispatch on `main`;
never move a published tag; a manual tag push must match the catalog and the
verified commit. Full order and caveats: [README.md](README.md#maintainers).

## 2build

- Git: autopilot leaves work uncommitted; the lead commits once per phase and lands it on `main`
- QA: no app runs from this repo; the **Verify** list above is the check path (generated projects carry their own `.babysit/qa.yaml`)
- Default run: `/goal "STATUS: DONE or STATUS: BLOCKED appears" /bbs:autopilot "<task>"`
- Search: use `rg`, never `grep`. `rg -uu` includes gitignored and hidden files; skip noise with `-g '!node_modules' -g '!.git'`. List files with `rg --files -uu`.

QA must prove the local target or name the blocker, and must include at least one non-happy-path case before PASS.
