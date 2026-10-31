# Maintain a formal check

When the code changes and the model does not, the check can keep passing on code that no longer
exists. That pass looks like a proof. This pass handles the changes that skipped the verify skill:
merges, edits without it, drift across many commits.

Edit only the verification (models, harnesses, properties, the verify skill). Never edit product
code unless the user asks. Never weaken a property or a model to make it pass.

## Pass

1. **Find the checks.** Find each project skill that runs a verifier against named code. Note the
   property, covered code, bounds, command and sync commit. No sync commit: use the last commit
   that changed the verification files, and say so.
2. **Run it as it is.** Record the result. A pass shows only that the old description holds.
3. **Read each change to covered code** since the sync commit, with its message. Follow renamed,
   split or moved code, and new code that writes the guarded state. Sort each change:
   - no effect on what the model describes (check against the model, not the message);
   - the model no longer matches (a step split, a branch or path added, a check moved);
   - the promise changed on purpose, with evidence (doc comment, tests, changelog, message);
   - the promise may be broken: no evidence of intent.
4. **Update from the code, not from the result.** Write the update before you rerun. Change a
   property only for an intended promise change: record old wording, new wording and evidence.
   Keep the bounds; if you must reduce one, report it.
5. **Rerun.** Pass: break the new code the way the property guards against and see the check catch
   it, then drop the break. Fail: replay the counterexample on the real code step by step. A step
   that cannot occur means the model is wrong; fix it. If all steps occur, it is a bug: name the
   commit that caused it, the steps in the code's words, and the harm.
6. **Update the verify skill**: covered code, commands, bounds, sync commit (not for a blocked
   check). Follow it once as the next agent would.

## Report

Per check, one outcome: **in sync**, **updated**, **bug** (can be with updated) or **blocked**
(say why). Add the commits read, each model change and its reason, the break that proved the
check can fail, each bug as steps with its harm and commit, and what is still not covered. If a
check passed before the update and fails after, say the old pass was on a stale description. Put
verification updates in their own change, apart from any product fix.
