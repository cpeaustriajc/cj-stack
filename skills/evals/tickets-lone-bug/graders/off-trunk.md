---
type: llm
---

The request asks for one bug in the team backlog, outside any project, fixed in its own PR, while
an unrelated project is being built as a stack.

Pass only if the final message does all of these:

1. Proposes exactly one item, for the broken footer link.
2. Gives it no Stack section and no slice position (no "Slice 1 of", no stack order).
3. Does not put it on, above or below any branch of the order status project. If it names a base
   branch, that base is the trunk (main, master or "the default branch").

Fail if the item is added to the order status stack, given a Stack line, or based on any branch
other than the trunk.
