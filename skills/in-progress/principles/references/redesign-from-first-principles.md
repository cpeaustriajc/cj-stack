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

**Not:** [Attack the Premise](attack-the-premise.md) questions a fact that the current design
assumes. This principle rebuilds the design around a new requirement. [Outcome-Oriented
Execution](outcome-oriented-execution.md) says how to move to the new design.
