---
type: llm
---

The fixture is a toast stack. `toast.css` moves each toast with a CSS `transition` on `transform` and `opacity` (400ms enter, 200ms exit, `cubic-bezier(0.23, 1, 0.32, 1)`, `@starting-style`, a reduced-motion block). New toasts change the older toasts' `--offset`, so a toast still entering is retargeted mid-motion; a CSS transition retargets from its live value, which is correct here. Separately, a swipe release (`data-swiped` / `data-snapping`) dismisses or snaps back on a fixed 200ms curve and ignores the release velocity.

Pass only if all hold:

1. No row or recommendation asks for a spring, the Web Animations API, a JS animation library or "physics" for the toast stack's enter, exit or restacking, and none says those transitions cannot be interrupted or will jump when retargeted.
2. The swipe release (the snap-back or the dismiss after a drag) is flagged for ignoring velocity, with a spring or a velocity-projected endpoint as the fix.
3. The reply ends with one verdict: Ship, Ship after the top N, or Rework.

Rows about other things (durations, shadow, the 110% exit, accessibility) do not fail it.
