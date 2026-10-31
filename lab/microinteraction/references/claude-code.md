# Claude Code

## Inline view

- Call `mcp__visualize__read_me` once with `modules: ["interactive"]`, then
  `mcp__visualize__show_widget` with one HTML view that holds every card.
- Each card is a row: the stage on the left, the text on the right. On a narrow screen the text
  stacks under the stage.
- The stage's motion is plain CSS (a transition toggled by a class, or `@keyframes` only when the
  suggestion itself is a keyframe loop). Replay removes the class, forces a reflow
  (`el.offsetWidth`), and adds it back. It also plays once on load.
- Pick and Skip are a toggle per card; nothing is chosen at the start. One button under the cards,
  Send, calls `sendPrompt("Pick 1, 3. Skip 2.")` with the numbers as chosen. A card left unchosen
  counts as Skip.
- After the view, end the turn. The owner's reply is the pick.

## Without the inline view

In a terminal or a headless run, print the three Parts as text, then end with: "Reply with the
numbers to pick, for example Pick 1, 3. The rest are skipped." End the turn there. Nobody answering
is not a pick.

## Files

The inline view is the only output. Never use `Edit` or `Write` on the project in this command.
