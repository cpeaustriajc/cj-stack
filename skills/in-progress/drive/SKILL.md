---
name: drive
description: >
  This skill should be used when the user says "drive this", "loop until it passes", "keep going
  until green", "run it overnight" or "hillclimb", hands over a ticket to finish unattended, or
  before writing a goal or Stop hook. It decides whether the work should loop, writes the exit
  check first, freezes the harness, then makes one change per pass, kept or reverted, with a log
  on disk and a brake on lack of progress. Not for a timer; that is /loop.
---

# Drive

A loop fails in a few predictable ways. It declares victory early because the worker graded its
own work. It stacks changes nobody tested, so the one that broke things is buried. It spins for
hours on the same dead end, or relaxes the target to call it done. It forgets what it tried when
the context fills. This skill is the method that prevents those; the tool that runs the loop is
in an adapter.

| Tool | Adapter |
|---|---|
| Claude Code (`/goal`, Stop hooks, `/loop`) | `references/claude-code.md` |

## 1. Should this loop at all?

Loop only when all three hold. Otherwise do it in one turn, or use a playbook.

- **A check that runs.** A command, test, metric or script answers "done?" without anyone's
  judgement. "Looks good" is not a check.
- **A harness that reproduces the problem.** The failing test fails now, the metric reads its
  baseline now.
- **Every action is reversible.** No deploys, data deletion, payments or messages to people inside
  the loop; those wait for me.

Product, taste and design calls never loop. Neither does work small enough to finish in a turn.

## 2. Write the exit check first

Before the first pass, write the predicate and show it to me:

```markdown
Done when: <the end state, as the check's own output: "pnpm test cart passes, 0 failing">
Check: <the exact command, and where its output goes>
Holds throughout: <what must stay true: files not to touch, the regression suite green>
Floor: <at least N passes, so an early lucky win can't end the run> (metric runs only)
Budget: <passes, hours or spend; whichever comes first ends the run>
```

A ticket from `tickets` already has one: its Done When and You see lines are the end state. Never
relax the predicate during the run to declare victory; a predicate found wrong stops the run and
comes to me.

## 3. Freeze the harness

- Run the check on the untouched code and record the baseline: the failing output, or the metric
  as the median of several runs.
- Prove it can tell: a deliberate break must turn it red. A check that passes too easily is
  suspected before the code is.
- Then freeze it. The loop never edits the check, the tests it relies on, or the data they read.
  A check found broken is fixed in its own change, outside the loop, with my say-so.

## 4. One pass

Each pass starts fresh from disk, not from memory:

1. **Get bearings.** Read the plan, the log's last rows and `git log`. Don't redo what the log
   shows was tried.
2. **One unit.** State the hypothesis in one line, make the smallest change that tests it.
3. **Run the check.** Paste its real output, not a summary of it.
4. **Keep or revert.** Better: commit it with the log row. Not better: revert all of it. Nothing
   is kept because it "might help", and changes are never stacked untested.
5. **Log the pass** (section 5), then the next pass.

A side discovery (an unrelated bug, a refactor that would help) goes in the log as a note for
me, not into this run.

## 5. State on disk

- **Plan**: the units still to try, in a file. A loop may change only an item's status, never
  delete or rewrite items; a plan that has gone stale is regenerated once, as a logged pass.
- **Log**: one row per pass in a gitignored `drive.tsv`: time, hypothesis, change, check before,
  check after, kept or reverted, and a pointer to the evidence (commit, output file), not prose.
- **Resume note**: when the run pauses, the next pass, what is uncommitted, how to restart, and
  the transcript path of every session the run has used. Stop at a clean boundary: commit or
  revert first.

## 6. Brake on progress, not on turns

- **Stuck**: several reverted passes in a row, or several passes with no change in the check.
  Change approach once: a different category of hypothesis, or combine near misses. If it is
  still stuck, stop and say so.
- **Out of budget**: stop, even mid-plan.
- **Dead end**: the predicate can't be met without breaking a Holds throughout line. Stop and
  bring me the conflict; don't trade one for the other.
- **Not a stop**: a slow but real improvement while untried cheap hypotheses remain.

A stop is a report, not a failure.

## 7. Someone else checks

The worker never grades itself. The exit is the check's output, and for a run that matters a
second reviewer, a fresh agent or a different model given the predicate, the diff and the log,
confirms done before I'm told it is. Inconclusive is not a pass.

## 8. Audit the trail

Before the report, one fresh agent that did none of the work, on the model the adapter names,
audits the log against the transcript of every session the run used. It gets the log, the plan
and the transcript paths, edits nothing, and flags:

- **Unsupported**: a log row the transcript does not show happening (the change, the check run,
  the keep or revert), or an evidence pointer that doesn't resolve (no such commit or file).
- **Unlogged**: an action in the transcript the log leaves out: a kept or reverted change, a
  change of approach, an edit to the check or its tests, a skipped step.
- **No artifact**: a "done", "passes" or "fixed" claim, in the log or the transcript, with no
  check output, commit or file behind it.

Each flag is one Attention line: the item, the evidence (log or transcript line, quoted), and what
I must check. The list goes at the top of the report as the auditor wrote it. No flags means
"Attention: nothing to check", with no padding and no cap on the count. An audit that could not
read a transcript is an Attention line, not a clean list.

Section 7's reviewer still confirms done: it judges the diff against the predicate, and this audit
judges whether the log tells what happened.

## 9. Report

When the run ends, in this order:

- The Attention list from section 8.
- The predicate's state, with the check's last output.
- Passes kept and reverted, and the budget used.
- Why it stopped: met, stuck, budget or dead end.
- What needs me: side discoveries, a predicate that looked wrong, anything skipped.
- The path to the log.
