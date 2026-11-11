---
name: current-docs-lookup
description: Use before using any library, framework, SDK, CLI, or cloud API you are not certain about in its installed version — setup commands, function signatures, config keys, flags, breaking changes. Prevents invented or outdated APIs by consulting live official documentation.
---

# Current documentation lookup

Your training data is a snapshot. Libraries change. Invented APIs are the most common way agents ship broken code.

## Order of sources

1. **The installed code itself**: the version in the lockfile, the package's type definitions (`node_modules/<pkg>/*.d.ts`), docstrings, `--help` output, the package's README/CHANGELOG in the dependency folder.
2. **A live docs tool if available**: e.g. a Context7 MCP server (resolve the library ID, then fetch docs for the specific topic and version), or another docs MCP the environment provides.
3. **Official documentation on the web**: the project's own docs site, release notes, and migration guides for the exact major version. Prefer these over blog posts and Q&A answers.
4. **Source repository**: examples and tests in the official repo.

## Procedure

1. Identify the library **and version** (`package.json`/lockfile, `pyproject.toml`, `pip show`, `npm ls <pkg>`).
2. Look up the specific thing you need (one topic, not the whole manual).
3. Use what the docs say for that version. If docs and memory disagree, docs win.
4. If you cannot verify something, say so, choose the conservative documented path, and add a test that would catch it being wrong.
5. When scaffolding, use the official generator/quickstart command from current docs, and record the versions installed.

## Red flags you are guessing

- You "remember" an option but can't point to where it is documented.
- Code compiles only after adding `any`/`# type: ignore`.
- The import path or package name is from an older major version.
- Copying a snippet without checking its date or version.

## Never

- Invent function names, flags, env vars, or config keys.
- Upgrade a major version silently to make an example work.
- Paste API keys into docs queries.
