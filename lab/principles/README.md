# principles

A skill that gives you and Claude one vocabulary of 20 engineering principles. You steer Claude with a principle's name, and Claude names each principle that changed one of its decisions.

> In progress: shipped in the `lab` plugin, and can change at any time.

## When to use it

Use it when Claude is about to make a mistake that one phrase can stop. The name points at a full rule that Claude reads before it acts.

- You say "apply prove it works" when Claude claims success because the build passed.
- You say "subtract before you add" when Claude adds a fourth adapter beside three old ones.
- You say "attack the premise" when two fixes failed for the same reason.

Claude also reads a principle on its own before a design, test, debugging or measurement decision. Do not use it to pick the steps for a bug or a refactor: use `playbooks`. Do not use it to review a diff: use `interrogate`.

## Example

You say: "Apply test behavior, not implementation to the cart tests."

1. Claude reads the principle's file.
2. Claude checks each cart test against two edits: a broken return value, and a change to internals only.
3. Claude rewrites the test that still passes when the total is wrong.

You get the changed tests and one line such as "Test Behavior, Not Implementation: rewrote `cart.test.ts` to assert the total from the spec".

## Install

The `lab` plugin ships this skill:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install lab@cj-stack
```

The skill then loads as `/lab:principles`.

## What it does

- The index in `SKILL.md` lists each principle with when it applies and its rule in one line.
- Each principle is a skill of its own, such as `principle-prove-it-works`. You can type one by name: `/lab:principle-prove-it-works`.
- Each principle's file says when it applies, the rule, the sign that Claude skipped it, and the neighbour principle it is not.
- Claude reads the file before it applies the principle.
- Claude cites a principle only with the decision that it changed. A name with no decision is left out.

## Limits

- It does not change files on its own. It changes how Claude decides while it works.
- It holds no project rules. Your repo's own rules win where they conflict.
- It leaves out two pstack principles that the cj-stack setup covers already: Guard the Context Window and Never Block on the Human.

## More

- [SKILL.md](SKILL.md): the index and the citation rule.
- [principle-prove-it-works](../principle-prove-it-works/README.md) and the 19 other `principle-*` folders: one skill per principle.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
- The principles are adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan, under the MIT license.
