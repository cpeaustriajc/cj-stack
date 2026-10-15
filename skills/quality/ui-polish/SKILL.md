---
name: ui-polish
description: >
  This skill should be used when the user asks to review a UI against its design, polish spacing,
  type, colour or motion, or sign off a visual change, and before asking for visual sign-off. It
  compares the screen with the design and a list of common mistakes, and reports a
  Before/After/Why table with one verdict: ship, ship after the top fixes, or rework.
---

# UI polish

The goal is a UI that matches its design and feels quick, without extra flourishes. This skill
reviews and reports. It changes nothing until I name what to change.

## 1. Find the source of truth

Before judging anything, find the design: a mockup, a Figma frame, a design-tool export, a
screenshot I gave you, or the closest existing screen in the same app. **The design wins over
your taste.** A design plan
I approved counts as the design, even when it departs from the existing screens. If there is
no design, say so and judge against the existing screens.

Look at the real thing in a browser, at the real width and at 375px, in light and dark if the
app has both. Reading the code is not enough.

## 2. Check against the mistake list

Read `references/motion.md` when the change has motion, `references/interaction.md` when it has
controls, forms, loading or navigation, and `references/app-ui.md` for dashboards, admin,
settings or other dense app screens. Every row in the report names the rule it breaks.

**Layout and content**
- Drifts from the design: spacing, radius, weight, colour, order, or components the design
  doesn't have.
- Clutter: a description under every heading, helper text that repeats the label, a paragraph
  where a line would do. Recommend cutting.
- Truncated text with no way to read it in full. It needs a tooltip or a title on hover.
- Missing states: empty, loading, error, one item, very long values.
- Hand-built widget where the project's component library already has one, such as a tooltip,
  dialog or select.
- Labels or calls to action that contradict each other, such as "Buy now" next to a different
  price flow.

**Motion**
- Any `ease-in`, on entrances or exits. Ease out instead; ease-in-out only for movement already
  on screen.
- Feedback to a click, key or hover that doesn't start at once, or a duration outside the
  per-element bands in `references/motion.md`. One deliberate page-load or reveal sequence the
  design asks for may run longer.
- More than one thing moving for attention at once. Stage one change at a time; secondary
  motion stays smaller and quieter than the main one.
- Things that grow from `scale(0)`. Start from about 0.95 with opacity.
- Animating `width`, `height`, `top`, `left` or `margin` instead of `transform` and `opacity`.
- Keyframe animations that can't be interrupted, so they jump when toggled fast. Prefer
  transitions.
- Animation on something used dozens of times a session, such as typing or keyboard actions.
- No `prefers-reduced-motion` fallback.

Fix order for motion: delete the animation, shorten it, fix the easing, fix the origin, make it
interruptible, then move it to `transform` and `opacity`.

A tradeoff the code or design documents, such as a comment explaining a deliberately slow
transition, is respected. Mention it in the row, but don't flag it as a mistake.

## 3. Report, then stop

One table with one row per issue, most visible first:

| # | Where | Before | After | Why |
|---|---|---|---|---|

When the issue is in code, "Where" cites `file:line` as well as the screen location. Attach a screenshot when the issue is
visual. Then give one verdict: **Ship**, **Ship after the top N**, or **Rework** when it is off-
design. Fix only the rows I name.
Asked to run until clean, every row is named: fix them all, then run steps 1–3 again in full.
A pass counts only with its table and verdict. Ask for sign-off once, after a pass with no rows.
For a visual change, put before and after screenshots in the PR
body; the PR review is the sign-off. Wait before committing only when the project requires it or
the commit goes to the trunk.
