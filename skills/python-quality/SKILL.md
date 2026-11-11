---
name: python-quality
description: Use when writing or reviewing Python (scripts, CLIs, APIs, data code). Covers project setup, typing, structure, error handling, testing with pytest, and tooling (ruff, mypy/pyright).
---

# Python quality

## Project setup

- Python 3.12+ (or the repo's pinned version). One isolated environment per project (`uv` or `python -m venv`). Never install into the system Python.
- `pyproject.toml` for metadata, dependencies, and tool config. Pin direct dependencies; commit the lockfile if the tool produces one.
- Tooling: `ruff` (lint + format), `mypy` or `pyright` (types), `pytest` (tests).
- Layout: `src/<package>/...` and `tests/...`. Entry point via `if __name__ == "__main__": main()` or a console script.

## Code

- Clear names, small functions, one responsibility each. Write a `main()`; avoid top-level side effects so modules import cleanly in tests.
- Type hints on all public functions; use `dataclass` / Pydantic models for structured data, `Enum`/`Literal` for fixed choices.
- Validate external input (CLI args, files, HTTP, env) at the boundary, e.g. with Pydantic or `argparse` types.
- Use the standard library first (`pathlib`, `datetime` with time zones, `logging`, `json`, `csv`, `argparse`).
- Use context managers (`with`) for files, connections, and locks.
- f-strings for formatting; never build SQL or shell commands with string formatting (use parameters / argument lists).

## Errors

- Catch specific exceptions you can handle; never bare `except:` or `except Exception: pass`.
- Raise meaningful exceptions with context; use `raise ... from err` to keep the cause.
- Use `logging`, not `print`, in library/service code.

## Tests (pytest)

- Plain `assert`, small focused tests, fixtures for setup, `parametrize` for input tables, `tmp_path` for files, `monkeypatch` for env.
- Test behavior through public functions; isolate network and time.

## Before committing

`ruff check . && ruff format --check . && mypy . && pytest -q` (adapt to the repo) — all clean.
