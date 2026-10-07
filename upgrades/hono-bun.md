# hono-bun upgrade guide

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
