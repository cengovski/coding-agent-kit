---
name: using-this-kit
description: Start here. Use at the beginning of any coding task to decide which skills in this kit apply and in what order. Use when you receive a new product request, a bug report, or a feature request and have not yet chosen a workflow.
---

# Using this kit

## Procedure

1. Read `AGENTS.md` once (core rules + workflow table). Do not read every skill.
2. Classify the task:
   - **New app or major feature** → full workflow: clarify → architecture → plan → build → test → harden → verify → finish.
   - **Small feature** → clarify briefly (acceptance criteria in the task or PR), plan inline, TDD, verify, finish.
   - **Bug** → `systematic-debugging` → regression test → fix → verify → finish.
   - **Question / investigation** → read code and docs, answer with file references; change nothing.
3. List the skills you will use, in order, in one line. Example: `clarifying-requests → architecture-and-stack → planning-work → test-driven-development → e2e-testing-playwright → self-review → git-and-pr-hygiene`.
4. Open each skill only when you reach its step.

## Skill index

| Skill | Use when |
|---|---|
| clarifying-requests | Turning a request into `SPEC.md` |
| architecture-and-stack | Choosing a stack and structure for a new app |
| api-design | Designing HTTP/RPC endpoints |
| data-modeling | Designing tables, schemas, migrations |
| planning-work | Breaking a spec into ordered, verifiable tasks |
| implementation-discipline | Writing code in small steps |
| test-driven-development | Any behavior change |
| typescript-quality | Writing TS/JS |
| python-quality | Writing Python |
| current-docs-lookup | Using any library, framework, CLI, or cloud API |
| e2e-testing-playwright | Any app with a web UI |
| ui-accessibility | Building UI components and pages |
| error-handling-and-config | Errors, logging, env vars, configuration |
| security-and-secrets | Auth, user input, dependencies, credentials |
| systematic-debugging | Anything fails unexpectedly |
| verification-before-done | Before saying "done" |
| self-review | Before opening a PR or handing off |
| git-and-pr-hygiene | Branching, committing, opening a PR, finishing |

## Rules

- If a skill conflicts with an explicit instruction from the human, the human wins; note the deviation.
- If the project already has conventions, follow them over this kit's defaults.
