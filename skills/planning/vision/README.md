# vision

A skill that grills a product idea and tells you if it is worth building. It then writes the top of the plan: destination, features and order.

## When to use it

Use it when an idea is still vague and you want an honest answer before any spec exists.

- You ask "is this worth building?" or "grill me on this idea".
- You want a plan from product down to tickets.
- Something you built for yourself might sell.
- You want a product-level status update.

Do not use it to grill one change or design: use `grill`. Do not use it to write the spec for one feature: use `shape`. Do not use it to cut tickets: use `tickets`.

## Example

You say: "I want a booking tool for independent tattoo artists. Is it worth building? Grill me."

1. Claude asks a first round with one question per branch, each with a recommended answer.
2. Claude shows a feature list F1 to Fn that grows after each round.
3. Claude recommends one verdict: build, shrink, test first or don't build.
4. After you approve the draft, Claude writes the product into your tracker.

You get a product page with a destination, a verdict, features and a build order. Claude then hands the first feature to `shape`.

## Install

The `cj-stack` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-stack@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-stack@cj-stack`. This also turns off every other skill in `cj-stack`. For other agents such as Codex, run `scripts/link-skills.sh` in the repo.

## What it does

- Claude finds your tracker (Linear, Jira, GitHub or another) from `CLAUDE.md`, `AGENTS.md` or the connected tools. If it finds none, it asks once.
- Claude runs the interview from `grill` and asks the worth-it question first. A product idea is always grilled, never only sized.
- Claude puts a vague answer under "Not yet specified" and does not press it into a feature.
- Claude makes the riskiest unknown the first item of the first project, if a lookup or prototype can settle it.
- Claude writes the product with these parts: Status, Destination, Worth it, Success, Features, Sequence, Not yet specified and Out of scope.
- The product stays Draft until Worth it and Out of scope are filled and you confirm it.
- After confirmation, Claude creates one project for each feature in the first step of the Sequence. Later features wait.
- At each Launch, Claude checks the Worth it verdict again and says whether it holds.

## Limits

- It writes no spec and no ticket. `shape` and `tickets` do that.
- It writes nothing until you say the draft product is right.
- Cost and time numbers are Claude's guesses, and Claude labels them as guesses.
- It does not find an idea for you. It works on an idea you bring.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [../shape/references/top-down.md](../shape/references/top-down.md): the five planning rules and the tracker lookup.
- [../grill/SKILL.md](../grill/SKILL.md): the interview method.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
