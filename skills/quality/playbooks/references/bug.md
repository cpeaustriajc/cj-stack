# Bug

1. Restate the bug as observed behaviour: who, where, what they did, what they saw, and what
   they should have seen. If the spec or design says what should happen, that wins.
2. Reproduce it on the same surface it was reported on (the same page, device size,
   account type and data). Not reproduced means not understood: say so and stop, rather than
   fixing a guess. After the fast repro, list hypotheses ranked by likelihood times
   cheapness to test, and change one variable at a time.
   Then minimise: remove one input, step or piece of data at a time and re-run. Stop when
   removing any part that is left makes the bug go away.
   Tag each temporary debug log with one unique prefix, such as `[DBG-7c1e]`, so one grep
   finds all of them.
3. Capture the repro as an end-to-end check that fails now. Save its evidence. Take the
   expected value from the report, the spec or a worked example, never from the code under test.
4. Find the root cause and name it in one line. Fix the source, not the symptom. A guard,
   retry or `?.` that hides the failure is not a fix.
   Also name the one fact the fix's safety depends on, such as "no caller passes null here".
   Say how well it's verified (assumed, read in code, covered by a test, or seen running)
   and end with the cheapest test that would catch it if it's wrong.
5. Commit the failing repro check before the fix, or in the same commit with the fix after
   it, so the history shows the check failing first.
6. Re-run the repro (it must pass) and the checks for the surrounding feature. Save the evidence.
   Before the commit, clean up:
   - `grep` the debug prefix: no tagged log is left.
   - Throwaway scripts and harnesses are deleted or moved to `.claude/work/`.
   - The commit message names the hypothesis that proved true.
7. Report: the root cause, the fix, the evidence path, and the command to re-run it. Add the
   case to the feature file's "What tends to break" if it isn't there.
