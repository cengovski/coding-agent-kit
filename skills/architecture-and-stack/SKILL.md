---
name: architecture-and-stack
description: Use when creating a new app or a major new component and you must choose language, framework, database, hosting, and folder structure. Produces a short, justified stack decision that favors boring, well-maintained technology.
---

# Architecture and stack choice

## Principles

- **Boring by default.** Prefer tools with stable releases, active maintenance, large communities, and good official docs. Each new dependency is a liability you must justify.
- **Match the team and the task**, not the hype. If the human or repo already uses a stack, use it.
- **One deployable unit** until there is a concrete reason to split. No microservices for v1.
- **Typed boundaries.** Validate data where it enters the system (HTTP, forms, files, env, third-party APIs).

## Default menu (adjust to the request)

| Need | Sensible default | Alternative |
|---|---|---|
| Full-stack web app | TypeScript + Next.js (App Router) or React + Vite with a small API | SvelteKit, Remix-style frameworks |
| API / backend only | TypeScript + Fastify/Hono, or Python + FastAPI | Go net/http |
| Script / data / CLI | Python 3.12+ with `uv` or `pip` + venv | Node CLI |
| Database | PostgreSQL (SQLite for local/single-user) | — |
| ORM / queries | Prisma or Drizzle (TS), SQLAlchemy 2.x (Python) | Raw SQL with a query builder |
| Validation | Zod (TS), Pydantic v2 (Python) | Valibot |
| Unit tests | Vitest (TS), pytest (Python) | Jest |
| E2E tests | Playwright Test | — |
| Styling | Tailwind CSS or CSS modules | Component library if speed > control |
| Auth | The framework's established auth library or a managed provider | Never roll your own crypto |

Before you commit to any row, check current versions and setup commands with `current-docs-lookup`. Do not rely on remembered versions.

## Procedure

1. List the constraints from `SPEC.md` (platform, hosting, budget, data sensitivity, offline, scale).
2. Pick a stack from the menu or the existing repo; write a 5–10 line **decision record** in `SPEC.md` → "Architecture": choice, why, what was rejected and why.
3. Sketch the structure:
   - Modules / folders by feature, not by file type, once there is more than a handful of files.
   - The data model (see `data-modeling`) and the API surface (see `api-design`).
   - Where config, secrets, and logs come from (see `error-handling-and-config`).
4. Scaffold with the framework's **official** generator (`npm create ...`, `uv init`, etc.). Do not hand-write boilerplate that a generator produces.
5. Immediately add: lint, format, typecheck, unit test runner, E2E runner (if UI), `.gitignore`, `.env.example`, and a README with run/test commands. Make the first commit green.
6. Set up CI early (a single workflow that runs install, lint, typecheck, test, build).

## Red flags

- A dependency with no release in 12+ months, single maintainer, or no docs, for a core concern.
- Two libraries that do the same job.
- Architecture diagrams with more boxes than there are users.
