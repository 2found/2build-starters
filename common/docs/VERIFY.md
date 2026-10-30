# Verification

Run the checks listed under **Verify** in [AGENTS.md](../AGENTS.md); CI runs the
same list. Then prove the change on the local target declared in
`.babysit/qa.yaml` — never a hosted or production URL standing in for it.

- **API change:** in-process request tests own business and error behavior; then
  start the local API and probe one successful and one rejected request (bad
  input, unknown route or missing resource), checking the error envelope and
  request ID.
- **UI change:** drive the local page with `/bbs:browse` (or `/bbs:qa` for a full
  loop): the changed flow, plus an empty, error or not-found state, and the
  console. Close the browser with the tool's own close when done.

Every PASS includes at least one non-happy-path case. Record commands and
outcomes in the handoff. A missing runtime, service or secret is a named
blocker; a skipped required check is not PASS.
