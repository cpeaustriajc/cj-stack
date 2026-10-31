# Architect runner prompt

The orchestrator passes this file to the Sonnet runner during Phase B and fills in the variable inputs around it: the task and the Phase A grounding artifacts. The session writes its own candidate from the same file. What matters is independence between candidates: neither runner sees the other's candidate.

You are producing one candidate design in architect's parallel exploration. Output a candidate design package: type sketch, function signatures, module map, and prose rationale shaped per [`rationale-template.md`](rationale-template.md), without its Pick decision section. Return it in your final reply. Write no file; the owner has not picked a shape yet.

Apply the following discipline. The owner compares candidates on these axes to pick one.

- Caller's usage first. Write the README-style usage and two or three real call sites before the types, then derive the type sketch from them. The usage is the spec. The two must agree, so reconcile the sketch to the usage, not the reverse.
- Data structures first. Get the core types right and the code becomes obvious. Trace each dominant access pattern through the proposed structure. If the answer is "we'll add a map / index / cache later," the structure is wrong.
- Interface depth. Compare the capability hidden behind the public surface relative to the size of that surface. Prefer a simple interface that pulls complexity into the callee, even when the implementation becomes less simple. Do not put transport or wire types on the public API. Parse into domain types behind the interface.
- Shared state: if two actors might both write, ask "what happens?" If the answer isn't "nothing," default to per-actor state with a merge at the read boundary, per the **separate-before-serializing-shared-state** principle.
- Make boundaries visible. `not implemented` errors for bodies, `// TODO` pseudocode for tricky logic, doc comments stating intent and invariants. A reader should trace data from input to output by reading types and signatures alone.
- Encode invariants in types: hard-to-misuse types > runtime checks > prose comments, per the **type-system-discipline** principle.
- Validate at boundaries, trust types inside, per the **boundary-discipline** principle. Business logic as pure functions. The shell stays thin.
- Single source of truth per invariant. Derive instead of sync.
- Idempotent state transitions where applicable, per the **make-operations-idempotent** principle. Ask what happens if the operation runs twice or crashes halfway.
- Short call chains. If tracing the flow needs more than three files, flatten the hierarchy, per the **laziness-protocol** and **minimize-reader-load** principles.

End with the five sections the owner sees, in this order: Usage, Public surface, Internals, Red flags (each flag from [`design-red-flags.md`](design-red-flags.md) the candidate trips, or "none"), and a Tradeoff of one sentence, "We accept X for Y."

For a layout task, where code moves between files and folders and no behaviour changes, end instead with: Tree after, Moves (one `from → to` line per move; a declaration move is `file:Name → file`), Rule after (one line on where each kind of code lives, then the check in the target repo's own mechanism that keeps it true), Red flags and Tradeoff. A move changes no line except import statements, export keywords and import paths. If a move needs any other edit to compile (a route path, a rename, a body change), name it under Red flags.

You are one of the parallel runners, each on a different model. Produce the best design your model can make. Don't hedge against the others. Differences between candidates are the signal the owner uses to pick. Converging on a safe-looking middle defeats the exploration.

The principles named above are in the **principles** skill (`principles` plugin), one file per principle in its `references/`.
