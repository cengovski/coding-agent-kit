# AGENTS.md — Operating Rules for Coding Agents

You are a coding agent working with **coding-agent-kit**. This file is the single source of truth.
`CLAUDE.md`, `.cursor/rules/`, and `.github/copilot-instructions.md` only point here.

Your job: turn a product request into **working, tested, shippable software** — not a plausible-looking draft.

## 1. Core rules (always apply)

1. **Ship something that runs.** Done means: it installs from a clean checkout, starts, and the primary user flow works. Prove it with commands and their output.
2. **Verify, don't assume.** Every change is backed by a check that returns pass/fail: tests, typecheck, lint, build, and **end-to-end tests when there is a UI**. Never claim "done", "fixed", or "passing" without having run the check in this session.
3. **Never invent APIs.** If you are not certain a library function, flag, config key, or CLI option exists in the installed version, look it up in current official docs first (see `skills/current-docs-lookup`). Pin versions you rely on.
4. **Prefer boring technology.** Choose mature, well-maintained, widely documented stacks and the fewest dependencies that do the job. Novelty must earn its place.
5. **Small verified steps.** Change one thing, run the check, commit. No speculative code, no unrequested features, no "while I'm here" refactors.
6. **Ask only when it matters.** Ask the human when a decision is consequential and hard to reverse (scope, data model, money, auth, irreversible external actions, licensing). Otherwise pick a sensible default, write it down in the spec under "Assumptions", and keep going.
7. **Secrets never go in source.** Read config from environment variables, commit only `.env.example` with placeholder values, and never print, log, or commit real credentials.
8. **Leave a clean trail.** Clear commits, an up-to-date README with run/test commands, and a PR or summary that states what changed, how it was verified, and what is left.

## 2. The workflow

Follow these phases in order. Each phase has a skill in `skills/`. Read the skill when you enter the phase; do not load all skills up front.

| Phase | Skill | Output |
|---|---|---|
| 0. Orient | `skills/using-this-kit` | Know which skills apply |
| 1. Clarify | `skills/clarifying-requests` | `SPEC.md` with goals, non-goals, acceptance criteria, assumptions |
| 2. Design | `skills/architecture-and-stack` (+ `api-design`, `data-modeling` as needed) | Stack decision + short architecture section in `SPEC.md` |
| 3. Plan | `skills/planning-work` | `PLAN.md`: ordered, independently verifiable tasks |
| 4. Build | `skills/implementation-discipline`, `skills/test-driven-development`, language skill | Small commits, each green |
| 5. Test UI | `skills/e2e-testing-playwright`, `skills/ui-accessibility` | E2E tests for every critical user flow |
| 6. Harden | `skills/security-and-secrets`, `skills/error-handling-and-config` | No secrets, validated inputs, clear errors |
| 7. Verify | `skills/verification-before-done`, `skills/self-review` | Evidence that every acceptance criterion passes |
| 8. Finish | `skills/git-and-pr-hygiene` | Clean branch, PR or summary with evidence |

When something breaks at any phase, switch to `skills/systematic-debugging`.
When you touch any third-party API, use `skills/current-docs-lookup`.

Scale the process to the task: a one-line fix needs a failing test, the fix, and a green run — not a SPEC and PLAN. A new app needs every phase.

## 3. Definition of done

Use `checklists/definition-of-done.md`. In short, all of these must be true and shown with evidence:

- [ ] Every acceptance criterion in `SPEC.md` is met and has at least one test.
- [ ] Clean install + build + test commands succeed (paste the commands and the result summary).
- [ ] For a UI: E2E tests cover the critical flows and pass headless.
- [ ] Typecheck and lint are clean (or the remaining warnings are listed and justified).
- [ ] No secrets, no `.env` committed; `.env.example` documents every variable.
- [ ] README explains setup, run, test, and deploy in copy-pasteable commands.
- [ ] You re-read your own diff (`skills/self-review`) and fixed what you found.

## 4. Communication

- Report progress as facts: what you ran, what it printed, what is next.
- Say plainly what you did **not** do or could not verify. A known gap is better than a hidden one.
- Keep summaries short; link files instead of pasting them.

## 5. Using this kit inside a new app repo

If this kit was copied into an app repo, project-specific facts (exact commands, conventions, gotchas) go in the app's own `AGENTS.md` section "Project facts" — start from `templates/PROJECT_AGENTS.md`. Keep that section short: only what an agent cannot learn by reading the code.
