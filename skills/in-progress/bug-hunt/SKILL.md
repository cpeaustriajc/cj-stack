---
name: bug-hunt
description: >
  This skill should be used when the user says "bug hunt", "deep code review", "audit the
  codebase", "hunt for bugs until clean", "run N rounds of review" or "find and fix every bug".
  Three parallel hunters search the whole scope for real bugs, fix each one test-first in files
  they own, and search again, round after round, until a round where all three find zero. For a
  report-only review of one diff, use interrogate instead.
---

# Bug hunt

One review pass finds some bugs and hides the rest behind them. A fix also changes the code that
the next pass reads. So the hunt repeats until a full round finds nothing.

## 1. Scope and shards

- The scope is what I named (paths, a PR, an issue such as an audit ticket), else the whole repo
  minus generated, vendored and lock files.
- Write the file list to the scratchpad. Split it into three shards of about equal lines, by
  area (one feature or package stays in one shard).
- Read the project's test command, E2E command and its rules on test ids and visible copy first.
  Every hunter gets them.

## 2. Each round

Spawn the three hunters **in one message**, so they run in parallel. Never one after another.
Tool mechanics: `references/claude-code.md`.

Each hunter reads the full scope but **edits only its own shard**. This stops two agents editing
one file. Rotate the shards each round, so every file gets fresh eyes.

Hunter brief (fill in the brackets):

> Goal: find real bugs in [scope] and fix the ones in your shard [file list].
> A bug is wrong behaviour, a regression, a broken edge case, a security hole, data loss or a
> divergence from [spec/issue]. Not style, naming, "consider adding" or a refactor.
> Known bugs already fixed or rejected: [ledger]. Do not report them again.
> For each bug in your shard: write a test that fails, show it fail, fix the code, show it pass.
> Do not change test ids or visible copy unless the fix needs it. If you cannot write a failing
> test, do not fix it: report it as unproven.
> For a bug outside your shard: report it, do not edit.
> Read every file in your shard in full. Return: one line per shard file (`path: clean` or
> `path: N bugs`), then per bug: file:line, the defect, the failure scenario (input or state →
> wrong result), the test name, fixed or not and why. End with `BUGS FOUND: <n>`.

## 3. Between rounds (main session)

- Check coverage: every shard file has a line in the reply. A missing file goes into the next
  round. Keep a count: files read / files in scope, as a percent.
- Verify each fix yourself: read the diff, run the new test. A diff that fails your review twice
  goes back with a hunter one model tier up.
- Hand each out-of-shard bug to the hunter that owns that file next round.
- Add each bug to the ledger in the scratchpad: verified-fixed, unproven, or rejected with one
  line why.
- Run the full test suite. A red suite is the next round's first bug.
- Commit each verified fix as its own atomic commit, if the project lets you commit.

## 4. Stop

Stop when one round has all three hunters at `BUGS FOUND: 0` and coverage is 100%. Also stop and
ask me after 5 rounds, or when a round finds only bugs a hunter rejects as not real.

Run the E2E suite once at the end. Report:
- coverage percent and rounds run
- **verified bugs**, fixed, each with its commit and test
- **unproven bugs**, kept apart from the verified ones, with why no failing test exists
- **rejected findings**, one line each, so I can override
- the exact E2E command and where its trace or report is

The ledger and every hunter reply stay in the scratchpad. Say where.
