# principle-minimize-reader-load

A skill that holds one engineering principle, Minimize Reader Load. You type its name, and Claude reads the rule and applies it.

## When to use it

Use it when you want Claude to apply Minimize Reader Load to the work in front of it. To find the right principle first, use the `principles` skill: it lists all 20 and says when each applies.

## Example

You type `/principles:principle-minimize-reader-load` and name the work. Claude reads the rule, applies it, and names the decision that the rule changed.

## Install

The `principles` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install principles@cj-stack
```

The skill then loads as `/principles:principle-minimize-reader-load`.

## What it does

- Claude reads the rule in `SKILL.md`: when it applies, the rule, and the sign that Claude skipped it.
- Claude never loads it on its own. The `principles` skill reads it when the rule fits a decision.

## Limits

- It changes no file on its own. It changes how Claude decides.
- Your repo's own rules win where they conflict.

## More

- [SKILL.md](SKILL.md): the rule.
- [principles](../principles/README.md): the index of all 20 principles.
- The principle is adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan, under the MIT license.
