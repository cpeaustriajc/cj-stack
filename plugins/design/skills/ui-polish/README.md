# ui-polish

A skill that reviews a UI against its design and a list of common mistakes. It reports a Before/After/Why table and one verdict.

## When to use it

Use it to review a screen against its design, to polish spacing, type, colour or motion, and before you ask for visual sign-off.

- To test a flow as a careless user, use `break-it`.
- To build a screen from a design, ask Claude directly. This skill only reviews.
- To fix a bug, use `playbooks`.

## Example

You say: "Review the new pricing page against the Figma frame before I sign off."

1. Claude finds the design and opens the page in a browser at the real width and at 375px.
2. Claude checks the page against the mistake list and the reference files for motion, interaction and dense app screens.
3. Claude replies with a table and one verdict.

You get one row per issue, most visible first. Each row has Where, Before, After and Why, and the Why names the rule it breaks. The verdict is Ship, Ship after the top N, or Rework.

## Install

The `design` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install design@cj-stack
```

To turn the plugin off, run `claude plugin disable design@cj-stack`. This also turns off every other skill in `design`.

Requirement: a browser that Claude can drive, so it sees the real screen.

## What it does

- The design is the source of truth: a mockup, a Figma frame, a screenshot you give, or the closest screen in the app.
- Claude checks the screen in light and dark, if the app has both.
- A row cites `file:line` when the issue is in code, and carries a screenshot when the issue is visual.
- For a visual change, Claude puts before and after screenshots in the PR body, and you sign off when you review the PR. Claude waits before it commits only when the project requires that, or when the commit goes straight to the trunk.

## Limits

- It reviews and reports. It changes nothing until you name the rows to fix.
- If no design exists, Claude says so and judges against the existing screens.
- A tradeoff that the code or design documents is mentioned in the row but not flagged as a mistake.
- It does not test a flow with bad input or odd user behavior.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [references/motion.md](references/motion.md), [interaction.md](references/interaction.md) and [app-ui.md](references/app-ui.md): the rules Claude checks.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
