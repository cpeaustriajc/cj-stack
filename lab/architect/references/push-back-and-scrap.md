# Push back and scrap

Read this when the owner pushes back on a candidate, or when implementation keeps producing friction the sketch cannot absorb. The phases are in `SKILL.md`.

### Push back

The owner replies `Push back on A: <reason>` or `Push back on B: <reason>`.

If the human pushes back on the shape (at the pick or after the fact), treat that as Phase A evidence. Re-ground and re-run Phase B before writing more code. The reason becomes a constraint in both runners' prompts, with the candidate it rejects named as the shape not to repeat. A push back after the pick first removes what the rejected sketch wrote (revert its commits), so a rejected shape leaves no code behind. Write no file in between. Show two new candidates in Phase C and stop again.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, throw the sketch out once the owner agrees. Don't bolt fixes onto a wrong design, per the **redesign-from-first-principles** and **fix-root-causes** principles.

The signal is a *pattern*, not single instances. Tells:

- The same shape of workaround appearing repeatedly across unrelated code.
- Multiple unrelated edge cases that all need special-case branches.
- Types that need escape hatches (`any`, casts, optional fields always set in practice) to compile.
- The "we need a lock" reflex when the sketch said the state wasn't shared.
- Callers having to know the abstraction's internal rules to use it.
- Two or more independent Phase D deviations of the same shape across the implementation.

Use judgment. A few edge cases don't condemn an architecture. Some problems are legitimately complex. Complexity in the data is not complexity in the design.

Watch for the pattern from the first stub file of the pick on, not only in Phase D: a caller the sketch does not cover is a deviation too. When the pattern shows, stop building and tell the owner: the tell, each instance with file and line, and an offer of a smaller re-sketch. End with "Reply Re-sketch, or Keep going with a reason." and wait. Scrap only on Re-sketch.

When you scrap:

1. Re-run the **how** method over what's been built.
2. Redesign as if the new constraints had been day-one assumptions, per redesign-from-first-principles.
3. Subtract before adding, per the **subtract-before-you-add** principle. The new sketch should be smaller than the old one before it grows.
4. Return to Phase B and re-run both runners.
