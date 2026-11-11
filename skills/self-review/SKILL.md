---
name: self-review
description: Use before declaring work done or opening a PR. A structured critical review of your own diff against the spec — correctness, tests, security, scope, and readability — performed as if by a skeptical reviewer who did not write it.
---

# Self-review

Review the diff as a stranger would. Your goal is to find problems, not to defend the code.

## Procedure

1. Get the full diff: `git diff main...HEAD` (or staged changes). Read every line.
2. Re-read `SPEC.md` / the task. Then check, in order:

**Correctness**
- [ ] Every acceptance criterion is implemented — point to the code and the test for each.
- [ ] Edge cases: empty, null, duplicates, large input, concurrent requests, time zones, unicode.
- [ ] Errors are handled at boundaries and shown to users clearly.

**Tests**
- [ ] New behavior has tests that would fail without the change.
- [ ] No skipped, weakened, or deleted tests; no snapshot updates accepted blindly.
- [ ] E2E covers the changed user flow if there is a UI.

**Security** (see `security-and-secrets`)
- [ ] No secrets or tokens; inputs validated; authz checked on the server.

**Scope and simplicity**
- [ ] No unrelated changes, dead code, debug logs, commented-out code, or speculative abstractions.
- [ ] No new dependency without a reason stated in the PR.
- [ ] Every library API used is verified against current docs.

**Readability**
- [ ] Names are clear; complex parts have a short *why* comment.
- [ ] README / `.env.example` / docs updated.

3. Fix what you found, rerun checks, and re-review the changed parts.
4. If a fresh reviewer is available (a subagent or second session with read-only access), ask it to review the diff against `SPEC.md` and report only correctness gaps, not style. Treat its findings as input, not orders: fix real issues, decline style nitpicks that add complexity.
5. In your final report, list anything you consciously left out.
