# Interaction rules

Check each rule against the change. A row in the report names the rule it breaks.

**Press and release**
- The control responds on press (`pointerdown` or an `:active` highlight) and confirms on release.
- Dragging off the control cancels the action.
- No double-tap delay; set `touch-action: manipulation`.

**Hit targets**
- At least 24x24 CSS px (WCAG 2.2 SC 2.5.8). Smaller targets pass only with the spacing, equivalent, inline, user-agent or essential exception.
- At least 44x44 on touch.
- The target extends past the visual, so a drifting pointer doesn't cancel.
- A checkbox or radio and its label form one target.

**Drag and hover**
- A drag follows the pointer 1:1 from the grab point.
- A destructive swipe commits on release, not mid-swipe.
- A slider keeps its drag when the pointer leaves it.
- A hover menu closes after about 300ms so the cursor can cross a gap.
- Hover triggers sit on a stable parent so the menu doesn't flicker.

**Loading**
- A spinner or skeleton appears only after 150-300ms, then stays at least 300-500ms.
- Use optimistic UI where a failure is safe to roll back.

**Focus**
- Focus rings use `:focus-visible`. An outline is never removed without a replacement.
- Compound controls use `:focus-within`.
- Sticky headers don't cover the focused element.
- Anchors carry `scroll-margin-top`.

**Forms**
- Mobile inputs are 16px or larger so iOS doesn't zoom, and zoom is never disabled.
- Paste is never blocked.
- Each input has the right `type`, `inputmode` and `autocomplete`.
- Submit stays enabled until the request starts.
- Errors appear inline, say the fix, and focus moves to the first error.
- Unsaved changes trigger a warning before leaving.

**Destructive actions**
- Each gets a confirmation or an undo window.

**Navigation**
- The URL reflects filters, tabs and pagination.
- Links open in a new tab with Cmd or Ctrl-click.

**Accessible text and contrast (WCAG 2.2)**
- Normal text has at least 4.5:1 contrast against its background (SC 1.4.3).
- Large text, 18pt or 14pt bold and up, has at least 3:1 (SC 1.4.3).
- UI component boundaries, states and meaningful graphics have at least 3:1 (SC 1.4.11).
- Icon-only buttons have an `aria-label`.
- Toasts use `aria-live="polite"`.
- Every gesture has a tap or keyboard alternative.

**Scroll and screen edges**
- Modals and drawers use `overscroll-behavior: contain`.
- Full-bleed layouts respect `env(safe-area-inset-*)`.

**Mobile web**
- App shells use `100dvh` and full-screen heroes use `100svh`, never `100vh`, which jumps when
  the mobile browser bars move.
- `-webkit-tap-highlight-color: transparent` only when the control has its own visible pressed
  state.
- A `theme-color` meta for each colour scheme, light and dark, using its `media` attribute.
- `user-select: none` only on controls such as buttons, tabs and drag handles, never on content.
- Check on a real phone, not only a narrow desktop window.

Sources: https://vercel.com/design/guidelines, https://github.com/vercel-labs/web-interface-guidelines, https://rauno.me/craft/interaction-design, https://developer.apple.com/videos/play/wwdc2018/803/, https://www.joshwcomeau.com/animation/css-transitions/, https://www.w3.org/TR/WCAG22/, https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
