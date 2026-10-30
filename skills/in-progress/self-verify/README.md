# self-verify

A skill that sets up your project's own `verify` skill. An agent then proves its change works before commit. A fresh agent checks that proof before merge.

> In progress: only in the opt-in `cj-lab` plugin.

## When to use it

Few people read the diff of every PR. So the agent that writes a change must prove it with a command that you can re-run. This skill sets up that proof and keeps it current.

Claude loads it on phrases such as:

- "set up verification"
- "make agents verify their work"
- "agents keep claiming done without proof"
- "set up PR verification"
- "audit the verify skill"

- For one bug fix, use `playbooks`.
- For one feature file, use `feature-files`.
- For a periodic sweep for bugs, use `bug-hunt`.

## Example

You say: "Set up PR verification for this repo."

1. Claude reads your feature files and asks once where the full E2E suite runs, and when.
2. Claude writes `.claude/skills/verify/SKILL.md` in your project.
3. Claude runs it once on one feature and keeps the evidence.

You get the new `verify` skill and one result line per feature: `VERIFIED`, `NOT VERIFIED` or `BLOCKED`. Each line has the re-run command and an evidence path.

## Install

The `cj-lab` plugin lists this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-lab@cj-stack
```

To turn it off, run `claude plugin disable cj-lab@cj-stack`. This also turns off the other `cj-lab` skills.

## What it does

- Claude rejects tests that pass without proof, such as a test whose only assertion is `toBeTruthy`.
- Claude reads the real exit code of the test runner. Zero tests run counts as `NOT VERIFIED`.
- A fresh agent looks at each screenshot or output before the result line. If it cannot see the claimed state, the line is `NOT VERIFIED`.
- A weekly audit first starts one read-only agent per feature file to compare the file with the code. Another agent lists new routes, commands and screens that no feature file names.
- The audit then drives every feature in the live app. It ends as clean, changed (one PR for feature files and the verify skill only) or blocked.
- A fresh agent posts a PR verdict: `PASS`, `PASS+NOTES`, `FAIL` or `BLOCKED`. The comment holds the head SHA and the `git patch-id`. A changed or removed test assertion that the PR body does not name is a `FAIL`.
- Each `FAIL` ends with one prevention proposal. Nothing is applied until you accept it.

## Limits

- It has no 21-step ship pipeline and no always-on browser daemon.
- It does no coverage scoring and no hourly audit loops.
- The weekly audit never edits product code.
- Claude Code runs a skill named `verify` before each commit from v2.1.286. A plugin skill does not count, so the skill lives in your project.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method.
- [references/claude-code.md](references/claude-code.md): the pre-commit run, the weekly audit, the agent models and the stronger gates.
- [references/verify-template.md](references/verify-template.md): the template for the project's `verify` skill.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
- [../evals/self-verify-audit-drift](../evals/self-verify-audit-drift) and [../evals/self-verify-wrong-capture](../evals/self-verify-wrong-capture): `claude plugin eval` cases for the audit and the evidence review.
