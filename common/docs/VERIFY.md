# Verification

Run the checks documented in README.md. For API changes, use in-process request
tests for business/error behavior, then start the local target declared in
`.babysit/qa.yaml` and probe both a successful and a rejected request. API-only
projects do not need browser QA.

Record commands and outcomes in the handoff. A missing runtime, service or secret
is a named blocker; skipping a required check is not PASS. Never use a production
endpoint to stand in for the local target.
