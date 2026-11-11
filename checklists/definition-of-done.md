# Definition of Done

Show evidence (commands + results) for each item.

## Product
- [ ] Every acceptance criterion in SPEC.md is met.
- [ ] Each criterion has at least one automated test.
- [ ] Loading, empty, error, and success states exist for every data view.

## Quality
- [ ] Clean install works (`npm ci` / `uv sync` / `pip install -r ...`).
- [ ] Lint clean. Typecheck clean.
- [ ] Unit + integration tests pass (counts reported, none skipped without reason).
- [ ] E2E tests pass headless for every critical UI flow.
- [ ] Build succeeds; the app starts and the main flow works when run.

## Safety
- [ ] No secrets in code, tests, docs, or git history of this change.
- [ ] `.env.example` lists every variable; `.env` is gitignored.
- [ ] Server-side input validation and authorization checks, with tests for the unauthorized case.
- [ ] Dependency audit has no unaddressed high/critical issues.

## Delivery
- [ ] README: setup, run, test, deploy — copy-pasteable.
- [ ] Self-review done on the full diff; findings fixed.
- [ ] Commits are focused with clear messages; PR/summary lists what changed, how verified, and what is left.
