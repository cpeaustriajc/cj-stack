# Design

Use this before code that crosses a module boundary or is costly to undo: a new public API, a
data shape that gets stored, a split of a module. Skip it for mechanical work (a rename, a
move, a change that follows an existing pattern) and say so in one line.

1. Write 3-6 criteria that a sketch can pass or fail, such as "a new provider touches one
   file". Take them from the spec and the callers, not from a sketch.
2. Read the caller's usage first: the README and 2-3 real call sites. Write the calls as the
   callers want to make them, then derive the types from those calls.
3. Get two whole-shape sketches, not two point fixes. Each sketch is written blind to the
   other, from the same criteria and call sites. Each gives the public API, the data shape,
   who owns each piece of state, and the files it touches. `references/claude-code.md` says
   how to run the two sketches in parallel.
4. Read both sketches end to end. Score each one per criterion, then pick a base and graft at
   most 1-2 ideas from the other by hand. If the sketches differ widely, the criteria were
   vague: restate them and run step 3 again.
5. Screen the pick for these red flags, and change the shape if one is present:
   - Two writers own one piece of state.
   - Two ways do one task.
   - Callers can import internals.
   - Two or more lists must be kept the same by hand.
   - A layer only passes calls through.
   - Wire, transport or storage types appear in the public API.
6. Record the shape, the tradeoffs accepted ("we accept X for Y") and the alternatives you
   did not pick, with the reason. Put the record in the PR body or the decision log
   (`project-knowledge`).
7. Build against the sketch. If the build needs a change to an agreed signature, stop and
   tell the user; do not absorb the change. Scrap the sketch and go back to step 2 when you
   see the same workaround twice, a cast only to compile, special-case branches, or callers
   that must know internal rules.
