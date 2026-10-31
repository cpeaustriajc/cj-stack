---
name: principle-foundational-thinking
description: >
  This skill should be used when the user types /principle-foundational-thinking. It holds the
  Foundational Thinking principle, for before you write the logic of a new feature or module, and
  when you set the order of the work.
disable-model-invocation: true
---

# Foundational Thinking

**When:** before you write the logic of a new feature or module, and when you set the order of
the work.

**Rule:**

- Define the data shapes before the logic. Trace each access pattern, and pick the structures
  that fit the most frequent paths.
- Do the scaffold first: work that each later step uses, such as CI, lint, test setup and
  shared types.
- Before two actors share state, ask: "What happens if the other actor changes this at the
  same time?" If the answer is not "nothing", isolate the state.
- Each step lands one complete abstraction or makes one deeper. Do not spread a new capability
  across the callers as special cases.

**You skipped it when:** the logic came first and the types came after it, or one capability
shows up as a special case in many callers.

**Not:** [Model the Domain](../principle-model-the-domain/SKILL.md) picks the structure. This principle puts the
shapes and the scaffold before the logic. [Separate Before Serializing Shared
State](../principle-separate-before-serializing-shared-state/SKILL.md) handles the shared state that you find.
