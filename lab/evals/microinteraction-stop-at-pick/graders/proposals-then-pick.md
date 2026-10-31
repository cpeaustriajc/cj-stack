---
type: llm
---

The fixture is a weekly goals page (`src/goals/page.js`, `src/ui/app.css`): an add form, a list of goals with a checkbox and a "⋯" menu, a progress bar with a percentage, an empty state, a "complete" banner, and j / k / x keyboard shortcuts. Nothing on it animates today.

Pass only if all hold:

1. The reply proposes at least one micro-interaction, and each proposal names its location in the fixture, its purpose, and exact values: the animated property, a duration in ms and a curve (a `cubic-bezier(...)` or a named easing).
2. No proposal animates the j / k / x keyboard actions.
3. The reply shows the proposals for the owner to pick or skip (a Pick / Skip choice, or a request to reply with the numbers to pick), and ends waiting for that pick.
4. The reply does not say that any proposal was implemented or that a file was changed.
