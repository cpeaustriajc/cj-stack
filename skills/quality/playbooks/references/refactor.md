# Refactor

1. State the goal as what gets easier: fewer files to read, one source of truth, a boundary
   made explicit. "Cleaner" is not a goal.
2. Pin today's behaviour before touching code: the end-to-end checks covering every surface
   the code reaches. A passing typecheck is not a pin. If no check covers a surface, write one
   first. Save the before evidence.
3. Subtract first: delete dead code, wrappers with one caller and orphan references before
   you reshape (Subtract Before You Add). Commit in this order: subtraction, reshape, cleanup.
   Change in small steps, each ending green. Migrate every caller, then delete the old path in
   the same task. No compatibility shims or re-exports unless a caller outside the repo needs
   one.
   After a rename, grep strings, docs and config for the old name too.
   Grep stops at these readers, so check them by hand: library source at the pinned version,
   JSON, database and wire-format readers, feature flags, and teardown timing.
   Also name the one fact the change's safety depends on, such as "no caller passes null
   here". Say how well it's verified (assumed, read in code, covered by a test, or seen
   running) and end with the cheapest test that would catch it if it's wrong.
4. Stay inside the asked scope. Note other smells in one line for later; don't fix them now.
5. Re-run the pins. Behaviour must be identical, and any difference is a bug in the refactor.
   Rewrite tests to the new contract, and delete tests that only pin old internals (Test
   Behavior Not Implementation).
6. If the diff doesn't make some code easier to read, revert it and say why.
7. Report what got simpler (the files or layers a reader no longer needs), plus the pin evidence.
