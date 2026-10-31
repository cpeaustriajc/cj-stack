# formal-verify

A skill that model-checks the code where a bug costs the most and tests reach the least. It leaves a project skill that the next agent runs on each change to that code.

## When to use it

A change to a retry, a race, a lease or a state machine can pass every test. No test reaches the bad order of steps. A model checker tries every order in a stated scope.

Claude loads it on phrases such as:

- "model-check this race"
- "prove this invariant"
- "formally verify the lease logic"
- "is the model still true to the code"

- For a verify skill that drives the real app, use `self-verify`.
- For one bug fix, use `playbooks`.
- For a hunt across the whole codebase, use `bug-hunt`.

## Example

You say: "Formally verify the job lease logic and leave a check for the next agent."

1. Claude picks the promise from the code: one job runs on one worker at a time.
2. Claude writes a small TLA+ model, runs TLC and shows the check fail on a broken variant.
3. Claude writes a project skill with the run command, the covered files and a sync commit.

You get each bug as a list of steps in the code's words, the bounds, and what the check does not cover.

## Install

The `engineering` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install engineering@dotfiles
```

The skill then loads as `/engineering:formal-verify`.

## What it does

- Claude chooses the tool from the question: TLA+ for the order of events, a code verifier for every input.
- Claude shows each property fail on a broken variant before it trusts a pass.
- Claude reports a bug in the current code as a finding. It never weakens the property to make the check pass.
- Claude writes the project skill into your repo, not into the plugin, and runs it once on a scratch break.
- In maintain mode, Claude reads each commit since the sync commit and gives each check one outcome: in sync, updated, bug or blocked.

## Limits

- Known defect: in the 2026-11-01 `formal-verify-lease-race` run, the plugin run failed the `product-untouched` grader. Its clean product code is unproven.
- The skill edits product code for a scratch break, then reverts it. The 2026-11-01 run did not show the revert with `git status`.
- A pass covers the model and its bounds, not the whole system.
- It does not install a model checker for you outside the run. The project skill names the command.
- It has no settings.
- It is untested. On 2026-11-01 the lease-race case scored 0.67 with the plugin and 0.67 without it, in one run each.
- Only the run with the plugin wrote a project verify skill with a sync commit. Both runs found the race.

## More

- [SKILL.md](SKILL.md): the create mode.
- [references/maintain.md](references/maintain.md): the maintain pass.
- [../../evals/formal-verify-lease-race](../../evals/formal-verify-lease-race): a `claude plugin eval` case with a lease race that the tests miss.
- Source: Lauren Tan's `create-formal-verification-skill` and `maintain-formal-verification-skill` in [cursor/plugins](https://github.com/cursor/plugins/tree/519d36aa98955bf680db01bcde5fdfba686dc901/pstack/skills), commit `519d36a`, MIT. Evidence: the eval scores in Limits, a tie so far.
- Not adopted: Lauren Tan's `statechart` skill. A run without the plugin passed its checkout case (score 1.0), so it showed no gain.
