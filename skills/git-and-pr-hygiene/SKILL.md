---
name: git-and-pr-hygiene
description: Use when branching, committing, pushing, opening a pull request, or finishing a piece of work. Covers small focused commits, clear messages, safe git operations, PR descriptions with evidence, and wrapping up.
---

# Git and PR hygiene

## Branching

- Start from an up-to-date default branch: `git switch main && git pull`.
- One branch per task: `feat/task-create`, `fix/login-timeout`, `chore/ci`.
- Check `git status` before and after every operation.

## Commits

- Small and focused: one logical change, tests included, suite green.
- Message: imperative summary ≤ 72 chars, blank line, *why* in the body when not obvious. Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`) if the repo uses them.
- Stage deliberately (`git add -p` or explicit paths). Never commit `.env`, secrets, build output, `node_modules`, large binaries, or editor files.
- Do not commit generated noise or unrelated formatting changes.

## Safety

- Never force-push shared branches, rewrite published history, or skip hooks (`--no-verify`) unless the human explicitly asks.
- Don't commit directly to `main` in a shared repo unless that is the project's agreed workflow.
- Resolve conflicts by understanding both sides; rerun tests after.

## Finishing

1. Run the full verification (`verification-before-done`).
2. Do the `self-review` pass on the full diff (`git diff main...HEAD`).
3. Update README / docs / `.env.example` / changelog if behavior or setup changed.
4. Push the branch and open a PR (e.g. `gh pr create`) using `templates/PULL_REQUEST.md`:
   - **What & why** — 2–4 sentences, link the spec/issue.
   - **How verified** — commands run and results; screenshots for UI.
   - **Risks / follow-ups** — what's not done, known limitations.
5. Keep the PR reviewable (ideally < ~400 changed lines). Split large work into stacked or sequential PRs.
6. After review feedback: address each point or explain why not; re-verify; push new commits rather than rewriting reviewed history.
7. Merge only when CI is green and a human has approved (or the human asked you to merge). Delete the merged branch.
