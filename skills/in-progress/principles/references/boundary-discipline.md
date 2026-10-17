# Boundary Discipline

**When:** you decide where validation, error handling or a framework adapter goes.

**Rule:** Validate and handle errors at system boundaries: CLI arguments, config, files,
network and external APIs. Inside the system, trust the types and do not check again. Keep
business logic in pure functions; the framework shell only calls them.

- Parse raw input into domain types at the boundary.
- Do not expose transport, storage or framework types through the public surface.

**The tests:**

- "Does this data cross a system boundary here?" If not, the check is redundant.
- "Can this logic be a pure function that the shell calls?" If yes, extract it.

**You skipped it when:** null checks sit deep in call chains, or you cannot test the logic
without the framework.

**Not:** [Type System Discipline](type-system-discipline.md) shapes the types. The project's
error handling rules say how to handle an error. This principle says where.
