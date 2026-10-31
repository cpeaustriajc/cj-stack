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

For a layout re-architecture, where the task moves code between files and folders and changes no
behaviour, read `references/layout.md` before Phase C: it shows **Today** as a file tree with line
counts, and each candidate as Tree after, Moves, Rule after, Red flags and Tradeoff.

### Pick

The owner replies `Pick A` or `Pick B`.

Read `references/pick.md`, then write the picked sketch as stub files and the rationale as the
pull request body. A layout pick runs **Pick a layout** in `references/layout.md` instead.


### Push back

The owner replies `Push back on A: <reason>` or `Push back on B: <reason>`. Read
`references/push-back-and-scrap.md` before you write anything more.

## Phase D: Implement against the sketch

A layout pick has no Phase D: the run stops after the check's commit.

Replace `not implemented` bodies with code, pseudocode with logic. The picked sketch is the contract. Deviations from it are signal to surface, not friction to absorb silently. If a function needs a parameter the sketch didn't anticipate, ask whether the sketch was wrong, the requirement was missed, or the implementation is overreaching.

## Phase E: Scrap when the architecture is wrong

If implementation keeps producing friction the sketch can't absorb, from the first stub file of the
pick on, read `references/push-back-and-scrap.md`: it lists the tells, and you scrap only when the
owner replies Re-sketch.

## Outputs

The caller's usage is written first and the type sketch derived from it. One file with new types and signatures for small changes. Module map plus type definitions for larger work. The rationale ships alongside, shaped per `references/rationale-template.md`, including the usage sketch and the pick decision, as the pull request body.

## Credit

Adapted from pstack's `architect` by Lauren Tan (MIT; see `LICENSE`).
