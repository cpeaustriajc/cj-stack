# Claude Code

## Read-only

- Use only read tools: Read, Grep, Glob, and Bash commands that change nothing (`git status`,
  `git log`, `git diff`, `gh pr view`, `gh pr checks`, `gh run list`).
- Never call Write, Edit, `git commit`, `git push`, `gh pr comment`, or a command that starts a
  server, a test run or a build. Never start an `Agent`.
- Agents this chat started: read their last notification or `TaskList`. `ListAgents` names the
  live sessions. Do not message them.

## Sibling skills

- `/bro` (lab) is slash-only. Read `../bro/SKILL.md` for its voice. If it is absent, the voice
  rules in SKILL.md are enough; do not stop for it.

## Diagrams

- Call `mcp__visualize__read_me` once with `modules: ["interactive"]`, then
  `mcp__visualize__show_widget` with one small HTML diagram per picture: at most six boxes, lines
  between the boxes that connect.
- A click on a box calls `sendPrompt("<the box label>: what changed here, and what do you need from me?")`.
- On a narrow screen the boxes stack in the order of the lines.
- Without the visualize tools (terminal, headless runs), print a mermaid `flowchart LR` block with
  the same boxes and lines.

## Screenshots and videos

- With an inline view, embed each one the work saved. In a terminal, give its path as a Markdown
  link on the summary line it shows.
