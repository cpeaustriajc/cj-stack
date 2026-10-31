---
name: principle-prove-it-works
description: >
  This skill should be used when the user types /principle-prove-it-works. It holds the Prove It
  Works principle, for before you say that a task is done, and each time a check fails.
disable-model-invocation: true
---

# Prove It Works

**When:** before you say that a task is done, and each time a check fails.

**Rule:** Check the real thing, not a proxy. Read the actual value, the live process and the
real output, not a cache, a timestamp, a self-report or "it compiles". The project's test
policy and the playbooks say how.

If a check fails, suspect the observation method first: a stale cache, the wrong process, an
old build, the wrong environment or the wrong file. Show that the observation sees your change
before you revert or change the fix.

**You skipped it when:** a correct fix is reverted because the check read an old build, or
"done" rests on a subagent's word.

**Not:** [Explain the Number](../principle-explain-the-number/SKILL.md) asks what a measured value means. [Test
Behavior, Not Implementation](../principle-test-behavior-not-implementation/SKILL.md) asks whether a test can
fail.
