---
name: principle-sequence-verifiable-units
description: >
  This skill should be used when the user types /principle-sequence-verifiable-units. It holds the
  Sequence Verifiable Units principle, for multi-step work, such as a sweep, a migration or a run
  of similar edits, and when you order commits and PRs.
disable-model-invocation: true
---

# Sequence Verifiable Units

**When:** multi-step work, such as a sweep, a migration or a run of similar edits, and when you
order commits and PRs.

**Rule:** Each unit starts from a known-good state, makes one change, runs its check, and only
then goes on. The playbooks hold the steps for each slice. This principle adds:

- Rebase onto a clean trunk before the first unit, so each check measures against the real
  baseline.
- Run the check for each unit, also when a script did the edits.
- Order the commits so a reviewer can replay them as an argument: the failing test, then the
  fix; the removal, then the reshape; the baseline, then the treatment; the scaffold, then the
  feature.

**You skipped it when:** a check compares against a stale base, or the commit order proves
nothing, such as a test that lands after its fix.

**Not:** [Outcome-Oriented Execution](../principle-outcome-oriented-execution/SKILL.md) allows declared red at a
phase step. [Prove It Works](../principle-prove-it-works/SKILL.md) keeps each check real.
