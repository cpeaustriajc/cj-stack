---
name: no-comments
description: "This skill should be used when the user types /no-comments with a folder of old code: spawn the sweeper, fix accepted findings, land comment deletions, suppression removals and reshapes as separate commits with the same test results, offer encodings for claimed constraints, and hand each MUST KILL to /architect."
disable-model-invocation: true
argument-hint: "<folder>"
---

# No comments

Spawn the sweeper. Act on accepted findings.

Defer to the sweeper's fresh perspective.

The scope is `$ARGUMENTS`. Tool mechanics (spawn calls, models) are in `references/claude-code.md`.

## Scope

Use the folder in the arguments: every tracked source file below it. Otherwise use the caller's files or diff. Otherwise use the current diff against the base branch, default `main`, including the working tree.

## Steps

1. Prepare. If `git check-ignore -q <work folder>` fails, add the work folder to `.git/info/exclude`. Never edit `.gitignore`: a sweep commits only in-scope files, so that edit stays behind and stops the next sweep. Run `git status --porcelain`. If it prints anything outside the project's work folder, stop and tell the owner to commit their own work first. Run the repo's typecheck, lint and tests (from its README, package scripts or instructions) and save each exit code and the names of the failing checks to the project's work folder. This is the baseline.
2. Spawn the sweeper with `references/sweeper-prompt.md` and the scope. Do not restate its rules. The sweeper changes no file; it returns a report.
3. Inspect its report. Reject application-code edits, scope escapes, exception-protected deletions, misstated `MUST KILL` reasons, and flags that treat kept intentional code as guilty. Reshape flags on our-code surprises stay actionable. Do not restore those comments. A keep survives only with proof it is about something we cannot change. Audit missed scoped lint and TypeScript suppressions. Correctness or safety suppressions stay actionable `MUST KILL`s. Restore deletions only with exact exceptions and scoped proof. If a kill is ambiguous, do not restore. Rerun the sweeper once on a rejected report with the failure named. Reject a second, report it open, and fail `/no-comments`.
4. Check each `CONSTRAINT` row: a comment that says `IMPORTANT`, `do not remove`, `do not change wording`, or `talk to X before changing`. Run cj-lab's **why** skill on its symbol, or the **how** method when the claim is about what the code does today (read `../how/SKILL.md` and follow it: `/how` is slash-only). Leave keeps about things we cannot change. If the claim is refuted, delete the comment with the accepted set. If it is still ambiguous, leave the comment in place and list it under skips as "constraint, not proven". If it is proven, offer the cheapest in-scope type, runtime, test, or CI lint that makes the comment unneeded, and leave the comment in place. Wait for interactive approval (step 7). Unattended and eval require caller pre-approval.
5. Land the accepted set as up to three commits, in this order, on a branch, never the trunk. On the trunk, create one named by the repo's branch rule, else `no-comments/<folder>`. Each commit holds one kind of change only. Stage only the files you changed in scope, never the work folder:
   1. **Comments**: delete each accepted comment. Change no code token.
   2. **Reshapes**: fix trivial accepted `MUST KILL` flags directly by deleting a dead path, dropping a parameter that no caller passes (search the whole repo, not only the folder), or using the real API. Implement the smallest root-cause fix in scope. Remove every named workaround. Never bolt on symptom guards. A flag that needs a new shape gets no edit: report it open for `/architect`. Architect shapes; this run builds no shape.
   3. **Suppressions**: delete each accepted suppression.

   After each change, run the baseline checks again. They must give the same result: the same exit codes and the same failing checks. If a result changes, undo the item that changed it, report it open with the check that changed, and run the checks again before the commit. Never commit a changed result. Skip a commit that has nothing in it.
6. Report the deletion count (comments and suppressions together, the same number everywhere in the report), each `MUST KILL` flag in one line (`file:line symbol: reason`), and skips, each with its reason. Then the commits with their before and after results, restored comments, reruns, fixes, encoding offers, unproven and unenforced constraints, and other open work. If the sweep finds nothing, report `0 deletions in <folder>`, the number of files read, and make no commit.

   Then show the inline view from `references/claude-code.md`. Its `file:line` values are the lines after the commits of step 5, not the sweeper's lines:
   - Each `MUST KILL` as the deleted comment beside the code it excused, with its reshape line, its commit if a reshape fixed it, and one action that sends it to `/architect`. The action's task names the logic re-architecture: the symbol, its file, the reshape and the deleted comment. `/architect` stops at its sketches.
   - Each proven constraint as its comment beside its code, the evidence for it, and the offered encoding, with an Encode and a Delete action.

   If the view holds a constraint offer, end the turn and wait.
7. Act on the owner's reply. Encode nothing that the owner did not approve. Find each named constraint by its comment text near the `file:line`: an earlier commit can move it. If the text is not there, ask the owner and change nothing.
   - `Encode <file:line> as <kind>`: add the encoding. Show that it passes on today's code and fails on a change that breaks the constraint, then drop that change. Delete the comment. Run the baseline checks: the same result, plus the new check passing. Commit one constraint per commit.
   - `Delete constraint <file:line>`: delete the comment in a comments-only commit and report the constraint open.

## Credit

Adapted from pstack's `no-comments` and its comment agent by Lauren Tan (MIT; see `LICENSE`).
