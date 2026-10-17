# Build the Lever

**When:** any work that is not trivial: edits across files, a migration, an analysis, a check.
Trivial means a few clear edits that you can see at one look. The bar is triviality, not
repetition.

**Rule:** Build the tool that does the work or proves it: a codemod, a script, a generator, a
query or a rerunnable check. A reviewer runs the tool; hand edits can only be checked again by
hand.

- Do the first unit by hand. Then build the tool, run it on that unit, and diff its result
  against yours.
- Make the tool safe to run again. Build the smallest script, not a framework.
- If one script can do every unit, run it yourself. Do not give subagents work that a script
  can do.
- When subagents share work, write the recipe, the check and the files they must not touch in
  one file that they all read. Keep that file outside their write scope.
- Commit the tool if the work continues after this session.

**You skipped it when:** you cite this principle and the diff has no script, codemod,
generator or recipe file.

**Not:** [Prove It Works](prove-it-works.md) checks the final output. This principle applies
to the work itself.
