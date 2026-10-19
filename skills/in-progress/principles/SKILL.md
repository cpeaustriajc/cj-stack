---
name: principles
description: >
  This skill should be used when the user names an engineering principle, such as "apply prove
  it works", "subtract before you add" or "attack the premise", and before a design, test,
  debugging or measurement decision. It indexes 20 principles; Claude reads the one it applies
  and cites it with the decision it changed. Not for picking a work playbook (playbooks) or
  reviewing a diff (interrogate).
---

# Principles

One shared vocabulary of engineering rules. Each name points at one rule in
`references/<name-in-kebab-case>.md`. The user steers with a name; you cite a name for each
decision it changed.

## Apply

1. Pick each principle whose "when" fits the decision in front of you. A principle the user
   names always applies.
2. Read the leaf in full before you apply it. The index line is not the rule.
3. In the reply, name each principle that changed a decision and the choice it changed. For
   example: "Attack the Premise: tested the cache-key premise before fix 3; it was false."
4. Cite only a leaf that you read in this session. A citation with no changed decision behind
   it is name-dropping: leave it out.

## Index

### Core

- **Laziness Protocol**: sizing a diff, or about to add a layer or a flag. One decision in one
  place; the smallest change.
- **Foundational Thinking**: before the logic of new code. Data shapes and scaffold first.
- **Redesign From First Principles**: a new requirement for a design that exists. Build what
  you would build from zero, then update each reference.
- **Attack the Premise**: two fixes on one shared premise failed. Write the premise down and
  test it before fix 3.
- **Subtract Before You Add**: planning an addition, a refactor or a rewrite. Remove dead
  weight first.
- **Minimize Reader Load**: code that is hard to trace. Fewer layers to trace, less state to
  hold.
- **Outcome-Oriented Execution**: a declared migration with phases. Go to the target; no
  temporary compatibility code.
- **Experience First**: product, UX or scope trade-offs. The consumer's and the maintainer's
  experience before your convenience.
- **Exhaust the Design Space**: a decision with no precedent. Compare 2 or 3 prototypes first.
- **Build the Lever**: any work that is not trivial. Build the script that does or proves it.

### Architecture

- **Model the Domain**: stateful logic or many branches. One structure, not scattered
  conditionals.
- **Boundary Discipline**: placing validation or error handling. Check at system boundaries,
  trust inside, keep logic pure.
- **Type System Discipline**: types or signatures in a typed language. Make illegal states fail
  to compile.
- **Make Operations Idempotent**: steps that run amid crashes and retries. Each run ends in the
  same state.
- **Separate Before Serializing Shared State**: actors that may write one target at the same
  time. Remove the sharing before you add a lock.

### Verification

- **Prove It Works**: before "done", and when a check fails. Check the real thing; suspect the
  observation first.
- **Fix Root Causes**: debugging. Find the first wrong decision; a guard is a fix only for a
  legitimate state.
- **Sequence Verifiable Units**: multi-step work and commit order. One change, one check; the
  commit order proves the work.
- **Test Behavior, Not Implementation**: writing or keeping a test. It fails when the behavior
  breaks and passes when only internals change.
- **Explain the Number**: before you trust a measured number. Name its limiter and rule out
  what else it measured.
