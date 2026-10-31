---
name: principle-exhaust-the-design-space
description: >
  This skill should be used when the user types /principle-exhaust-the-design-space. It holds the
  Exhaust the Design Space principle, for a new interaction, API shape or architecture decision
  with no precedent in the codebase, or a product decision that depends on feel, not on logic. If
  a precedent exists, follow it.
disable-model-invocation: true
---

# Exhaust the Design Space

**When:** a new interaction, API shape or architecture decision with no precedent in the
codebase, or a product decision that depends on feel, not on logic. If a precedent exists,
follow it.

**Rule:** Build 2 or 3 competing options as small prototypes. Compare them side by side on the
same task. Then choose one, and say why each other option lost.

**You skipped it when:** the first shape you thought of ships, and the PR names no option that
you compared.

**Not:** [Redesign From First Principles](../principle-redesign-from-first-principles/SKILL.md) rebuilds a design
for one new requirement. [Model the Domain](../principle-model-the-domain/SKILL.md) picks a data structure. This
principle compares whole options before you commit to one.
