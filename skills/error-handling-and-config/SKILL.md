---
name: error-handling-and-config
description: Use when adding error handling, logging, environment variables, or configuration to an app. Covers validating config at startup, a consistent error strategy, user-facing messages, and structured logging.
---

# Error handling, logging, and configuration

## Configuration

- All environment-specific values (URLs, keys, feature flags, ports) come from environment variables.
- **Validate config once at startup** with a schema (Zod / Pydantic settings). Fail fast with a clear message naming the missing variable — never the value.
- Export a single typed `config` object; don't read `process.env` / `os.environ` all over the code.
- Document every variable in `.env.example` with a placeholder and a one-line comment. Keep README setup steps in sync.
- Sensible local defaults are fine for non-secrets; secrets have no defaults.

## Errors

- Distinguish **expected** errors (validation, not found, permission, conflict) from **unexpected** ones (bugs, outages).
  - Expected → return a typed result or a specific error class; map to a clear user message and the right status code.
  - Unexpected → let them propagate to one top-level handler that logs details and returns a generic message.
- Catch only where you can do something useful (retry, fallback, translate, add context). Never swallow errors silently.
- External calls: set timeouts; retry only idempotent operations, with backoff and a cap.
- UI: every async action shows pending, success, and error states; errors tell the user what to do next.

## Logging

- Use a logger with levels (`debug`, `info`, `warn`, `error`); structured (JSON) in production.
- Log events with context (request id, user id, operation), not secrets, tokens, passwords, or full personal data.
- One log line per error at the place it's handled — not at every layer.
