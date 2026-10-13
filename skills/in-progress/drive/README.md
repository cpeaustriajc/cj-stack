# drive

A skill that decides whether a piece of work should loop until a check passes. If it should, Claude runs the loop one change at a time, with a log on disk.

> In progress: not shipped in any plugin.

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

You get a report with the check's last output, the passes kept and reverted, why the run stopped, and the log path.

## Install

This skill is not shipped in any plugin, so you cannot install it yet. The repo's routing evals link it into a throwaway eval plugin, as described in `.claude/skills/run-cj-stack/SKILL.md`.

## What it does

- Claude asks you to approve the exit check before any change.
- Claude freezes the check. The loop never edits the check, its tests or its data.
- Claude writes a plan file, a gitignored `drive.tsv` log and a resume note.
- A run stops when it is stuck, out of budget or blocked by a rule it must keep.
- A fresh reviewer confirms a run that matters before Claude says it is done.

The Claude Code adapter turns the exit check into a `/goal` condition. It can also add a Stop hook that runs the check itself.

## Limits

- It does not deploy, delete data, take payments or message people inside the loop.
- It does not relax the exit check to finish a run.
- A `/goal` evaluator reads only the transcript, so the check output must appear there.
- The `loop-brake` mod can cap a `/goal` run. The adapter explains how to raise or turn off that cap.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method.
- [references/claude-code.md](references/claude-code.md): how to run the loop with `/goal`, Stop hooks and `/loop`.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
