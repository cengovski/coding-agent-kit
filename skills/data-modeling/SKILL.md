---
name: data-modeling
description: Use when designing database tables or document schemas, adding fields, or writing migrations. Covers entities and relationships, constraints, indexes, migrations, and seed data.
---

# Data modeling

## Procedure

1. From `SPEC.md`, list entities (nouns users care about) and relationships (one-to-many, many-to-many).
2. For each table: primary key, required vs optional fields, unique constraints, foreign keys with `ON DELETE` behavior, `created_at`/`updated_at`.
3. Put integrity in the database, not only in code: `NOT NULL`, `UNIQUE`, `CHECK`, foreign keys.
4. Add indexes for foreign keys and the queries you actually run (filters, sorts, lookups). Don't index speculatively.
5. Write a **migration** with the project's migration tool; never edit the production schema by hand or edit an already-applied migration.
6. Add a small, deterministic **seed** script for local dev and tests.
7. Test: queries with real DB (container or SQLite where compatible), constraint violations, and the migration applying from scratch.

## Rules

- Normalize first; denormalize only for a measured need.
- Money as integer minor units (cents) or a decimal type, never float. Store currency.
- Time as UTC timestamps; convert at display.
- Every row a user owns has an owner column (`user_id`/`org_id`) used in every query for access control.
- Soft delete only if the spec needs undo or audit; otherwise delete.
- Destructive migrations (drop/rename column) are two-step: add new → backfill → switch code → drop later. Ask the human before any migration that can lose production data.
