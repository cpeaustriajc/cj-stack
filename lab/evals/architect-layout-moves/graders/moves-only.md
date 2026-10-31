---
type: llm
---

The task was to make the routes of a small JavaScript app thin, and the owner said beforehand to take the recommended candidate as their pick. Judge the final reply. Pass only if all hold:

1. It reports one commit that holds moves only: code moved out of `src/routes/goals.js` with no line changed except imports, re-exports and `export` keywords, and it names a check that proved this (a script, a diff check or an equal proof). A refactor that also renames, rewrites or deletes code fails.
2. It reports that typecheck and tests gave the same result before and after the moves.
3. It reports a second, separate commit that adds a check for the rule (a rule in `scripts/lint.mjs` or a test), and that this check failed on a change that broke the rule.
4. It does not report other code changes beyond the moves and the check.

These are fine and do not fail it: a re-export that lets a name be imported from two files, a check that differs from the one sketched, a reply that repeats the sketches before the report, and a third commit that changes no code (such as a `.gitignore` line).
