# hono-bun upgrade guide

## 0.2.0 — template revision 2

Harness only; no application code changed. Brings the entrypoint to the 2build
`harness-audit` contract.

- `AGENTS.md` is now template-owned (it moved out of `common/`). If yours is
  unmodified, take the new file. Otherwise add, keeping your own rules: a doc map
  linking `docs/ARCHITECTURE-API.md` and `docs/VERIFY.md` and stating Design N/A;
  **Hard Constraints**; **Run** and **Verify** command blocks matching
  `package.json`; a **Deploy and release** section (N/A until a target exists);
  the `## 2build` bullets (Git, QA harness, Default run, Search) and the closing
  QA sentence.
- `docs/ARCHITECTURE.md` → `docs/ARCHITECTURE-API.md` (`git mv`), extended with
  route mount levels, error/readiness rules, operational data, database and
  migration rules. Update any links to the old name.
- `docs/VERIFY.md` reads its check list from AGENTS.md and adds UI guidance.
- `.gitignore` adds `.next/`, `out/`, `coverage/`, `next-env.d.ts`,
  `*.tsbuildinfo`, `.DS_Store`.
- `README.md` and `.babysit/qa.yaml` notes link the new doc names.

Verify: `bun run typecheck && bun run test && bun run build`, then one successful
and one rejected `POST /greetings` against the local API.

## 0.1.0 — template revision 1

Initial release; no earlier version to migrate.

## How subsequent releases are applied

This guide must retain instructions for every supported older template revision.
Each release entry names changed files, concrete edits, breaking behavior and
verification commands. New catalog releases that do not affect hono-bun keep its
template revision unchanged and require no project update.

For an existing project:

1. Read `.babysit/starter.lock.yaml` and identify its release/template revision.
2. Inspect upstream changes and these instructions from that revision to the
   target release. Preserve product-specific edits; do not replace entire files.
3. Apply relevant code/harness changes. Run README.md checks and successful plus
   rejected requests against the local API.
4. Only after verification, update the lock's `release`, `template_revision` and
   `revision` to the applied release and resolved Git commit. Retain source and ID.

An update notice or newer CLI does not mean an application migration was applied.
