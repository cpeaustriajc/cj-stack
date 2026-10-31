---
name: principle-test-behavior-not-implementation
description: >
  This skill should be used when the user types /principle-test-behavior-not-implementation. It
  holds the Test Behavior, Not Implementation principle, for you write, change or keep a test.
disable-model-invocation: true
---

# Test Behavior, Not Implementation

**When:** you write, change or keep a test.

**Rule:** Assert what the users of the code can observe: return values, errors, state they
read back, and effects on outside systems. Judge each test by two edits:

1. **Break the behavior.** The test must fail.
2. **Change only the internals.** The test must pass.

- The payload that a mocked external service gets is behavior. A call to an internal helper
  is not.
- The error type that callers branch on is the contract. The message text is not.

**You skipped it when:** a test passes while the code returns a wrong value, or a test breaks
on each refactor.

**Not:** [Prove It Works](../principle-prove-it-works/SKILL.md) checks the real output once. This principle
decides if a test can fail.
