# tickets

A skill that cuts a confirmed spec into thin work items. Each item can be demoed on its own and quotes the requirements it meets.

## When to use it

Use it when a spec is confirmed and you need the next piece of work. Use it also when one ticket is too long.

- You say "break this into tickets", "cut the next slice" or "write the issue".
- You say "file these bugs as issues" or "rewrite this ticket".
- A ticket does two things and needs a split.

Do not use it to write the spec or the milestones: use `shape`. Do not use it to plan a whole product: use `vision`. Do not use it to ask questions about an approach: use `grill`. Do not use it to fix the ticket's code.

## Example

You say: "Cut the next slice from the checkout spec. R4 through R7 have no ticket yet."

1. Claude opens the spec and lists which requirements existing items already cite.
2. Claude shows the slice as a list: title, requirements, what you see and what blocks it.
3. You approve the slice or change its size or order.
4. Claude writes the items, blockers first, and runs the tree check.

You get work items that each hold Context, Outcome, Done When and, if needed, Out of Scope.

## Install

The `cj-stack` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-stack@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-stack@cj-stack`. This also turns off every other skill in `cj-stack`. For other agents such as Codex, run `scripts/link-skills.sh` in the repo.

## What it does

- Claude reads the spec first. If the spec is Draft, Claude cuts only prototype items for the Demo phase and says what would confirm it.
- Claude cuts the next slice only, not the whole spec. Each item is a narrow path through every layer, not one layer.
- Claude asks one question: are the size and the blocking right? Any other question goes up to `shape` as a spec change.
- Each Done When quotes the requirement with its number and has a "You see" line that says what the verifier observes.
- An item has 3 to 5 Done When checks and a body under about 1,500 characters. A longer item is split.
- Claude labels each item Task, Bug or Chore. A Chore adds a No-QA check and cites no requirement.
- A bug found after Done becomes a new item, related to the original.
- Claude writes through your tracker's adapter in `shape/references/`, then runs the tree check. Add `--launch` when the project enters Launch.

## Limits

- It cuts nothing from a Draft spec, except prototype items.
- It does not settle spec questions inside a ticket.
- Items hold no file paths and no code, because both go stale.
- It does not mark an item Done. The verifier does.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [../shape/references/top-down.md](../shape/references/top-down.md): the five rules and the tracker lookup.
- [../shape/references/tree-outline.md](../shape/references/tree-outline.md): the tree JSON that the check reads.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
