# Item kinds

Read this when an item is a Bug or a Chore, when you pick its work type, or when a change is wide and mechanical. The method is in `SKILL.md`.

## A wide mechanical change

- **A wide mechanical change** (a rename whose call sites span the codebase) is the one exception
  to vertical slicing: add the new form beside the old, migrate callers in batches, then remove
  the old form, each its own item.

## A Bug

A **Bug** adds what was expected and what happened, with the steps that reproduce it, under
Context, and cites the requirement it breaks. The steps start from the reachable state, with its
trigger named, as a Done When check does.

## Work types and rules

- **Work types.** `Task` for anything a user can see, `Bug` for a defect, and `Chore` for work with
  no visible change: docs, tooling, dependencies, or a refactor that automated tests prove changes
  no behaviour. A Chore cites no requirement and skips the verifier, so it can't touch the areas
  the project lists as risky (sign-in and payment, typically). When unsure, it is a Task.
- **A Chore's body adds a check** that it really can skip the verifier. If any line is false, it
  is a Task:

  ```markdown
  ## No-QA check

  - [ ] It touches none of the areas the project lists as risky.
  - [ ] It renames or removes no route and no test selector.
  - [ ] Nothing a user or tester could notice changes.
  - [ ] Every user path it changes is covered by an automated test.
  ```

  Its Done When holds checks an engineer can confirm alone: a command that passes, a file state, a
  search that finds nothing, or the end-to-end command and where its trace is.
- **Labels, not separate items, split frontend from backend**, unless the halves ship separately.
  Sub-items hold the tasks under an item that is longer than one cycle.
- **A bug found after Done is a new item**, labelled Bug and related to the original. Reopening
  hides the history.
