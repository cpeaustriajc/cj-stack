# Worked example

Before:

> Configuration of the proto import ratchet budget script parameters is performed via
> budget.json. Note that it's important to remember that running with --write, which updates
> the committed budget to reflect the current count, should only be done when lowering it. If
> exceeded, CI fails.

After:

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import
> protos. If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the
> budget.

What changed:

- The noun string "proto import ratchet budget script parameters" became the real file names.
- The passive "is performed" became an actor and a verb: "`budget.mjs` reads".
- The filler "Note that it's important to remember that" is gone.
- The condition "If the count exceeds the budget" comes before the result.
- "only" moved next to the word it changes: "only to lower".
- "ratchet" is gone. Rule 26 of `unslop` lists it as an abstract metaphor noun.
