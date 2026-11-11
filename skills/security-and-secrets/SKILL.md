---
name: security-and-secrets
description: Use when handling credentials, API keys, auth, user input, file uploads, databases, or dependencies, and before shipping any app. Defensive security baseline and secrets hygiene for web apps, APIs, and scripts.
---

# Security and secrets hygiene

Defensive only. Protect the user's system and data.

## Secrets

- Secrets come from **environment variables or a secret manager**, never source code, tests, fixtures, docs, or commit messages.
- Commit `.env.example` with variable names and placeholder values; keep `.env*` in `.gitignore`.
- Never print, log, or echo secret values; redact tokens in error messages and logs.
- Before every commit, check the diff for keys, tokens, passwords, private keys, and connection strings. Use a secret scanner (e.g. gitleaks) in CI when possible.
- If a secret was committed: tell the human immediately — it must be **rotated**; deleting it from the latest commit is not enough.
- Client-side code is public. Only expose values explicitly meant to be public (e.g. framework `NEXT_PUBLIC_*` vars), never server secrets.

## Input and output

- Validate all input on the server with a schema (type, length, format, allowed values). Client validation is UX, not security.
- SQL: parameterized queries / ORM only. Shell: argument arrays, never string concatenation with user input.
- Output encoding: rely on the framework's escaping; avoid raw HTML injection APIs (`dangerouslySetInnerHTML`, `|safe`) with user content.
- File uploads: check size and type, store outside the web root or in object storage, generate your own filenames.

## Auth and access

- Use an established auth library or provider; never write your own password hashing or crypto. If you store passwords, use a slow hash (argon2/bcrypt) via a library.
- Check authorization on the **server for every request** to a protected resource ("can *this* user access *this* record?"), not just authentication.
- Secure cookies (`HttpOnly`, `Secure`, `SameSite`), CSRF protection for cookie-based forms, rate limiting on login and expensive endpoints.
- Principle of least privilege for DB users, API tokens, and CI permissions.

## Dependencies and config

- Add only maintained dependencies; commit lockfiles; run `npm audit` / `pip-audit` and fix high-severity issues.
- Security headers via the framework or middleware; HTTPS in production; CORS restricted to known origins.
- Debug modes and verbose error pages off in production.

## Pre-ship checklist

- [ ] No secrets in repo history of this change (`git log -p` / scanner).
- [ ] `.env.example` complete; `.env` ignored.
- [ ] Every protected route/endpoint has an authz check and a test for the unauthorized case.
- [ ] Inputs validated server-side.
- [ ] Dependency audit has no unaddressed high/critical issues.
