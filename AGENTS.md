# 2build starters

This repository owns starter files and the catalog. `2found/2build` owns the
`bbs bootstrap` / `bbs starter check` implementation. Do not copy CLI or skills here.

- `common/` is copied into every generated project; keep its rules stack-neutral.
- `templates/<id>/` adds runnable stack files. Common/template file collisions fail.
- Use `__PROJECT_NAME__` and `__GIT_PROFILE__` for substitutions. These are the only tokens.
- Keep secrets out of source. Only `.env.example` is shipped; real env files are ignored.
- Update `catalog.json.version` for a release. Stable tags are `vX.Y.Z` and must match it.
- Increment a template's integer `revision` when its files change. Common harness
  changes increment every affected template revision. An unrelated template release
  must not notify projects whose template revision is unchanged.
- Keep cumulative, actionable upgrade instructions in `upgrades/<id>.md`.
  Projects own generated code; upgrades must preserve local changes.
- Verify the generated output, not just the template tree: run
  `BBS_BIN=/absolute/path/to/bbs python3 tests/verify.py`. The binary must support
  bootstrap and meet `catalog.json.min_cli_version`; Bun is required.
- Do not bump dependency versions without generating and committing `bun.lock`.
- This starter has no UI, database, authentication or deployment dependency.
  Add those through an explicit stack/template decision rather than the common harness.
