# feature-files

A skill that keeps one short file per feature. The file says what exists, how to reach it, and how to drive and check it.

## When to use it

Use it when an E2E check keeps rediscovering your app. A check opens the one file for the area it touches and reads nothing else.

Claude loads it when you write or update a feature file, and when it verifies a change in the running app. `break-it` and `playbooks` read these files.

- To write the test code itself, ask Claude directly. This skill holds no test code.
- To write a spec for a project, use `shape`.
- To break a flow as a careless user, use `break-it`.

## Example

You say: "Write a feature file for the checkout area so E2E checks know how to reach and drive it."

1. Claude finds the folder the project already uses. If there is none, it proposes `docs/features/` and waits for your yes.
2. Claude reads the app and writes `checkout.md`.

You get a file under about 40 lines. Its fields are What exists, How a user gets there, How to drive it, Check, Paths to cover and What tends to break.

## Install

The `cj-stack` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-stack@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-stack@cj-stack`. This also turns off every other skill in `cj-stack`.

## What it does

- Claude writes one file per feature, named after what a user calls it. An `index.md` lists the files in a table.
- The file describes behavior a user can see. It holds no dates, statuses or ticket numbers.
- Launch steps stay out of the file. They live in the recipe that `/run-skill-generator` records, which `/run` and `/verify` follow.
- To verify a change, Claude reads the one or two files for the touched areas. It runs the Check and the Paths to cover.
- Claude saves the evidence and the command that runs the check again.
- If the app no longer matches the file, Claude fixes the file in the same change.

## Limits

- It does not document the whole app at once. You write a file for each feature the next change touches.
- It does not write test code.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method Claude follows and the file template.
- [references/claude-code.md](references/claude-code.md): the Claude Code build and launch recipe that holds the launch steps.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
