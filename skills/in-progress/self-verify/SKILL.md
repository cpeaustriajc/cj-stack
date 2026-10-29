---
name: self-verify
description: >
  This skill should be used when the user says "set up verification", "make agents verify their
  work", "verify skill", "agents keep claiming done without proof", "we can't review every PR",
  "set up PR verification" or "audit the verify skill". It sets up and maintains the project's own
  verify skill and the per-PR verdict. One bug fix goes to playbooks; one feature file goes to
  feature-files; a periodic sweep goes to bug-hunt.
---

# Self-verify

## Why

People read only PRs whose `Merge danger` line says one-way door. Most PRs get no human read of
the diff. So the agent proves its own change, and a fresh agent checks that proof before merge.

A proof is a command that a person can re-run. The proof leaves evidence that a person can check.

## Setup

1. Read the project's feature files. They are the map. Each feature file has a **Code** line
   (paths) and **Tests** and **Check** lines (proof). With none yet, write them in the verify
   skill's `references/features/`, one for each feature the next change touches.
2. Use the project's run skill for launch. Do not copy a launch command into the verify skill.
3. Ask the user once where the full E2E suite runs, and when. Example: acme's full run took
   23-53 minutes locally. Write the answer into the project's verify skill. Never decide it for
   all projects.
4. Write `.claude/skills/verify/SKILL.md` in the target project, from `references/verify-template.md`.
   Do not write it into the plugin. Plugin skills do not run before commit.
5. Prove the skill once: run it on one feature and keep the evidence. A verify skill that was
   never run is a draft.
6. Commit the skill with the project. Update it when a feature file changes.

## Evidence rules

- Read the runner's own exit code. Use `set -o pipefail` and read `${PIPESTATUS[0]}`, or a report
  file. Never trust `tail`.
- Count the tests. Zero tests run is NOT VERIFIED.
- A timeout, a missing prerequisite or a skipped check is BLOCKED. Name the missing item.
- Each step pairs an action with a user-visible end state. A toast alone is not proof. An
  attribute a person cannot see, such as an `aria-label` or a `data-*` value, is not a
  user-visible end state.
- An exact check (text, value or state) decides the result. An agent's opinion of a screen,
  the capture reviewer's included, can only add a gate on top of it.
- Use the real environment the feature file names. A mock counts only at a boundary the project
  already isolates.
- Write one result line per feature: `VERIFIED`, `NOT VERIFIED` or `BLOCKED`, plus the command.
- Save the report, screenshots or trace in a path the reviewer can open. Print the path.
- Each capture gets a reviewer before you write its result line. A capture is a screenshot, a
  video end frame or saved output. The reviewer is a new read-only agent on the smallest model
  tier. An agent that has read the log or the steps is not fresh, and that includes a PR
  verifier. Read `references/claude-code.md` first. Give the reviewer only the capture and the
  end state that the claim names. It answers one question: does the capture show that state? For
  a repro, that is the broken state; for a fix, the fixed state. VERIFIED needs its "yes"; "no"
  or "cannot tell" makes the line NOT VERIFIED. A new capture gets a new reviewer; never ask
  again about the same capture.

## No fake tests

Reject a test that passes without proving the feature. Reject these patterns:

- `toBeTruthy`, `toBeDefined` or `not.toThrow` as the only assertion.
- Mocks of internal modules of the code under test.
- Snapshot tests that accept any output.
- A test that asserts on its own fixture.
- Expected values computed by the code under test.
- A claim about what the screen shows, asserted only on an attribute a person cannot see.

Delete or rewrite a test that would still pass if the code under test returned `undefined`.
Never edit a test to match wrong code.

Add a lint rule only after it fails on the real existing test that it targets. The rule's message
names the fix.

## Repair on failure

When a verify run fails:

- If a feature file or the verify skill is wrong (a renamed route, a moved button), fix that one
  file in the same change. Say so in the PR.
- If the app is wrong, it is a bug. Report it, or fix it in the playbooks bug order. Never edit
  the map to hide it.

## Weekly audit

Run the verify skill on the default branch once a week, by a scheduled routine or a desktop
scheduled task. Mechanics: `references/claude-code.md`. Do these steps in this order:

1. **Source wave.** Read `references/claude-code.md` first. Start one read-only reader on the
   smallest model tier for each feature file, all at the same time. Each reader compares its
   feature file with the code on the **Code** line. It returns each drift
   as the code's `file:line` and the feature-file line that the code contradicts, or "no drift".
   A reader never drives the app and never edits.
2. **Churn sweep.** List the paths that the commits since the last audit changed. One more
   reader of the same kind finds the user-facing surfaces in them (routes, commands, screens) that no feature
   file lists. Drop each finding that has no source path.
3. **Live pass.** Drive every feature once in the live app, also when the source wave found no
   drift. A reader's drift is a lead: fix a feature file only after the live pass confirms it.

The audit:

- Ends in exactly one result:
  - **clean**: no PR.
  - **changed**: one PR that fixes only feature files and the verify skill.
  - **blocked**: names the blocker.
- Never edits product code.
- Sorts each mismatch into doc drift, harness gap or product regression. Doc drift and harness
  gaps go into the PR. A product regression goes to the tracker, not into the map.
- Treats an unlisted surface as doc drift: the PR adds its feature file, proved in the live pass.

## PR verdict

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

## Never twice

Each FAIL, and each bug that a verdict or an audit finds, ends with one prevention proposal. Pick
the strongest layer that can hold it: code structure, lint rule, hook, test, skill, then instruction
file. Route it as in the `hone` skill. The user accepts it. Nothing is applied silently.

## What this skill does not do

- No 21-step ship pipeline.
- No always-on browser daemon.
- No coverage scoring.
- No hourly audit loops.
- Cheap checks first. Run the fast checks before the slow ones.
