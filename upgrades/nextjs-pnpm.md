# nextjs-pnpm upgrade guide

## 0.2.0 — template revision 1

Initial release; no earlier version to migrate. Requires bbs 1.118.0+ (catalog
`scaffold` support): bootstrap runs `create-next-app@latest`, adds
`@tanstack/react-query`, `zod`, `vitest` and current `@types/node`, sets the `dev`/`start`/`typecheck`/`test`
scripts, then overlays the starter files.

## How subsequent releases are applied

Same contract as [hono-bun](hono-bun.md#how-subsequent-releases-are-applied):
read the lock, apply only the listed edits while preserving product changes, run
the AGENTS.md **Verify** list plus a local browser check of `/` and a 404, then
advance the lock. Framework files that came from `create-next-app` are upgraded
with Next.js's own upgrade guide, not by re-running the scaffold.
