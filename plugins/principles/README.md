# principles

A plugin that gives you and Claude one vocabulary of 20 engineering principles. You steer Claude with a principle's name, and Claude names each principle that changed one of its decisions.

## When to use it

Use it when Claude is about to make a mistake that one phrase can stop.

- You say "apply prove it works" when Claude claims success because the build passed.
- You say "subtract before you add" when Claude adds a fourth adapter beside three old ones.
- You say "attack the premise" when two fixes failed for the same reason.

Claude also reads a principle on its own before a design, test, debugging or measurement decision.

## Example

You say: "Apply test behavior, not implementation to the cart tests."

1. Claude reads the principle's file.
2. Claude checks each cart test against two edits: a broken return value, and a change to internals only.
3. Claude rewrites the test that still passes when the total is wrong.

You get the changed tests and one line such as "Test Behavior, Not Implementation: rewrote `cart.test.ts` to assert the total from the spec".

## Install

In Claude Code, add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install principles@dotfiles
```

## What it does

- The `principles` skill is the index. It lists each principle with when it applies and its rule in one line.
- Each principle is a skill of its own that you can type by name, such as `/principles:principle-prove-it-works`.
- Claude cites a principle only with the decision that it changed.
- The plugin runs no scripts or hooks, and it sends and fetches nothing. It holds Markdown instructions only.

## Limits

- It does not change files on its own. It changes how Claude decides while it works.
- It holds no project rules. Your repo's own rules win where they conflict.

## More

- [skills/principles/README.md](skills/principles/README.md): the index skill, and when to use a neighbour skill instead.
- [skills/](skills/): one folder for each of the 20 principles.
- The principles are adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan, under the MIT license. See [LICENSE](LICENSE).
