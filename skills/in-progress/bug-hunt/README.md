# bug-hunt

A skill that sweeps a codebase for real bugs. Three parallel reviewers search, fix each bug test-first, and search again until a full round finds nothing.

> In progress: not shipped in any plugin.

## When to use it

One review pass finds some bugs and hides the rest behind them. Each fix also changes the code that the next pass reads. This skill repeats the hunt until a round comes back clean.

Claude loads it when you say "bug hunt", "deep code review", "audit the codebase", "hunt for bugs until clean" or "find and fix every bug".

Run it as a periodic sweep: nightly, weekly or on demand.

- For proof that one change works before merge, use `self-verify`.
- For a report-only review of one diff, use `interrogate`.

## Example

You say: "Bug hunt the whole repo until a round comes back clean."

1. Claude splits the files into three shards and starts three reviewers at once.
2. Each reviewer fixes the bugs in its own shard, test-first, and reports bugs elsewhere.
3. Claude checks the fixes, runs the test suite, then starts the next round with rotated shards.

You get a report with the coverage percent, the rounds run, the verified bugs with their commits and tests, and the exact E2E command.

## Install

This skill is not shipped in any plugin, so you cannot install it yet.

## What it does

- Claude writes the file list, the bug ledger and every reviewer reply to the ignored work folder (`.claude/work/<topic>/` in Claude Code). It tells you where.
- Each reviewer reads the whole scope but edits only its own shard.
- A bug without a failing test stays unproven. The reviewer reports it and does not fix it.
- Claude commits each verified fix on its own, if the project allows commits.
- Claude proposes one prevention per verified bug: a lint rule, test, hook or instruction change. You decide.
- The hunt stops after one clean round at 100% coverage. It also stops and asks you after 5 rounds.

## Limits

- It is not a per-PR gate.
- It does not give a report-only review.
- It does not use `/code-review` as a reviewer, because that command has a usage cap.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method.
- [references/claude-code.md](references/claude-code.md): how Claude starts the reviewers in Claude Code.
