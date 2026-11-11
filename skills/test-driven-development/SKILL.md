---
name: test-driven-development
description: Use for any new behavior or bug fix. Write a failing test that describes the behavior, watch it fail for the right reason, write the minimum code to pass, then refactor. Use when adding features, fixing bugs, or changing logic.
---

# Test-driven development

## The loop: red → green → refactor

1. **Red.** Write one small test for the next piece of behavior. Run it. It must **fail**, and fail for the expected reason (assertion, not a typo or import error). A test you never saw fail proves nothing.
2. **Green.** Write the simplest code that makes it pass. Run the test again.
3. **Refactor.** Clean up names and duplication with tests green. Run the suite again.
4. Repeat with the next behavior.

For a bug: first write a test that reproduces it (red), then fix (green). Keep the test as a regression guard.

## What to test

- **Behavior through public interfaces** (function inputs/outputs, HTTP responses, rendered UI) — not private implementation details.
- The happy path, each validation rule, boundaries (empty, zero, max, unicode), and each documented error.
- One reason to fail per test; descriptive names: `rejects_task_with_empty_title`.

## Test layers

| Layer | Tool (default) | Scope |
|---|---|---|
| Unit | Vitest / pytest | Pure logic, fast, no network |
| Integration | Vitest / pytest + real DB (container or SQLite) | Modules together, API handlers, queries |
| E2E | Playwright | Critical user flows in a real browser (see `e2e-testing-playwright`) |

Most tests are unit/integration; E2E covers the flows that would embarrass you if broken.

## Rules

- Do not mock what you own; mock only slow or external boundaries (payment, email, third-party APIs). Prefer fakes over deep mock chains.
- Tests must be deterministic: control time, randomness, and network. No `sleep` to wait for things.
- Never delete, skip, or weaken a test to make it pass. If a test is wrong, explain why in the commit.
- Keep the whole suite fast enough to run on every change.
- Run the exact test command and read the output; report the pass/fail counts.
