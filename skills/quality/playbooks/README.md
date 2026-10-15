# playbooks

A skill that gives Claude a fixed list of steps for five kinds of work: bug fix, refactor, performance fix, feature and prototype. Each list ends in proof you can check.

## When to use it

Claude loads this skill at the start of a task bigger than a one-line change. Use it when you want each kind of work to leave evidence, not a claim.

- Bug fix: the bug is reproduced before the fix.
- Refactor: today's behaviour is pinned before the code changes.
- Performance fix: a measured baseline exists before the first change.
- Feature: each slice is checked in the running app.
- Prototype: you see the design options before any app code.

Do not use it to split a spec into tickets: use `tickets`. Do not use it to hunt for bugs as a careless user: use `break-it`. Do not use it to explain code.

## Example

You say: "Fix the bug where the cart empties after login, reproduce it first."

1. Claude names the playbook in one line: bug.
2. Claude copies the playbook steps into the task list and works them in order.
3. Claude writes an end-to-end check that fails, commits it, then fixes the root cause.

You get a report with the root cause, the fix, the evidence path and the command that re-runs the check.

## Install

The `cj-stack` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-stack@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-stack@cj-stack`. This also turns off every other skill in `cj-stack`.

## What it does

The skill writes no files of its own. It changes how Claude plans and reports.

- Claude picks one playbook and says which one. If the task has two kinds, the bug playbook runs first and the refactor becomes its own task.
- Claude copies the playbook steps into the task list. A skipped step stays in the list with the reason.
- A check ends as VERIFIED, NOT VERIFIED or INCONCLUSIVE. INCONCLUSIVE never counts as a pass.
- Evidence is a command you can re-run, plus its trace, screenshots or video.
- Claude reads the project's feature file first, if one exists. The `feature-files` skill writes it.

The feature playbook also runs `triage` first, and `ui-polish` and `break-it` for anything with UI.

## Limits

- It does not apply to a one-line change.
- It does not write code of its own. It only orders and records the work Claude does.
- Missing evidence is reported as a gap. It never counts as a pass.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [references/bug.md](references/bug.md), [refactor.md](references/refactor.md), [perf.md](references/perf.md), [feature.md](references/feature.md) and [prototype.md](references/prototype.md): the five playbooks.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
