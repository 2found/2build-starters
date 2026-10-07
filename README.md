# 2build starters

Start a project your coding agent can run, change and verify. Each starter combines
a runnable stack with architecture guidance, checks, local QA and a 2build harness.

**Status:** initial source preview. Remote bootstrap requires a published starter
release and a `bbs` release containing these commands (planned minimum: 1.95.0).
Both releases are pending. Local `--source` works with the matching CLI preview.

## Start with one agent prompt

```text
Create a new project named my-api using the hono-bun starter from 2build starters.
Use bbs bootstrap with the startup git profile; install 2build for my current agent
following https://raw.githubusercontent.com/2found/2build/main/docs/install.md if
needed. Check bbs bootstrap --help exists and that its version meets the catalog.
Read the generated AGENTS.md, verify the local API with one successful and one
rejected request, then report the starter source/version and how to run the project.
Name any missing prerequisite. Do not commit, push or deploy.
```

## Commands

Once both CLI and starter releases are published:

```bash
bbs bootstrap my-api --template hono-bun --profile startup
bbs bootstrap another-api --template hono-bun --version 0.1.0
bbs starter check --dir my-api --json
```

During local development, use a binary built from the matching 2build change:

```bash
# From the 2build checkout; inject the planned release version for this preview.
go build -ldflags '-X github.com/2found/2build/internal/cmd.version=1.95.0' -o /tmp/bbs-starters ./cmd/bbs
# From the directory containing the starter checkout:
/tmp/bbs-starters bootstrap my-api --source ./2build-starters --template hono-bun --profile startup
```

Bootstrap refuses existing targets, installs frozen dependencies, runs typecheck,
tests and build, then publishes the generated directory. Failure leaves no project
behind. `--no-verify` generates files only and reports `verified: false`; readiness
has not been proved. Git init, remotes, commits and deployment are left to the caller.

## Available starter

`hono-bun` provides Bun, Hono, TypeScript and Zod; a stateless example module;
request IDs, logging, consistent errors; health/readiness routes; tests and CI.
Bun 1.3.14+ is required. No database, auth, UI or external service is required.
The default git profile is `startup`; `pet` and `enterprise` are also supported.

`common/` owns the stack-neutral agent harness. `templates/` owns stack files.
`catalog.json` owns the release version, template revisions and command arrays.
The CLI implementation lives in `2found/2build`; skills are installed there,
never vendored into a starter.

## Knowing about updates

Every generated project commits `.babysit/starter.lock.yaml`: source, catalog
release, template ID/revision and source Git commit. Local generation records a
SHA-256 snapshot digest instead of pretending it came from a published commit.

`bbs starter check --json` compares that lock against the latest stable GitHub
release, resolving its tag to a commit before reading the catalog. It reports an
update only when both the catalog release and this template's revision are newer.
The standard 2build skill preamble performs the same advisory check. JSON-only
telemetry callers must call `starter check` themselves.

Release data is cached in machine state for 24 hours. Network failures use stale
data when available and expose a warning; failed requests are throttled for 15
minutes. `--force` refreshes it. `bbs config set update_check false` suppresses
automatic checks. Explicit checks remain available. An offline result is not a
claim that the project is current.

Updates never overwrite generated code or advance its lock. Follow the cumulative
guide in `upgrades/`, preserve product-specific changes, verify the result, and
only then record the applied source/version/revision. Package dependency updates
are separate. A newer CLI/plugin is updated with `bbs update`; it does not update
the generated application.

## Maintainers

Run `BBS_BIN=/absolute/path/to/bbs python3 tests/verify.py` from this repository.
It creates real projects, runs their frozen dependency install and checks, probes
the built local API including rejected inputs, and verifies overwrite refusal and
read-only update reporting.

CI checks the template's frozen install, typecheck, tests and build immediately.
Generated-project integration runs once the catalog's required CLI release is
published; until then that job is explicitly skipped with a workflow notice.
Use workflow dispatch to rerun it after the CLI release becomes available.

Release order: publish a 2build CLI containing these commands first, then a stable
starter `vX.Y.Z` release matching `catalog.json.version`. The starter release
workflow requires generated-project verification before publishing.
Stable tags/releases must remain immutable. Increment affected template revisions
and extend their upgrade guide for every applicable change; common harness edits
affect all templates that consume them. See AGENTS.md for the authoring contract.
