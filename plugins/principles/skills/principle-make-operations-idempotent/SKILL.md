---
name: principle-make-operations-idempotent
description: >
  This skill should be used when the user types /principle-make-operations-idempotent. It holds
  the Make Operations Idempotent principle, for you design a command, a lifecycle step, a hook, a
  script or a loop that runs amid crashes, restarts and retries.
disable-model-invocation: true
---

# Make Operations Idempotent

**When:** you design a command, a lifecycle step, a hook, a script or a loop that runs amid
crashes, restarts and retries.

**Rule:** Derive each step from the state that exists, not from what the last run meant to do.
Read the current state, compare it with the goal, and apply only the difference.

Anything a run leaves behind must look stale to the next run, at whatever point the last run
stopped: a lock, a temporary file, a half-written record, a claimed job. For example, write to
a temporary path and rename it into place, or compare files by content, not by creation order.

**The test:**

1. What happens if this runs twice in a row?
2. What happens if the last run crashed at each possible point?
3. Does each case end in the same state?

If an answer is "it depends on what the last run left", add a step that reconciles the state.

**You skipped it when:** a crash halfway needs cleanup by hand, or the second run fails with
"already exists".

**Not:** [Separate Before Serializing Shared State](../principle-separate-before-serializing-shared-state/SKILL.md)
handles actors that run at the same time. This principle handles one actor across runs.
