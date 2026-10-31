# Claude Code

## Proof scripts

- Write each proof script in the project's gitignored work folder, `.claude/work/blast-radius/`,
  never beside the code. Run it from the project root so it imports the code the app ships.
- Paste the command, its exit code and its output in the writeup. Leave the script there, so the
  owner can run it again.
- Never edit the change's own files to prove a fact.

## Sibling skills

- `why` and `unslop` are slash-only, so the Skill tool cannot start them. Read
  `../why/SKILL.md` and `../../plugins/writing/skills/unslop/SKILL.md` and follow them.
- `interrogate` ships in cj-stack and the Skill tool starts it.

## Risk map

- Call `mcp__visualize__read_me` once with `modules: ["interactive"]`, then
  `mcp__visualize__show_widget` with an HTML map.
- The change sits in the middle: one box with its one-line summary, and the safety fact under it,
  marked proven (with its step) or unproven.
- Around it, one box per confirmed risk: how it breaks, its `file:line`, its likelihood and cost,
  and its step on the How sure are you list. A line joins each box to the change.
- The cleared risks sit apart in a muted group, labelled Cleared, each with its `file:line` and the
  reason it is fine.
- A click on a risk box calls `sendPrompt("How do I check <file:line>: <how it breaks>?")`. A click
  on a cleared box calls `sendPrompt("Why is <file:line> cleared?")`.
- On a narrow screen the boxes stack: the change, then the risks, then Cleared.
- Without the visualize tools (terminal, headless evals), print a mermaid `flowchart LR` block:
  a `change` node in the middle, one node per risk with its `file:line` and step joined to it, and
  a `subgraph Cleared` that holds the cleared nodes with no line to the change.
