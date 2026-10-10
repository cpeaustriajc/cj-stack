---
name: playbooks
description: Route a bug fix, refactor, performance fix or feature to its playbook and copy the steps into the task list, so each kind of work carries its own proof - a reproduced bug, pinned behaviour, a measured baseline, a verified slice. Use at the start of any bug, refactor, "make it faster" or feature task bigger than a one-line change.
---

# Playbooks

Each kind of work fails in its own way, so each has a fixed order that carries its own proof.

1. Pick the playbook: `references/bug.md`, `refactor.md`, `perf.md` or `feature.md`. Say which
   one in one line. If the task is two kinds, such as a bug fix that needs a refactor, run the
   bug playbook first and treat the refactor as its own task.
2. Copy the playbook's steps **verbatim** into the task list as the first items. A step you
   skip stays in the list, marked `skip: <reason>`. Never drop a step silently.
3. Work the steps in order. A step that ends with a check isn't done until the check has run
   and its evidence is saved.
4. End every check as VERIFIED, NOT VERIFIED or INCONCLUSIVE. INCONCLUSIVE never counts as a
   pass, and missing evidence is reported as a gap.
5. Report the proof the playbook asks for, then commit per slice as usual.

The steps fit into Scout → Spec → Build → Commit. They decide *what* each phase must prove,
not who does it.

Evidence follows the end-to-end rule: drive the real app and leave a re-runnable command plus
its trace, screenshots or video. Read the project's feature file for the area first, if it has
one (`feature-files`).
