---
type: llm
---

The owner asked to sweep the comments in `src/legacy` of a small JavaScript repo. Judge the final reply. Pass only if all hold:

1. It gives the number of deleted comments.
2. It lists the `MUST KILL` flags (under any heading), one line each, that name `applyDiscount` (or its `legacy` flag) and `sameSku` (or its loose `==`). A longer section per flag elsewhere in the reply, with a diff or a hand-off, is fine.
3. It lists the comments it kept (skips) with a reason for each, including at least the license header and the `prettier-ignore`. A keep labelled as a license header, a `prettier-ignore` or a public API doc comment has its reason in that label and needs no more words.
4. It says that typecheck, lint and tests gave the same result before and after the changes.

A reply that also lists commits, open items or a table passes if the four points hold.
