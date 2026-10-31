# drive

A skill that decides whether a piece of work should loop until a check passes. If it should, Claude runs the loop one change at a time, with a log on disk.

## When to use it

Claude loads this skill when you say "drive this", "loop until it passes", "keep going until green", "run it overnight" or "hillclimb". It also loads when you hand over a ticket to finish unattended, or before you write a goal or a Stop hook.

Claude loops only when three things hold:

- A command, test or metric answers "done?" without anyone's judgement.
- A harness reproduces the problem now.
- Every action can be undone.

Do not use it for a timer: use `/loop`. Do not use it for product, taste or design calls. Do not use it for work that fits in one turn.

## Example

You say: "Drive cart.test.ts to green overnight, keep going until every test passes."

1. Claude shows you the exit check, with its command and budget, before the first pass.
2. Claude runs the check on the untouched code and records the baseline.
3. Claude makes one change per pass, then keeps it or reverts it, and logs the row.

You get a report. It opens with an Attention list of what to check. Then it gives the check's last output, the passes kept and reverted, why the run stopped, and the log path.

## Install

The `engineering` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install engineering@dotfiles
```

The skill then loads as `/engineering:drive`.

## What it does

- Claude asks you to approve the exit check before any change.
- Claude freezes the check. The loop never edits the check, its tests or its data.
- Claude writes a plan file, a gitignored `drive.tsv` log and a resume note.
- A run stops when it is stuck, out of budget or blocked by a rule it must keep.
- A fresh reviewer confirms a run that matters before Claude says it is done.
- Before the report, a fresh Sonnet agent compares the log with the session transcript. It lists each log row that did not happen, each action the log leaves out and each "done" with no proof. An empty list says "nothing to check".

The Claude Code adapter turns the exit check into a `/goal` condition. It can also add a Stop hook that runs the check itself.

## Limits

- It does not deploy, delete data, take payments or message people inside the loop.
- It does not relax the exit check to finish a run.
- A `/goal` evaluator reads only the transcript, so the check output must appear there.
- Claude Code's Stop-hook cap (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`, 8 by default) can end a `/goal` run. Each tool call resets the count. The adapter explains how to raise the cap for a run or turn it off with `0`.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method.
- [references/claude-code.md](references/claude-code.md): how to run the loop with `/goal`, Stop hooks and `/loop`, and how to start the audit agent.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
- [evals/handback/](evals/handback/): two `claude plugin eval` cases for the audit, one log that claims a pass the transcript never ran and one clean log. Run `plugins/engineering/skills/drive/evals/handback/run.sh` from the repo root.
