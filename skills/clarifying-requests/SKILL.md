---
name: clarifying-requests
description: Use when starting from a product idea or feature request, before writing code. Turns a vague request into a short SPEC.md with users, goals, non-goals, acceptance criteria, and assumptions. Use when requirements are ambiguous or the request is one or two sentences long.
---

# Clarifying requests

Goal: a written definition of done that a test can check. Building the wrong thing well is still failure.

## Procedure

1. **Restate** the request in 2–3 sentences: who the user is, what they do, why it matters.
2. **Find the gaps.** For each, decide: is it *consequential* (hard to reverse, changes scope, money, data, auth, legal) or *defaultable*?
   - Consequential → ask. Batch all questions into **one** message, max ~5, each with a recommended default and options, e.g. "Auth: (a) email magic link [recommended], (b) Google OAuth, (c) none for v1".
   - Defaultable → choose a sensible default and record it under *Assumptions*.
3. If the human is unavailable or says "you decide", proceed with your recommended defaults and record them.
4. **Write `SPEC.md`** using `templates/SPEC.md`:
   - Problem and target user
   - Core user flows (numbered steps)
   - Acceptance criteria — each one observable and testable ("Given/When/Then" or a checkable sentence)
   - Non-goals for this version (explicit, to block scope creep)
   - Assumptions and open questions
   - Constraints: platform, budget, hosting, deadlines, data privacy
5. Keep v1 small: the smallest version that delivers the core flow end to end. Put everything else under "Later".
6. Show the spec to the human if they are present; otherwise continue.

## Good acceptance criteria

- ✅ "A signed-out user who visits /dashboard is redirected to /login."
- ✅ "Creating a task with an empty title shows 'Title is required' and does not save."
- ❌ "The app is fast and user-friendly." (not testable — make it concrete or drop it)

## Anti-patterns

- Asking ten questions one at a time.
- Asking about things you can find in the repo or docs.
- Silently adding features nobody asked for.
