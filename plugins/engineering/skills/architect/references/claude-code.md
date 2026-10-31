# Claude Code

## Runners

| Runner | How it runs |
|---|---|
| Sonnet | `Agent` with `subagent_type: "researcher"`, `model: "sonnet"`, `run_in_background: true`; if `researcher` is not listed, `Explore` with `model: "sonnet"` |
| Opus | the main session itself, after the Sonnet `Agent` call has started |

- The Sonnet prompt holds `runner-prompt.md`, the task and the Phase A grounding, never your
  own candidate.
- Both runner agent types have only read tools. Never use `general-purpose` for the runner: it can
  edit, and no file changes before the pick.
- Never `model: "opus"` on a subagent; the session is the Opus runner. Models follow dotfiles's
  `models/README.md`.
- In the Phase A grounding, the how method's explorers and explainer use the spawns in
  `../how/references/claude-code.md`.

## Side-by-side view

- Call `mcp__visualize__read_me` once with `modules: ["interactive"]`, then
  `mcp__visualize__show_widget` with an HTML view of two columns, candidate A and candidate B.
- Each column holds the five sections in order: Usage, Public surface, Internals, Red flags,
  Tradeoff, with code in `<pre>` blocks. Its header names the model that wrote it.
- Under each column, two buttons: Pick calls `sendPrompt("Pick <A|B>")`; Push back asks for a
  reason in a text field, then calls `sendPrompt("Push back on <A|B>: <reason>")`.
- For a logic re-architecture, a full-width Today band sits above the columns: today's excerpts
  with file and line in `<pre>` blocks, each red-flagged line marked with the flag's name.
- For a layout re-architecture, the Today band holds today's file tree with line counts, and
  each column holds Tree after, Moves, Rule after, Red flags and Tradeoff.
- On a narrow screen the columns stack, A above B.
- Without the visualize tools (terminal, headless evals), print `## Today` first for a logic
  re-architecture, then `## Candidate A (<model>)` with
  its five sections as `###` headings, then `## Candidate B (<model>)` the same way. A layout
  re-architecture prints `## Today` as the file tree, and its own five sections. End with:
  "Reply Pick A, Pick B, or Push back with a reason."

## Pull request

- After the pick, open the pull request with dotfiles's `create-pr` skill, with the rationale as
  its body. Without that skill, use `gh pr create --body-file <rationale file>`.
- If a pull request is already open for the branch, `gh pr edit --body-file` replaces its body.
