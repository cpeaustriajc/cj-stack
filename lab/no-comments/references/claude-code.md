# Claude Code

## Sweeper

| Role | `Agent` call |
|---|---|
| Sweeper | `subagent_type: "researcher"`, `model: "sonnet"`; if `researcher` is not listed, `Explore` with `model: "sonnet"` |

- The prompt holds `sweeper-prompt.md` with `<scope>` replaced by the folder path or file list.
- Both agent types have only read tools, so the sweeper cannot change a file. The session deletes
  what it lists. Never use `general-purpose`: it can edit.
- Never `model: "opus"`: the session judges and applies. Models follow cj-stack's
  `models/README.md`.
- A folder with more than 40 source files: split it by subfolder into two to four scopes and send
  every sweeper `Agent` call in one message, so they run in parallel. Add up their counts.

## Commits

- One `git commit` per kind, with the subject `no-comments: delete comments in <folder>`,
  `no-comments: reshape <symbols>`, `no-comments: remove suppressions in <folder>` or
  `no-comments: encode <symbol> constraint`.
- Before the comments commit, `git diff --cached -U0` must show only removed lines, or lines whose
  only change is a removed trailing comment. Read each removed text: it must be comment text (it
  starts with the language's comment marker or sits inside a block comment). A removed code line
  fails the check.

## Inline view

- Call `mcp__visualize__read_me` once with `modules: ["interactive"]`, then
  `mcp__visualize__show_widget` with an HTML view of one card per item: `MUST KILL` cards first,
  then constraint cards.
- Comment and code text comes from the swept repo. Insert it into HTML as escaped text, and build
  each `sendPrompt` argument with `JSON.stringify`, so a quote or a newline cannot break a button.
- A `MUST KILL` card: a header `file:line symbol` and its state (open, or the reshape commit's
  short SHA). Below it, the deleted comment, struck through in red, above the code it excused,
  with line numbers, in one `<pre>` block. Then the reshape line. One button, "Send to
  /architect", calls `sendPrompt("/lab:architect Logic re-architecture of <symbol> in <file>:
  <reshape>. It replaces the deleted comment: <comment text>")`.
- A constraint card: the comment above its code in one `<pre>` block, the evidence with its label
  from why or how, and the offered encoding. Two buttons: Encode calls
  `sendPrompt("Encode <file:line> as <kind>")`; Delete calls
  `sendPrompt("Delete constraint <file:line>")`.
- Without the visualize tools (terminal, headless evals), print `## MUST KILL` with one
  `### file:line symbol` per item: its state, a `diff` block with the deleted comment as `-` lines above
  the code it excused, the reshape line, and the line "Send to /architect:" followed by the same
  `/lab:architect ...` prompt in a code block. Then `## Constraints` with one `###` per item:
  the comment and code block, the evidence and the offer. End with: "Reply Encode <file:line> as
  <kind>, or Delete constraint <file:line>."
