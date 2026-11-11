---
name: api-design
description: Use when designing or changing HTTP/JSON APIs, server actions, or RPC endpoints for an app. Covers resource naming, request validation, status codes, error format, pagination, idempotency, and API tests.
---

# API design

## Procedure

1. List the operations each user flow in `SPEC.md` needs. Design only those.
2. For each endpoint write: method + path, auth requirement, request schema, success response, error cases. Keep this list in `SPEC.md` or an OpenAPI file if the project uses one.
3. Implement with schema validation at the edge and a test per success and error case.

## Conventions (REST-style JSON)

- Nouns for resources, plural: `GET /api/tasks`, `POST /api/tasks`, `GET /api/tasks/:id`, `PATCH /api/tasks/:id`, `DELETE /api/tasks/:id`.
- Status codes: `200` ok, `201` created, `204` no content, `400` invalid input, `401` not authenticated, `403` not allowed, `404` not found, `409` conflict, `422` semantic validation (if used consistently), `429` rate limited, `500` unexpected.
- One error shape everywhere, e.g. `{ "error": { "code": "validation_failed", "message": "Title is required", "fields": { "title": "required" } } }`. Never leak stack traces or SQL to clients.
- Pagination for any list that can grow: `?limit=&cursor=` (cursor-based) with a max limit.
- Timestamps in ISO 8601 UTC; IDs as opaque strings.
- Make retries safe: `PUT`/`DELETE` idempotent; for create/payment endpoints that clients may retry, support an idempotency key.
- Version only when you must break clients (`/v2` or header); prefer additive changes.

## Rules

- Authorization per resource on every handler (see `security-and-secrets`).
- Don't return more fields than the client needs (no password hashes, internal flags).
- Keep business logic out of handlers: handler = parse → call service → map result to response.
