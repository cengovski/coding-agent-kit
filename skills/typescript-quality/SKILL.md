---
name: typescript-quality
description: Use when writing or reviewing TypeScript or JavaScript (Node, React, Next.js, etc.). Covers strict config, types at boundaries, runtime validation, async correctness, module hygiene, and tooling.
---

# TypeScript / JavaScript quality

## Project setup

- TypeScript with `"strict": true` (plus `noUncheckedIndexedAccess` for new projects). Prefer TS over plain JS for anything non-trivial.
- Scripts in `package.json`: `dev`, `build`, `start`, `lint`, `typecheck` (`tsc --noEmit`), `test`, `test:e2e`.
- ESLint (the framework's recommended config) + Prettier or the framework's formatter. Commit the lockfile; use `npm ci` / `pnpm install --frozen-lockfile` in CI.
- Pin the Node version (`engines` and/or `.nvmrc`). Use an active LTS.

## Types

- No `any`. Use `unknown` and narrow. If an escape hatch is truly needed, isolate it and comment why.
- Let inference work inside functions; annotate exported function signatures and public types.
- Model states with discriminated unions instead of optional-field soup:
  `type Load = { status: 'loading' } | { status: 'error'; error: string } | { status: 'ok'; data: Task[] }`.
- Derive types from a single source: `z.infer<typeof Schema>`, DB schema types, `as const` objects. Don't hand-maintain duplicates.
- Avoid `as` casts and non-null `!` except right after a check the compiler can't see.

## Boundaries

- Validate everything external at runtime (request bodies, query params, env, `JSON.parse`, third-party responses) with a schema (e.g. Zod). Types alone don't validate data.
- Parse once at the edge, then pass typed values inward.

## Async and errors

- Always `await` or deliberately handle promises; enable `no-floating-promises`.
- Run independent awaits in parallel with `Promise.all`; don't `await` in a loop unless order matters.
- Throw `Error` objects (or subclasses), never strings. Don't swallow errors with empty `catch`.

## Code style

- Small modules with explicit exports; prefer named exports.
- Pure functions for logic; side effects at the edges.
- `const` by default; immutable updates for shared state.
- React: keep components small, derive state instead of syncing it, keys on lists, effects only for real side effects, server/client boundaries respected in frameworks that have them.

## Before committing

`npm run lint && npm run typecheck && npm test` — all clean.
