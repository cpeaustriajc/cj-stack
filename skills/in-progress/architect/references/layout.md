# Layout tasks

Read this when Phase A names the task a layout task: it moves code between files and folders and changes no behaviour. It replaces parts of Phase C, the pick and Phase D in `SKILL.md`.

## Phase C for a layout task

For a layout re-architecture, where the task moves code between files and folders and changes no behaviour, show **Today** as today's file tree for the folders the task names, with the line count of each file, and mark each file the candidates move. Each candidate then has these sections instead of Usage, Public surface and Internals:

1. **Tree after**: the file tree after the moves, for the folders that change.
2. **Moves**: one line per move, `from → to`. A file move names two paths. A declaration move names `file:Name → file`.
3. **Rule after**: one line that says where each kind of code lives, then the check that keeps it true, in the target repo's own mechanism (its lint rules, guards or tests).
4. **Red flags** and 5. **Tradeoff**, as above.

A move changes no line except import statements, export keywords and import paths. A candidate that needs any other edit to compile is not a layout candidate: name that edit under its Red flags.

## Pick a layout

The owner replies `Pick A` or `Pick B` on layout candidates. Work on a branch, never the trunk. Save every output below to the project's work folder.

Before step 1, run `git status --porcelain`. If it prints anything, stop and tell the owner to commit their own work first: step 3 stages everything and the undo restores tracked files to `HEAD`, so uncommitted edits would be lost.

1. Before any move, run the repo's typecheck and tests. Save each exit code and the names of the failing checks.
2. Do every move in the picked sketch: `git mv` for a file, a verbatim cut and paste for a declaration. Add only the import and export lines the moves force. Change no other line.
3. Stage everything and run `python3 -I <base directory of this skill>/scripts/moves_only.py HEAD` from the repo root. It must print `moves only`.
4. Run typecheck and tests again. They must give the same result as before: the same exit codes and the same failing checks.
5. Commit the moves as one commit that holds moves only.
6. Add the rule's check in a second commit, in the target repo's own mechanism. Read the repo's instructions first: its guards can be owner-protected. If the repo forbids a new guard, use the closest allowed check (a lint rule or a test) and say so. Show that the check passes on the moved tree and fails on a change that breaks the rule, then drop that change.
7. Fill the rationale's "Pick decision" section and save the rationale as the pull request body to come.
8. Stop. Report the two commits, the before and after results, the check's failing proof and the rationale path. Do not build other code and do not push: the owner reviews the moves first.

If step 3 or step 4 fails, or typecheck passes only after an edit that step 2 does not allow (a changed route path, a renamed symbol, a body change, a broken import cycle), a move needs a logic edit. Undo every move: restore the tracked files to `HEAD` and delete the files the moves created. Commit nothing. Tell the owner which move needs which edit, then return to Phase B of `SKILL.md` with that edit as a constraint for both runners, and stop again at Phase C.
