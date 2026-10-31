# Claude Code

## Read-only

- Use only Read, Grep, Glob and Bash commands that change nothing (`git log`, `git diff`,
  `git show`), and only to find the project's terms or check a fact.
- Never call Write or Edit, never commit, and never start an `Agent`. A re-pitch is not new work.

## The picture

- Call `mcp__visualize__read_me` once with `modules: ["interactive"]`, then
  `mcp__visualize__show_widget` with one small HTML diagram: at most six boxes, with lines between
  the boxes that connect.
- A click on a box calls `sendPrompt("<the box label>: explain this part of your re-pitch more")`.
  Never start it with `/bro`: SKILL.md re-pitches an argument as new text.
- On a narrow screen the boxes stack in the order of the lines.
- Without the visualize tools (terminal, headless runs), print a mermaid `flowchart LR` block with
  the same boxes and lines, or the same boxes drawn in a code block for a before and after.
