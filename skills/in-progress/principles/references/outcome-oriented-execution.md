# Outcome-Oriented Execution

**When:** a planned rewrite or migration with phase boundaries that you declare before you
start. Only then.

**Rule:** Move straight to the target design. Do not write compatibility code only to keep
each middle step green.

- Before you start, declare where breakage is allowed and which checks must stay green on the
  areas that you touch.
- Breakage at a declared phase is allowed when it is planned, limited and reversible.
- At the end, run the full static and runtime checks.

Outside a declared migration, the project's "never commit red" rule wins.

**You skipped it when:** a shim or an adapter exists only so that a middle step passes, and it
stays after the migration.

**Not:** [Sequence Verifiable Units](sequence-verifiable-units.md) ends each unit green. This
principle allows declared red at a phase step. [Redesign From First
Principles](redesign-from-first-principles.md) picks the target.
