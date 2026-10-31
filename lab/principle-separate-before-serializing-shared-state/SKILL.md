---
name: principle-separate-before-serializing-shared-state
description: >
  This skill should be used when the user types /principle-separate-before-serializing-shared-
  state. It holds the Separate Before Serializing Shared State principle, for two or more actors
  that run at the same time may write the same file, branch, key or state object.
disable-model-invocation: true
---

# Separate Before Serializing Shared State

**When:** two or more actors that run at the same time may write the same file, branch, key or
state object.

**Rule:**

1. Find the shared write target.
2. Ask: "Do the actors need one canonical object, or do they publish independent facts?" If
   the facts are independent, give each actor its own file, key, branch or directory. Merge
   only where you read or report. Two workers that each write their own field into one
   `state.json` still share the file.
3. Only when one shared writer is a real invariant, serialize in the structure: a lock,
   sequential phases, a single writer or compare-and-swap.

Instructions and conventions are not concurrency control.

**You skipped it when:** "add a lock" is the first answer, or two hooks write one JSON file.

**Not:** [Make Operations Idempotent](../principle-make-operations-idempotent/SKILL.md) handles one actor across
runs. [Foundational Thinking](../principle-foundational-thinking/SKILL.md) asks the sharing question at design
time.
