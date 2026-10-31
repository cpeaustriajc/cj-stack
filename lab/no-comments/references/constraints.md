# Constraint comments

Read this when the sweeper's report has a `CONSTRAINT` row (step 4 of `SKILL.md`), and when the owner replies to a constraint offer (step 7).

## Check each constraint (step 4)

Check each `CONSTRAINT` row: a comment that says `IMPORTANT`, `do not remove`, `do not change wording`, or `talk to X before changing`. Run the lab's **why** skill on its symbol, or the **how** method when the claim is about what the code does today (read `../how/SKILL.md` and follow it: `/how` is slash-only). Leave keeps about things we cannot change. If the claim is refuted, delete the comment with the accepted set. If it is still ambiguous, leave the comment in place and list it under skips as "constraint, not proven". If it is proven, offer the cheapest in-scope type, runtime, test, or CI lint that makes the comment unneeded, and leave the comment in place. Wait for interactive approval (step 7). Unattended and eval require caller pre-approval.

## Act on the owner's reply (step 7)

Act on the owner's reply. Encode nothing that the owner did not approve. Find each named constraint by its comment text near the `file:line`: an earlier commit can move it. If the text is not there, ask the owner and change nothing.
- `Encode <file:line> as <kind>`: add the encoding. Show that it passes on today's code and fails on a change that breaks the constraint, then drop that change. Delete the comment. Run the baseline checks: the same result, plus the new check passing. Commit one constraint per commit.
- `Delete constraint <file:line>`: delete the comment in a comments-only commit and report the constraint open.
