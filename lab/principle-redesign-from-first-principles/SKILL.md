---
name: principle-redesign-from-first-principles
description: >
  This skill should be used when the user types /principle-redesign-from-first-principles. It
  holds the Redesign From First Principles principle, for a new requirement must go into a design
  that exists.
disable-model-invocation: true
---

# Redesign From First Principles

**When:** a new requirement must go into a design that exists.

**Rule:**

1. Read all the files that the requirement touches.
2. Ask: "If we wrote this from zero, with this requirement from day one, what would we build?"
3. Plan that whole design. Then deliver it in steps.
4. Update each reference to the old shape: types, docs, examples, tests, evals and the
   rationale text.

Do not attach the requirement to the side of the current design.

**You skipped it when:** a new flag or branch sits next to the old path, or the docs and
examples still show the old shape.

**Not:** [Attack the Premise](../principle-attack-the-premise/SKILL.md) questions a fact that the current design
assumes. This principle rebuilds the design around a new requirement. [Outcome-Oriented
Execution](../principle-outcome-oriented-execution/SKILL.md) says how to move to the new design.
