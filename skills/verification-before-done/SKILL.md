---
name: verification-before-done
description: Use before claiming any task is done, fixed, working, or passing. Requires running real checks in this session and reporting the evidence. Use right before handing off, opening a PR, or answering "is it done?".
---

# Verification before done

"It should work" is not evidence. Run it.

## Procedure

1. **Map criteria to evidence.** For each acceptance criterion in `SPEC.md` (or the task), name the test or manual check that proves it.
2. **Run from clean where feasible:**
   ```
   <install>        # e.g. npm ci  |  uv sync  |  pip install -r requirements.txt
   <lint>           # e.g. npm run lint  |  ruff check .
   <typecheck>      # e.g. npm run typecheck  |  mypy . / pyright
   <unit+integration tests>
   <build>          # e.g. npm run build
   <e2e>            # e.g. npx playwright test   (required when there is a UI)
   ```
3. **Actually run the app** and exercise the main flow once (start the server, hit the endpoint, open the page, or let the E2E suite do it). Check the console and server logs for errors.
4. **Read the output.** Do not stop at the exit code; confirm the expected tests ran (count > 0, none skipped unexpectedly).
5. **Report evidence**: the commands, pass/fail counts, and anything you could not verify and why.

## Report format

```
Verified:
- npm ci && npm run lint && npm run typecheck → clean
- npm test → 42 passed, 0 failed
- npx playwright test → 6 passed (chromium)
- Manual: signed up, created a task, reloaded, task persisted
Not verified:
- Email delivery (no SMTP credentials in this environment)
```

## Never

- Say "all tests pass" without having run them after your last change.
- Count a skipped or deleted test as passing.
- Hide a failing check. Fix it, or report it clearly.
