---
name: e2e-testing-playwright
description: Use for any project with a web UI to write and run end-to-end tests with Playwright Test. Covers setup, resilient locators, web-first assertions, test isolation, auth state, and CI. Use when adding a user-facing flow or verifying a UI change.
---

# End-to-end testing with Playwright

Check current setup commands and APIs in the official docs (https://playwright.dev/docs/intro) via `current-docs-lookup` before writing config. Do not rely on memory for flags or config keys.

## Setup

1. Install with the official initializer (currently `npm init playwright@latest`), choose TypeScript, a `tests/e2e` (or `e2e`) folder, and a CI workflow if offered.
2. In `playwright.config.ts`, configure:
   - `baseURL` pointing at the local app.
   - `webServer` to start the app automatically for tests (command + url + `reuseExistingServer` locally).
   - `trace: 'on-first-retry'` and retries only on CI.
   - At least Chromium; add Firefox/WebKit when cross-browser matters.
3. Add scripts: `"test:e2e": "playwright test"`. Ensure browsers install in CI (`npx playwright install --with-deps`).

## Writing tests

- **One test per user flow outcome**, named from the user's view: `user can create and complete a task`.
- **Locators the user would use**, in this order: `getByRole` (with accessible name) → `getByLabel` → `getByPlaceholder` → `getByText` → `getByTestId`. Avoid CSS/XPath tied to layout.
- **Web-first assertions** that auto-wait: `await expect(page.getByRole('heading', { name: 'Tasks' })).toBeVisible()`. Never `waitForTimeout`.
- **Isolation.** Each test sets up its own data (API call or fixture) and does not depend on test order. Use unique values per test.
- **Auth.** Log in once in a setup project and reuse `storageState`; don't type credentials in every test. Test-only credentials come from env vars, never committed.
- **Network.** Mock third-party services at the network layer (`page.route`) when they are slow, paid, or flaky; keep your own backend real.
- Use fixtures / page objects only when duplication actually appears.

## Minimum coverage for a web app

- [ ] Main happy path of every core flow in `SPEC.md`.
- [ ] Form validation error shown for invalid input.
- [ ] Auth gate: signed-out user cannot reach protected pages.
- [ ] Data persists after reload.
- [ ] Basic accessibility smoke test (see `ui-accessibility`; e.g. `@axe-core/playwright` on key pages).

## Running and debugging

- Headless run: `npx playwright test`; one file: `npx playwright test tests/e2e/tasks.spec.ts`.
- Debug: `--ui`, `--debug`, or open the trace from `npx playwright show-report`.
- Flaky test? Find the race (missing await, non-web-first assertion, shared data). Do not add retries or sleeps to hide it.
