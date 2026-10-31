---
name: principle-minimize-reader-load
description: >
  This skill should be used when the user types /principle-minimize-reader-load. It holds the
  Minimize Reader Load principle, for you shape or review code that is hard to trace, or you want
  to add a layer or a piece of state.
disable-model-invocation: true
---

# Minimize Reader Load

**When:** you shape or review code that is hard to trace, or you want to add a layer or a
piece of state.

**Rule:** Measure the work a reader must do, on two separate axes. Layers to trace: the hops
from a question to its answer. State to hold: hidden or mutable context. Lines of code and
"clean architecture" are only proxies.

- Inline a wrapper with one caller, an adapter with one implementation, and a layer that
  passes the same arguments through.
- Make the state scope small: a return value over a mutation, a local over a field, a field
  over module state, module state over a global. Derive a value; do not sync two copies.
- State an invariant once, at the boundary, not in each consumer.
- Add a layer or a piece of state only if it removes at least as much load elsewhere.

**The test:** can a new reader answer "Where does X come from?" and "What can change X?" in
30 seconds?

**You skipped it when:** a refactor adds a file or a layer and calls the result cleaner.

**Not:** [Subtract Before You Add](../principle-subtract-before-you-add/SKILL.md) sets the order of removal.
[Model the Domain](../principle-model-the-domain/SKILL.md) picks the structure that removes branches.
