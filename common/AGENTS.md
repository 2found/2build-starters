# __PROJECT_NAME__

Read [architecture](docs/ARCHITECTURE.md) before changing module boundaries and
[verification](docs/VERIFY.md) before declaring a task done. README.md owns the
install, dev and check commands for this stack.

- Read nearby code and reuse its conventions before adding helpers.
- Keep domain/use-case logic out of routes and persistence behind repo boundaries.
- Validate external inputs at the boundary; use the existing error envelope.
- Keep list endpoints paginated and queries bounded by indexes when adding a database.
- Commit placeholders only; real secrets belong in ignored local env files.
- Include a non-happy-path case in verification and report any missing environment.
- Before a UI change, establish DESIGN.md and reuse the project's components/tokens.

## 2build

Git policy: `.babysit/git-flow.yaml`. Local QA target/checks: `.babysit/qa.yaml`.
Use the installed 2build skills for planning, implementation, review and QA;
install instructions: https://github.com/2found/2build/blob/main/docs/install.md.

Starter provenance lives in `.babysit/starter.lock.yaml`. Run `bbs starter check
--json` when starting work if the skill preamble has not already checked. A new
release is advisory: read its guide, preserve product changes, verify, then update
the lock's release/template_revision/revision to the applied release. Never copy
the latest starter over the project or change the lock merely to silence a notice.

Machine paths/workspace registration stay in `~/.babysit/config.yaml`, never a
committed `.babysit/config.yaml`. No git remote or release policy is implied by creation.
