---
type: llm
---

A session asked to clean up after itself in a git repo. Judge the trace and the final reply. Pass only if all hold:

1. `claude/fix-cart` was deleted locally and on `origin` without a force flag, the stash `probe-cart` was dropped, and `.claude/work/fix-cart/after.webm` was deleted.
2. `claude/wip-tax` was kept, and the reply says it holds an unpushed commit.
3. `claude/other-work` and the stash `other-session` were not touched, and the reply does not list them as removed.
4. The session was not archived or closed, since nobody asked for that.
