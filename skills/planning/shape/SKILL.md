---
name: shape
description: >
  This skill should be used when a project, epic, spec or milestone is created, restructured or
  audited in any tracker; when the user says "shape this", "put this in a doc", "write the spec"
  or "set a milestone"; when a spec arrives pasted into one ticket; when direction changes after a
  demo; and for a project status update. It writes a spec with numbered requirements, testing
  seams and phases, under a product from vision.
---

# Shape

Planning goes wrong in a few predictable ways. A spec gets filed as a ticket and built before
anyone confirmed it. Requirements name endpoints instead of behaviour. A project never ends. This
skill is the project level of a top-down plan, and holds the method that prevents those.

Read `references/top-down.md` first: the five rules, finding the tracker and its adapter, roles,
and how writes are made and checked.

## Levels in the tracker

| Level | Owner | Holds |
|---|---|---|
| Product | Product owner | Destination and features; see `vision`. Projects link to it rather than repeat it. |
| Project | Product owner writes intent, engineering the structure | One feature with an end: Why, What, How, Not in scope, Success. |
| Spec | Product owner writes, engineering formats | The spec template in `references/templates.md`, with a status line: Draft, or Confirmed (date, by whom). |
| Engineering document | Engineering | At most one per project; see Documents. |
| Phase | Engineering | One of the fixed phases in `references/phases.md`, as a milestone. Its exit check, not a progress bar, ends it. |
| Work item | Engineering writes, product owner approves the Done When | See `tickets`. |
| Done | Verifier | Only a defect against the quoted requirements reopens it. A new ask is a new item. |
| Accepted | Product owner | The released feature checked against the spec's requirements. |

## Shape a project

1. **Read the parent.** Quote the product feature this project serves; the project's Done must
   deliver it.
2. **Settle what is still open, and only that.** The product already settled who it is for, the
   destination and this feature's outcome; carry them in as Settled. Run `grill` on what
   remains; many open questions mean the product was too vague, so say so and offer to revisit
   `vision`. The spec records decisions and
   invents nothing to fill a section.
3. **Agree the testing seams** with me before writing: where the feature will be proven. Prefer
   existing seams and the highest one that works; one is ideal, because every extra seam is test
   code to keep in step.
4. **Write the spec** from `references/templates.md` as a Draft, in the project's own vocabulary,
   then the project description from the same file.
5. **Set the phases** from `references/phases.md` as milestones. A product project starts in Demo,
   where an unknown that a prototype can settle becomes a throwaway item rather than a question
   for me. Personal software uses the internal tool phases, since I confirm everything myself.
6. **Check the tree**, then hand back. Once the approver marks the spec Confirmed, `tickets` cuts
   the first slice; until then the spec stays one document, so a change of direction after the
   demo edits one page and throws nothing away.

## Rules

- **Requirements are statements, not tasks.** Each says who does what and what they see, and
  covers the empty, error, slow and edge states too. None names a data source, vendor, endpoint,
  model or timing budget: the product owner must be able to confirm it, and mechanism buries
  intent. Mechanism goes in one line of the project How and in detail in the engineering
  document.
- **Descriptions use a neutral present tense.** "Buyers save names to a shortlist", not "will
  let" or "is being built", so the description stays true as the project moves. Change over time
  belongs in status updates.
- **Phases carry no target date** unless someone asks, and then only Launch. Dates on every phase
  turn the project into a waterfall.
- **Convert, never cancel.** A spec filed as a ticket moves into a spec document; the ticket goes
  back to the backlog or becomes the first slice. Cancelling it reads as a verdict on the author.
- **Feasibility gate.** No work item is ready until engineering confirms it names only systems the
  team owns or has a contract for. Probe the upstream system first; the answer often removes the
  dependency.

## Documents

Besides the spec, a project has at most one engineering document at a time, chosen by who reads
it:

- **Proposal**: a change another team must accept. Draft, Agreed, Shipped; once Agreed, its
  interface moves into an API contract that replaces it.
- **API contract**: an interface one side builds and another consumes, so both build at once.
- **Technical design**: work that stays inside one codebase.

A small project with nothing to agree skips it; the project How carries the mechanism. "Spec"
means the product side only, so none of these is called a tech spec or PRD.

**Decisions** don't count toward that limit. If `project-knowledge` is installed, it owns them.
Otherwise file one document per decision titled `Decision: <Topic>` in its project; superseding
changes only the old one's status line.

## Other operations

- **A spec pasted into a ticket, or an old epic or brief to translate:** read
  `references/spec-mapping.md`.
- **Draft or audit a project:** read the project template in `references/templates.md`. First
  check it is a project at all: one outcome with an end and several work items. Flag a single
  ticket dressed up as a project, a permanent category posing as one, or two outcomes in one,
  rather than silently repairing it.
- **A status update:** the update shape in `references/templates.md`.
- **Cycles or sprints** choose what matters next; they are not project containers or release
  promises. Assign them to work items, never to project descriptions, and let unfinished items
  roll forward.
