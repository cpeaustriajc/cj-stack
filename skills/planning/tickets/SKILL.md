---
name: tickets
description: >
  Cut a confirmed spec into work items in the team's tracker: thin end-to-end slices, each one
  demoable, sized for one session, citing the requirements it meets, with blocked-by links. Also
  writes or reviews a single work item, bug or chore. Use when I say "ticket", "break this into
  tickets", "cut the next slice", "write the issue", "file these" or "fix ABC-123"; after `shape`
  when a spec is Confirmed; and when a ticket is too long or does two things.
---

# Tickets

The bottom of three levels: `vision` for the product, `shape` for each project, `tickets` for each
slice. Read the five top-down rules in `../shape/SKILL.md` first; they hold here too. Find the
tracker and its adapter as section 1 there says; the adapter's **Work item**, **Sub-item**,
**Work type** and **Dependency** rows say where each part below lands.

## 1. Read the spec

Open the project's spec. If it is Draft, stop: only prototype items for its Demo phase may be cut,
and say what would confirm it. Otherwise list its requirements and which ones existing items
already cite.

## 2. Cut the next slice

The next slice only, not the whole spec: the spec lasts, items are cut as the work moves and may
be thrown away when direction changes.

- **Vertical, not layered.** Each item cuts a narrow but complete path through every layer the
  feature touches, and is demoable or verifiable on its own. A schema-only or API-only item is a
  layer, not a slice.
- **Sized for one session.** One fresh agent session or one person's day finishes it. Split one
  that needs more than five test cases, has more than five Done When checks, or touches several
  unrelated parts of the code.
- **Prefactor first.** A change that makes the slice easy goes in its own item, before it.
- **Order by what blocks.** Give each item the items that must finish before it starts; an item
  with none can start now. The riskiest unknown goes first.
- **A wide mechanical change** (a rename whose call sites span the codebase) is the one exception
  to vertical slicing: add the new form beside the old, migrate callers in batches, then remove
  the old form, each its own item.

Show me the slice as a list before writing anything: each item's title, the requirements it
cites, what I would see when it is done, and what blocks it. Ask whether the granularity and the
blocking are right, and iterate until I approve.

## 3. Write each item

```markdown
## Context

<Why this exists now, the evidence, and the links that stop someone rediscovering it.>

## Outcome

<The concrete state that is true when this is done. One sentence.>

## Done When

- [ ] R3: <the requirement, quoted word for word>
- [ ] You see: <the screen, message or state that proves it, specific enough to check>
- [ ] <Any finer condition the verifier needs.>

## Out of Scope

- <Only the boundaries that prevent a likely misunderstanding. Omit the section if none.>
```

- **Context:** 2–4 sentences plus links. Probe data and architecture go in the pull request or
  the engineering document; link them.
- **Outcome:** one sentence, from the user's side, not a layer-by-layer task list.
- **Done When:** 3–5 checks. Every requirement the item meets is quoted with its number; at least
  one **You see** line says what the verifier observes. No click-by-click steps, no "record only"
  measurements, no "deliberately absent" lists.
- **Out of Scope:** 0–3 bullets.
- **Whole body:** under about 1,500 characters. Longer means split it.
- **No file paths or code**: they go stale. A prototype's snippet that pins a decision may be
  inlined, marked as from a prototype.
- **An item is self-contained**: someone who never saw the conversation can pick it up from the
  item and the spec it links.
- **No "As a … I want … so that" line** unless the product owner asks for it. That sentence is
  where mechanism and timing tend to sneak in.

A **Bug** adds what was expected and what happened, with the steps that reproduce it, under
Context, and cites the requirement it breaks.

## 4. Work types and rules

- **Work types.** `Task` for anything a user can see, `Bug` for a defect, and `Chore` for work with
  no visible change: docs, tooling, dependencies, or a refactor that automated tests prove changes
  no behaviour. A Chore cites no requirement and skips the verifier, so it must not touch the
  areas the project lists as risky (sign-in and payment, typically). When unsure, it is a Task.
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
- **A requirement found wrong while building** goes up to me as a question for `shape`; the item
  never quietly changes it.
- **Use the tracker's templates** when the team has them, and read their current text first.

## 5. Writing to the tracker and checking the tree

Writing follows section 7 of `../shape/SKILL.md`: state each write before making it, show the
first one, batch the slice into as few writes as the tracker allows, and read it back. Create
blockers first so later items can link to real ids. Then read the project back into the outline
in `../shape/references/tree-outline.md` and run `python3 ../shape/scripts/check_tree.py
<outline.json>` from this skill's folder, with `--launch` when the project is entering Launch. Fix
every line it prints before handing back; its notes list the requirements still waiting for a
slice.
