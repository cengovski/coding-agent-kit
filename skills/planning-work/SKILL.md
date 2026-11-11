---
name: planning-work
description: Use after the spec and stack are decided and before implementation, to break work into small, ordered, independently verifiable tasks in PLAN.md. Use for any task that will take more than a few commits.
---

# Planning work

## Procedure

1. Read `SPEC.md`. Every acceptance criterion must map to at least one task.
2. Write `PLAN.md` (see `templates/PLAN.md`). Each task has:
   - **Goal** — one sentence.
   - **Files** likely touched.
   - **Test first** — the test(s) that will prove it works.
   - **Verify** — the exact command(s) to run.
   - **Done when** — observable result.
3. Order tasks so the app runs end to end as early as possible ("walking skeleton"): scaffold → one thin vertical slice through UI, API, and DB → then widen.
4. Keep tasks small: one to a few commits each, reviewable in minutes. Split anything bigger.
5. Mark risky or unknown tasks and do a short spike (time-boxed, throwaway) before relying on them.
6. As you work, tick tasks off and update the plan when reality differs. The plan is a living document, not a contract.

## Example task

```
### T3 — Create task via API
Goal: POST /api/tasks persists a task for the signed-in user.
Files: src/api/tasks.ts, src/db/schema.ts, tests/api/tasks.test.ts
Test first: rejects empty title (400), creates task (201, returns id), unauthenticated (401).
Verify: npm test -- tasks && npm run typecheck
Done when: tests green; row visible in local DB.
```

## Anti-patterns

- Plans with tasks like "implement backend".
- Building every layer completely before anything runs end to end.
- Tasks without a verification command.
