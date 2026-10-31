# Playwright

Mechanics for the hero-script video in SKILL.md step 7. Read the current Playwright docs when a
detail matters, since these change.

- **Click and key marks**: `screencast.show_actions(cursor="pointer", style={"title": "display:
  none", "point": "width: 28px; height: 28px; border: 3px solid red; border-radius: 50%"})`, plus
  a key label of your own. Playwright draws no click mark unless `point` is styled.
- **Pace**: the `duration` option of `show_actions` pauses before each action.
- **Chapter cards**: `screencast.show_chapter(title, description=...)`.
- If `screencast` is missing, the installed Playwright is older than these calls: upgrade it or
  use the project's own helper.
