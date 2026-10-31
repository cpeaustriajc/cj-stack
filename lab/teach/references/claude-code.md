# Claude Code

## Spawns

- how's explorers and explainer use the spawns in `../how/references/claude-code.md`.
- Send how's first spawns in the same message as why's first git command, so the two run in
  parallel.
- why's narrow default is git and its PRs. Add a tracker or docs source, at most two, only when
  the reasons are the point: the person asks why, or the subject is a past decision.
- A /teach run spawns no `general-purpose` agent: it can edit, and a run changes no file. So the
  session reads each source itself with its MCP or CLI, never through why's investigators.
- Never `model: "opus"` on a subagent; the main session teaches.

## Sibling skills

- `how`, `why` and `unslop` are lab skills. `/how` is slash-only, so read `../how/SKILL.md`,
  `../why/SKILL.md` and `../unslop/SKILL.md` and follow them.
- If `../unslop/SKILL.md` is missing, write plain English by the rules in SKILL.md and say so in
  one line at the end of the reply, never before the short answer.

## Diagram series

- Call `mcp__visualize__read_me` once with `modules: ["interactive"]`, then
  `mcp__visualize__show_widget` with an HTML build-up stepper: one frame per diagram.
- Frame 1 holds the first two parts and the edge between them. Each next frame redraws every part
  and edge of the frame before it in the same place, and adds one part or edge, drawn in the
  accent colour with its label. A one-line caption under each frame says what the new part does.
- Back and Next buttons move one frame; a row of frame dots shows where you are. The widget opens
  on frame 1, never on the last frame.
- A click on a part calls `sendPrompt("/teach <part name>: go one layer deeper")`.
- A spatial idea (layout, overlap, scroll position, before and after) is an inline SVG in the
  frame, drawn marker-on-whiteboard style: hand-drawn strokes, a few short labels. There is no
  image-generation tool; never describe the picture in words instead.
- Without the visualize tools (terminal, headless evals), print the series as mermaid blocks in
  order, each headed `Step <n> of <total>`. Each block repeats every node and edge of the block
  before it and adds one. Never print only the final block.
