---
name: systematic-debugging
description: Use when a test fails, a build breaks, an error appears, or behavior differs from expectations. Find the root cause with evidence before changing code; avoid guess-and-check fixes.
---

# Systematic debugging

## Procedure

1. **Read the error fully.** The whole message, stack trace, and the first failure (later ones are often consequences). Note file and line.
2. **Reproduce reliably.** Smallest command or test that shows the problem. If you can't reproduce it, you can't know you fixed it.
3. **Check what changed.** `git diff`, `git log -p`, recent dependency or config changes. A working → broken transition narrows the search fast (`git bisect` for bigger ranges).
4. **Form one hypothesis** that explains *all* the symptoms. Write it down.
5. **Test the hypothesis** with the cheapest experiment: a log line, a debugger breakpoint, a focused unit test, printing the actual value. Change one variable at a time.
6. **Fix the root cause**, not the symptom. Ask "why" until you reach something you control.
7. **Lock it in** with a regression test that failed before the fix and passes after.
8. **Clean up** debug logs and temporary code. Run the full check suite.

## Rules

- Do not change code you don't understand to "see if it helps".
- After two failed fixes, stop. Re-read the error, the docs (`current-docs-lookup`), and question your assumptions (versions, env vars, which file is actually loaded, cached builds).
- Never "fix" a failure by deleting the test, catching and ignoring the error, adding a sleep, or adding retries to mask a race.
- Keep notes of what you tried; report them if you escalate to the human.

## Common root causes

Wrong version/API (check docs) · missing or wrong env var · stale build/cache · async race or missing `await` · off-by-one / null / empty input · time zones · path or working-directory assumptions · test pollution from shared state.
