---
name: principle-attack-the-premise
description: >
  This skill should be used when the user types /principle-attack-the-premise. It holds the Attack
  the Premise principle, for two or more fixes failed the same check, and all of them assumed the
  same fact.
disable-model-invocation: true
---

# Attack the Premise

**When:** two or more fixes failed the same check, and all of them assumed the same fact.

**Rule:** Write the premise down in one sentence and test it before you write the next fix.
Look at how the failures are distributed, not only at their size: failures that all stop at
one limit point to a wait, not to slow work.

**Stop:** no next fix before the premise is written down and tested. This also applies to your
own fixes in this session, not only to fixes that the user reports.

**You skipped it when:** fix 3 assumes the same fact as fixes 1 and 2.

**Not:** [Fix Root Causes](../principle-fix-root-causes/SKILL.md) traces one symptom to its first wrong step.
This principle questions a belief after fixes failed.
