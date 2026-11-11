---
name: implementation-discipline
description: Use whenever you write or change code. Enforces small steps, minimal diffs, no speculative code, and keeping the project runnable after every step.
---

# Implementation discipline

## Rules

1. **Read before you write.** Look at nearby code, existing helpers, and conventions. Reuse instead of duplicating.
2. **One logical change at a time.** Make it, run the relevant checks, commit. Then the next one.
3. **Keep it runnable.** After every step the app builds and existing tests pass. If you break something, fix it before moving on.
4. **No speculative code.** Do not add options, abstractions, plugins, or config "for later". YAGNI. Three similar lines beat a premature abstraction.
5. **No unrequested scope.** Refactors, renames, and dependency upgrades go in separate, explicitly motivated commits — or are noted as follow-ups.
6. **Delete, don't comment out.** Git remembers.
7. **Name things for the reader.** Clear names over comments; comments explain *why*, not *what*.
8. **Handle the unhappy path** at boundaries (see `error-handling-and-config`), not with try/catch everywhere.
9. **Check every API you call** against current docs if you are not certain (see `current-docs-lookup`).
10. **Stop and rethink** after two failed attempts at the same thing. Re-read the error, the docs, and your assumptions instead of trying a third variation blindly.

## Per-step loop

```
pick next task in PLAN.md
→ write/adjust a failing test (test-driven-development)
→ write the minimum code to pass
→ run: tests for this area + typecheck + lint
→ refactor if needed, rerun
→ commit with a clear message
```

## Smells to catch in your own diff

- Files changed that have nothing to do with the task.
- New dependency for something the standard library or an existing dep already does.
- `any`, broad `except:`, disabled lint rules, skipped tests, `TODO` without an owner.
- Magic numbers/strings that belong in config or constants.
