# PR verdict

Read this before you give, or set up, the verdict on a PR. The evidence rules in `SKILL.md` apply to it.

A fresh agent that did not write the change runs the project verify skill on the PR head. For any
check that fails, it also runs that check on the base.

The verdict is PASS, PASS+NOTES, FAIL or BLOCKED. Post it as one PR comment with the head SHA and
the `git patch-id`. A later push that changes the patch-id voids the verdict.

Green CI or a bot approval is not a verdict.

The verifier reports only correctness and spec gaps. Asked for gaps, a reviewer always finds some;
do not add style notes. The verifier also checks that the PR body's Evidence line re-runs. The
`create-pr` step writes the Evidence, Merge danger and Test changes lines.

The verifier diffs every test file between base and head and asks: did any assertion get weaker?
Each changed or removed assertion line that the Test changes line does not name is a FAIL. A named
one is PASS+NOTES, with the old and new line quoted.
