---
type: llm
---

The request asks for five tickets in one project, built as separate PRs, where each status
builds on the one before.

Pass only if the final message does all of these:

1. Lists the five items in one order from bottom to top, where every item that blocks another
   comes before it.
2. Names, for every one of the five items, the git branch it builds on (its base branch).
3. Gives the first item the trunk (main, master or "the default branch") as its base.
4. Gives every later item the branch of the item directly before it as its base, not the trunk.

Fail if any item has no base branch, if two or more items branch off the trunk, or if the
message only lists blocked-by links or dependencies without naming base branches.
