---
name: architect
description: "This skill should be used when the user types /architect with a task: sketch types, signatures, and module structure before code, then stay in the loop while implementation fills in. Use for 'architect this', 'design this', or non-trivial work where jumping to code would lock in the wrong shape."
disable-model-invocation: true
argument-hint: "<task>"
---

# Architect

Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies and pseudocode. Show two candidates from two models side by side, wait for the owner's pick, then fill in code against the picked sketch.

The task is `$ARGUMENTS`. Tool mechanics (spawn calls, models, the inline view) are in `references/claude-code.md`.

## Start

Open a todolist with one entry per phase before starting.

1. Ground
2. Sketch
3. Agree
4. Implement
5. Scrap

## Phase A: Ground the problem

First name the task's kind in one line: new design, logic re-architecture, or layout. A task that asks to make files thin, split, move or regroup them, and names no change in behaviour, is a layout task, even when the repo has open issues that would redesign the same code. A layout task makes no behaviour change, so ground it on the files its words name and their line counts.

Build a real mental model of every system the new code touches. Run cj-lab's **how** method over the relevant subsystems: read `../how/SKILL.md` and follow it, because `/how` is slash-only and the Skill tool cannot start it. Naming a file isn't grounding. Produce the architectural explanation `how` prescribes. If the design redefines ownership or layering, also run the **why** skill on the existing shape so the rationale becomes a constraint, not a guess.

Skip Phase A only when the work is genuinely greenfield with no surrounding system to integrate.

## Phase B: Sketch

Two runners on two different models each write one candidate from `references/runner-prompt.md`, the task and the Phase A grounding. Neither sees the other.

1. Start the Sonnet runner as a background subagent first.
2. Write your own candidate in this session. Do not read the Sonnet runner's result until your candidate is complete.
3. Then read the Sonnet candidate.

Models follow cj-stack's `models/README.md`.

Design it twice. Require at least two structurally distinct candidates, even when the first looks sufficient. This is the **exhaust-the-design-space** principle (cj-lab's **principles** skill) made concrete. Whole-shape alternatives, not point fixes inside one shape. If both runners return the same shape, show both anyway and say they converged; never rewrite your candidate after reading the other.

Screen every candidate against [`references/design-red-flags.md`](references/design-red-flags.md). Assume the next contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Prefer the design where a change that looks right from one file is right for the whole repo.

Compare viable candidates on interface depth. Prefer the design that hides more complexity behind a smaller, simpler public surface. A rich interface can keep call chains short by concentrating capability instead of scattering it across layers.

Write no file in this phase. The candidates live in the conversation until the owner picks.

## Phase C: Agree

Always stop here, before any code is written. Show the two candidates side by side, each in these sections, in this order:

1. **Usage**: the caller's usage first, as in the rationale's "Usage (caller's view)".
2. **Public surface**: the types and signatures a caller sees.
3. **Internals**: what the surface hides, with `not implemented` bodies and pseudocode.
4. **Red flags**: each flag from `references/design-red-flags.md` the candidate trips, or "none", with one line each.
5. **Tradeoff**: one sentence, "We accept X for Y.", with no second sentence.

Add one line under each that names the model that wrote it. Recommend one, with one line why. Then end the turn and wait for the owner: Pick, or Push back with a reason. Where no inline view is available, print the same sections as text blocks, candidate A then candidate B, and still wait.

For a logic re-architecture, where the task reshapes code that exists today, show **Today** above the two candidates: today's public surface as excerpts with file and line, and each flag from `references/design-red-flags.md` it trips, marked at the line that trips it, or "none". A new design with no code to replace skips Today.

For a layout re-architecture, where the task moves code between files and folders and changes no behaviour, show **Today** as today's file tree for the folders the task names, with the line count of each file, and mark each file the candidates move. Each candidate then has these sections instead of Usage, Public surface and Internals:

1. **Tree after**: the file tree after the moves, for the folders that change.
2. **Moves**: one line per move, `from → to`. A file move names two paths. A declaration move names `file:Name → file`.
3. **Rule after**: one line that says where each kind of code lives, then the check that keeps it true, in the target repo's own mechanism (its lint rules, guards or tests).
4. **Red flags** and 5. **Tradeoff**, as above.

A move changes no line except import statements, export keywords and import paths. A candidate that needs any other edit to compile is not a layout candidate: name that edit under its Red flags.

### Pick

The owner replies `Pick A` or `Pick B`.

1. Write the picked sketch as real stub files: its types, signatures and module map, with `not implemented` bodies and `// TODO` pseudocode as shown. Change only what the sketch names.
2. Fill the rationale's "Pick decision" section: the picked candidate and its model, why it was picked (the owner's words if they gave a reason, else your recommendation line, marked as yours), the candidate not picked with its tradeoff line, and what was taken from it.
3. The rationale, with the picked shape, its tradeoffs accepted and the alternatives not picked, is the body of the pull request for this work. Open the pull request with it as the body, or put it in the body of the one already open.

A layout pick runs **Pick a layout** below instead of these steps.

The picked sketch can ship as its own commit, as the "scaffold first" mode of the **foundational-thinking** principle. Planned and scoped breakage during fill-in is fine, per the **outcome-oriented-execution** principle. For adversarial pressure on the design before implementing, run the **interrogate** skill on the picked sketch.

### Pick a layout

The owner replies `Pick A` or `Pick B` on layout candidates. Work on a branch, never the trunk. Save every output below to the project's work folder.

Before step 1, run `git status --porcelain`. If it prints anything, stop and tell the owner to commit their own work first: step 3 stages everything and the undo restores tracked files to `HEAD`, so uncommitted edits would be lost.

1. Before any move, run the repo's typecheck and tests. Save each exit code and the names of the failing checks.
2. Do every move in the picked sketch: `git mv` for a file, a verbatim cut and paste for a declaration. Add only the import and export lines the moves force. Change no other line.
3. Stage everything and run `python3 -I <base directory of this skill>/scripts/moves_only.py HEAD` from the repo root. It must print `moves only`.
4. Run typecheck and tests again. They must give the same result as before: the same exit codes and the same failing checks.
5. Commit the moves as one commit that holds moves only.
6. Add the rule's check in a second commit, in the target repo's own mechanism. Read the repo's instructions first: its guards can be owner-protected. If the repo forbids a new guard, use the closest allowed check (a lint rule or a test) and say so. Show that the check passes on the moved tree and fails on a change that breaks the rule, then drop that change.
7. Fill the rationale's "Pick decision" section and save the rationale as the pull request body to come.
8. Stop. Report the two commits, the before and after results, the check's failing proof and the rationale path. Do not build other code and do not push: the owner reviews the moves first.

If step 3 or step 4 fails, or typecheck passes only after an edit that step 2 does not allow (a changed route path, a renamed symbol, a body change, a broken import cycle), a move needs a logic edit. Undo every move: restore the tracked files to `HEAD` and delete the files the moves created. Commit nothing. Tell the owner which move needs which edit, then return to Phase B with that edit as a constraint for both runners, and stop again at Phase C.

### Push back

The owner replies `Push back on A: <reason>` or `Push back on B: <reason>`.

If the human pushes back on the shape (at the pick or after the fact), treat that as Phase A evidence. Re-ground and re-run Phase B before writing more code. The reason becomes a constraint in both runners' prompts, with the candidate it rejects named as the shape not to repeat. A push back after the pick first removes what the rejected sketch wrote (revert its commits), so a rejected shape leaves no code behind. Write no file in between. Show two new candidates in Phase C and stop again.

## Phase D: Implement against the sketch

A layout pick has no Phase D: the run stops after the check's commit.

Replace `not implemented` bodies with code, pseudocode with logic. The picked sketch is the contract. Deviations from it are signal to surface, not friction to absorb silently. If a function needs a parameter the sketch didn't anticipate, ask whether the sketch was wrong, the requirement was missed, or the implementation is overreaching.

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

## Outputs

The caller's usage is written first and the type sketch derived from it. One file with new types and signatures for small changes. Module map plus type definitions for larger work. The rationale ships alongside, shaped per `references/rationale-template.md`, including the usage sketch and the pick decision, as the pull request body.

## Credit

Adapted from pstack's `architect` by Lauren Tan (MIT; see `LICENSE`).
