# principle-build-the-lever

A skill that holds one engineering principle, Build the Lever. You type its name, and Claude reads the rule and applies it.

> In progress: not shipped in any plugin.

## When to use it

Use it when you want Claude to apply Build the Lever to the work in front of it. To find the right principle first, use the `principles` skill: it lists all 20 and says when each applies.

## Example

You type `/lab:principle-build-the-lever` and name the work. Claude reads the rule, applies it, and names the decision that the rule changed.

## Install

No plugin ships this skill yet. To try it for one session, link it into a local plugin folder named `lab` from a clone of this repository:

```
mkdir -p /tmp/lab/skills && ln -sfn "$PWD/lab/principle-build-the-lever" /tmp/lab/skills/principle-build-the-lever
claude --plugin-dir /tmp/lab
```

Link more lab skills into `/tmp/lab/skills/` to try them together. The skill then loads as `/lab:principle-build-the-lever`.

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
