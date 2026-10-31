# Claude Code

## Spawns

| Role | `Agent` call |
|---|---|
| Explorer | `subagent_type: "Explore"`, `model: "haiku"` |
| Explainer | `subagent_type: "researcher"`, `model: "sonnet"`; if `researcher` is not listed, `Explore` with `model: "sonnet"` |

- Both agent types have only read tools, so no spawn can change a file. Never use
  `general-purpose` here: it can edit.
- Never `model: "opus"`: the main session presents. Models follow dotfiles's `models/README.md`.
- Send every explorer `Agent` call in one message, so they run in parallel.

## Stepper

- Call `mcp__visualize__read_me` once with `modules: ["interactive"]`, then
  `mcp__visualize__show_widget` with an HTML stepper.
- One box per numbered stage: its title, its prose, and the files and functions it names. Back and
  Next buttons move one stage; a row of stage dots shows where you are.
- A click on a box calls `sendPrompt("/how <the stage title>: <one follow-up question about it>")`.
- Without the visualize tools (terminal, headless evals), print the stages as a numbered list and a
  mermaid `flowchart LR` block with one node per stage.
