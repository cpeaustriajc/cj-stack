# Model the Domain

**When:** you write stateful logic, the code branches a lot, or files repeat the same
assumption about a shape.

**Rule:** Put the domain into one data structure, not into conditionals across the code. Pick
the structure that makes invalid states impossible and deletes branches:

- a state machine instead of booleans, phases or lifecycle checks
- a typed model instead of loose parameters
- a lookup table, a registry or a discriminated union instead of branches across files
- a reducer or a command and event model instead of ad hoc state changes
- one module per body of domain knowledge, not one per phase (load, validate, save)

If no structure fits, write down what the code must never allow and how it reads the data.
Then pick the structure that encodes exactly that.

Keep plain code when it is clear, local and unlikely to grow. Reject an abstraction that adds
a hop and removes no branch, rule or invalid state.

**You skipped it when:** a feature adds one more branch to an if/else chain, a second boolean
must stay in sync with the first, or modules named after phases repeat one rule.

**Not:** [Type System Discipline](type-system-discipline.md) makes the compiler enforce the
structure. [Foundational Thinking](foundational-thinking.md) puts the structure first.
