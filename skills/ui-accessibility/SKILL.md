---
name: ui-accessibility
description: Use when building or changing user interface components, pages, or forms. Baseline accessibility and UI quality — semantic HTML, keyboard support, labels, contrast, states, and responsive layout — plus how to test it.
---

# UI quality and accessibility

## Baseline (every screen)

- **Semantic HTML first**: `button` for actions, `a` for navigation, `label` tied to every input, headings in order, landmarks (`header`, `nav`, `main`, `footer`). ARIA only when no native element fits.
- **Keyboard**: every interactive element reachable with Tab, visible focus style, Esc closes dialogs, focus moves into and back out of modals.
- **Text alternatives**: meaningful `alt` on images (empty `alt=""` for decorative), accessible names on icon-only buttons.
- **Contrast**: text meets WCAG AA (4.5:1 normal, 3:1 large). Don't convey meaning by color alone.
- **Forms**: inline error messages linked to fields, errors announced, don't clear user input on error, clear required markers.
- **States**: design loading, empty, error, and success states for every data view — not just the happy path.
- **Responsive**: works at 360px wide and on desktop; no horizontal scroll; tap targets ~44px.
- **Motion**: respect `prefers-reduced-motion`.

## Testing

- E2E tests locate elements by role and label (`getByRole`, `getByLabel`); if you can't, the UI is probably not accessible.
- Run an automated scan (e.g. `@axe-core/playwright`) on key pages in E2E and fix violations.
- Do one keyboard-only pass through the main flow.

## Consistency

- Use one component library or a small set of shared components; consistent spacing scale and typography.
- Copy is short and specific: buttons say what they do ("Save task", not "Submit").
