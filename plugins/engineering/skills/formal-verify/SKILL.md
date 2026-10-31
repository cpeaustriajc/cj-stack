---
name: formal-verify
description: >
  This skill should be used when the user says "model-check this race", "prove this invariant",
  "formally verify this" or "is the model still true to the code", or when a retry, race, lease or
  state machine needs more than tests. It writes or maintains a project verify skill.
---

# Formal verify

Tests check the cases someone wrote. A retry, race, lease or state machine can pass them all,
because no test reaches the bad order of steps. A model checker tries every order in a scope.

If the project has a formal check and the code changed since its sync commit, read
`references/maintain.md` and do its pass. Otherwise, create one:

1. **Target.** From the code, pick the promise where a break harms users most and tests reach
   least. Not the easiest one. Ask the user only what the code cannot tell you.
2. **Tool.** Order of events: TLA+ on a small model, in any language. The code for every input: a
   verifier that runs on the code; if none exists for the language, generated-input tests on the
   real code. Say why you chose it.
3. **Model.** Each part points to code a reviewer can open. One indivisible step in the code is
   one step in the model. Use the repo's names.
4. **Able to fail.** Show each property fail on a broken variant (a removed check, a reordered
   step). A check you never saw fail proves nothing.
5. **Findings stay findings.** If the current code breaks the property, report the counterexample
   as steps in the code's words, and the harm in one sentence. Never weaken the property or the
   model to pass. Do not change product code unless the user asks.
6. **Verify skill.** Write a project skill (with frontmatter) that tells a cold agent when a change
   touches the covered code, the one command to run, how to tell a bug from a model error, and how
   to update the model for an intended change. Record the covered files and functions, the bounds,
   and the sync commit; move it forward only after you confirm the model matches the code there.
   No placeholders. For a TLA+ check, TLC stops at the first broken rule: tell the agent to remove
   it and rerun until none breaks, and to tell each trace as steps in the code's words.
7. **Prove it.** Break the property in the real code, follow the verify skill as the next agent
   would, and see it catch the break. Drop the break and confirm the check is back to its start.
   If it misses, fix the skill or model, not the break.
8. **Hand off.** What you verified, the tool and why, the bounds, each finding as steps, the run
   command, and what is out of scope. A pass covers the model, not the system.
