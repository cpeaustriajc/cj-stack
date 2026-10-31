---
name: tickets
description: >
  This skill should be used when the user says "break this into tickets", "cut the next slice",
  "write the issue", "file these bugs as issues" or "rewrite this ticket", or a ticket is too
  long. It writes slices, or one bug or chore.
---

# Tickets

The work-item level of a top-down plan. Read `../shape/references/top-down.md` first: the five
rules, finding the tracker, and how writes are made and checked. The adapter's Work item,
Sub-item, Work type and Dependency rows say where each part below lands.

## 1. Read the spec

Open the project's spec. If it is Draft, stop: only prototype items for its Demo phase may be cut,
and say what would confirm it. Otherwise list its requirements and which ones existing items
already cite.

Read the facts an item rests on from the trunk, not the current branch: fetch it first, and search
open and recently closed items for the same work. A branch behind the trunk files work that is
already done.

## 2. Cut the next slice

Cut the next slice only, not the whole spec: the spec lasts, while items are cut as the work
moves and thrown away when direction changes.

- **Vertical, not layered.** Each item cuts a narrow but complete path through every layer the
  feature touches, and is demoable or verifiable on its own. A schema-only or API-only item is a
  layer, not a slice.
- **Sized for one session.** One fresh agent session or one person's day finishes it. Split one
  that needs more than five test cases, has more than five Done When checks, or touches several
  unrelated parts of the code.
- **Prefactor first.** A change that makes the slice easy goes in its own item, before it.
- **Order by what blocks.** Give each item the items that must finish before it starts; an item
  with none can start now. The riskiest unknown goes first.
- **Stack an Implementation slice.** When the slice sits under a project-sized container, is in
  the Implementation phase, and has two or more items that ship code, it is one stacked-PR chain:
  read `references/stacking.md` before you list the slice. A lone work item with no project, a
  small fix, Demo prototypes, Launch items and Post Launch bugs branch off the trunk.
- **A wide mechanical change** (a rename whose call sites span the codebase) is the one exception
  to vertical slicing: see `references/item-kinds.md`.

Show me the slice as a list before writing anything: each item's title, the requirements it
cites, what I would see when it is done, what blocks it, and for a stack its position and the
branch it builds on, bottom first. Ask whether the granularity and the
blocking are right, and iterate until I approve. That is the only question at this level. Any
other question means the spec is unclear, so it goes up to `shape` as a spec change rather than
being settled inside a ticket, where nobody would find it again.

## 3. Write each item

```markdown
## Context

<Why this exists now, the evidence, and the links that stop someone rediscovering it.>

## Outcome

<The concrete state that is true when this is done. One sentence.>

## Done When

- [ ] R3: <the requirement, quoted word for word>
- [ ] You see: <the screen, message or state that proves it>. Reach it with: <the account, data, switch or payment method that sets up that state>. (test | eye | engineer)
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
- **Each check is reachable.** It names what puts the app in its starting state: the account type,
  the kind of data ("a cart with a premium name", not "a domain"), the test switch, the payment
  method ("bank transfer, left unpaid"). If the state needs a trigger the reader would not guess,
  name the trigger. A verifier who must ask how to reach a state cannot test it.
- **A control's state is one exact word.** A check about a button, link or section says who sees
  it and gives one state: `visible`, `visible, refuses` (quote the message), `disabled` or
  `hidden`. Never "offers nothing", "does nothing", "unavailable" or "blocked": each reads as
  any of the four. Failure: "the panel offers nothing" meant `visible, refuses`; QA passed it as
  "hidden", and agents later treated both as true.
- **Each check names who proves it.** Hand testing, by a person or an agent clicking through, is
  the exception. `test` (the default): an end-to-end test drives it and records a video; the pull
  request gives the one command and where the video and report land. The verifier watches the
  video, so look and wording checks are `test` too. `eye`: no automation can reach it (a real
  device, a third-party inbox); say why. `engineer`: it needs access
  the verifier lacks (a database, a server setting, a burst of requests, a secret key), so the
  engineer runs it and attaches the command and its evidence; the verifier reviews that evidence.
- **Each check has an oracle the verifier can see.** Not "matches what the vendor does" without
  the exact text or state; not a count the screen does not show. A setting that persists says
  where it holds: this tab, this browser, any device.
- **A value on several pages agrees.** When the item shows one value (a price, a total, a count)
  on more than one page, one check names those pages and says each shows the same value for the
  same input: "the same name shows the same price on the shortlist, in the cart and at checkout".
- **Out of Scope:** 0–3 bullets.
- **Stack:** an item in a stack ends with a `## Stack` section that names its branch and its base;
  `references/stacking.md` has its form. Omit it on an item that branches off the trunk.
- **Whole body:** under about 1,500 characters. Longer means split it. Quoted requirement lines do
  not count; the tree check subtracts them, computed from the cited requirements.
- **No file paths or code**: they go stale. A prototype's snippet that pins a decision may be
  inlined, marked as from a prototype.
- **An item is self-contained**: someone who never saw the conversation can pick it up from the
  item and the spec it links.
- **No "As a … I want … so that" line** unless the product owner asks for it. That sentence is
  where mechanism and timing tend to sneak in.

A **Bug** adds what was expected, what happened and the steps to reproduce it: see
`references/item-kinds.md`.

## 4. Work types and rules

Before you give an item its work type (`Task`, `Bug` or `Chore`), read `references/item-kinds.md`:
a Chore adds a No-QA check, and a bug found after Done is a new item. When unsure, it is a Task.

## 5. Write and check

Write as `top-down.md` says, creating blockers first so later items link to real ids. For a
stack, write bottom first, so each Base names a branch that already has an item. Run the
tree check with `--launch` when the project is entering Launch; before that, its notes list the
requirements still waiting for a slice.
