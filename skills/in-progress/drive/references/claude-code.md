# Claude Code adapter

Mechanics checked against the Claude Code docs in October 2026; read the current pages when a
detail matters, since these change.

## `/goal` runs the loop

`/goal <condition>` (https://code.claude.com/docs/en/goal) keeps the session working until the
condition is met. After each turn a small fast model reads the condition and the conversation and
answers not yet, met, or impossible. One goal per session; `/goal` alone shows its status, `/goal
clear` ends it.

- **The evaluator reads the transcript only.** It runs no command and opens no file. So the
  condition asks for the check's output to be shown: write it as "`<check command>` has been run
  after the last change and its pasted output shows <end state>", never "the tests pass".
- **There is no built-in budget.** Put it in the condition: "or stop after 20 turns", and the
  evaluator judges it from the conversation. Use `--max-budget-usd` for a hard spend cap on a
  headless run.
- **Compile section 2 into one condition**: the Done when line as pasted check output, the Holds
  throughout lines, the Floor, and the Budget clause, in that order. End it with "and the report
  opens with section 8's Attention list", or the goal clears before the audit runs.
- **It doesn't change permissions.** An unattended run needs auto mode, or the loop stalls on the
  first prompt.
- **It survives `--resume`**, but its turn count and timer start over, so a turn budget restarts
  too; the log on disk is the real count.

## A check the evaluator can't fake

For a run that matters, add a Stop hook of `type: "agent"` (https://code.claude.com/docs/en/hooks-guide)
that runs the check itself and blocks the stop until it passes. That is section 7's separate
checker. Agent hooks are experimental; a command hook running the check script also works.

Claude Code overrides a Stop hook after it blocks eight times in a row, and ends the turn. Each
tool call resets the count. `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` sets the cap, and a `/goal` run can
hit it: the user's settings may set it lower than 8. For a long run, raise it for that run
(`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=20 claude`), or set `0` to turn it off and rely on section 6's
brake instead.

## The handback audit

`/goal`'s evaluator can't do section 8: it calls no tools, reads only the conversation, and returns
a verdict with one short reason. No built-in audits a log. Start one `general-purpose` `Agent`
with `model: "sonnet"`, never `haiku`: weighing each row against scattered tool calls is reading
and judging, which is Sonnet's job; Haiku finds files.

- **Transcripts** are `~/.claude/projects/<cwd with / and . as ->/<session id>.jsonl`, one JSON
  object per line. The current session is the newest file there; the resume note lists the
  earlier ones. Point the auditor at `"type":"tool_use"` lines for the commands and edits, and at
  `"tool_result"` lines for their output, and have it cite `grep -n` line numbers.
- **Give it only** the paths of the log, the plan and the transcripts, and section 8's three flags
  and line shape. Not the diff, not your summary: it must read the trail, not your story.
- **Paste its list as it came back.** Don't drop or soften a flag; answer one under it in the
  report.

## Waiting on something outside

A pass that waits on CI, a deploy or a long job uses `/loop` without an interval, so Claude paces
itself with `ScheduleWakeup`, rather than a goal that polls. Self-paced loops end after one missed
wakeup and are not restored on resume.

## With cj-stack mods

- **`session-modes`**: `/mode no-pr` suits a loop whose work I review before a pull request.
