# hone

A skill that reads your past Claude Code transcripts, finds the corrections you repeat, and proposes where each lesson should live. It changes nothing until you approve.

## When to use it

Use it when you tell Claude the same thing in many sessions and want a fix that lasts.

- You ask "what do I keep correcting" or "why does Claude keep doing X".
- A session had several corrections.
- You type `/hone <skill>` to review only the corrections you made while one skill ran.

Do not use it to update `CLAUDE.md` from one session. A correction from a single run does not qualify. Do not use it to review a diff: use `interrogate`.

The optional [hone-nudge](../../../mods/hone-nudge/) mod suggests `/hone <skill>` after you correct Claude during a cj-stack skill run.

## Example

You say: "hone the shape skill from the corrections I made while it ran last week."

1. Claude collects your corrections from the transcripts and writes them to one markdown file.
2. Claude reads the `shape` skill and keeps the patterns that recur.
3. Claude proposes a fix for each pattern, in the strongest place that can hold it.

You get three groups: Accept?, Backlog and Rejected. Claude asks which proposals to apply and applies only those.

## Install

The `cj-stack` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-stack@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-stack@cj-stack`. This also turns off every other skill in `cj-stack`.

## What it does

- It reads the transcripts in `~/.claude/projects` and skips folders with `-private-` in the path.
- It runs `scripts/corrections.py`, which needs Python 3, prints progress and writes one markdown file of exchanges.
- The script flags interrupted requests, rejected tool calls, dismissed forms and replies that open with "no", "why", "stop" or "don't".
- Stop-hook feedback appears as `HOOK`, so a hook loop can become a lesson too.
- The script accepts `--project <substring>`, `--since <YYYY-MM-DD>` and `--skill <skill>` to narrow the search.
- A lesson qualifies when it shows up in 2 or more sessions, or once with an obvious cost.
- Each proposal names a place, from strongest to weakest: code, lint, hook, test, skill, agent definition, instruction file.
- A proposed lint, test or hook must first fail on a real past instance of the mistake.
- It also proposes lines to remove, starting from `/doctor prompt-audit` for Claude Code.

## Limits

- It applies nothing without your approval.
- It reads only transcripts on this machine.
- The exchange file holds raw text from your sessions, so it can hold secrets. Do not share it.
- To change a skill, edit its source repo, not the installed copy in the plugin cache.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [references/claude-code.md](references/claude-code.md): the Claude Code audit commands it starts from.
- [scripts/corrections.py](scripts/corrections.py) and [scripts/test_corrections.sh](scripts/test_corrections.sh): the extractor and its test.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
- [mods/hone-nudge](../../../mods/hone-nudge/): the optional mod that suggests `/hone <skill>`.
