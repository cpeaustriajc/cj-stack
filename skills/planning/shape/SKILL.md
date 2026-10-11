---
name: shape
description: >
  Shape one project in the team's tracker (Linear, Jira, GitHub Issues and Projects, or another):
  its spec with numbered requirements, its milestones, and the project description, under a
  product from `vision` and above work items from `tickets`. Covers where a spec, requirement,
  dependency, risk or decision lands, who owns each level, project audits and status updates. Use
  before creating or restructuring any project, epic, spec or milestone; when I say "shape this",
  "put this in a doc", "write the spec" or "set a milestone"; when a spec arrives pasted into a
  single ticket; when direction changes after a demo; and when drafting or auditing a project
  description or a weekly update.
---

# Shape

Planning goes wrong in a few predictable ways. A spec gets filed as a ticket and built before
anyone confirmed it. Requirements name endpoints instead of behaviour. A project never ends, or a
ticket is so long it is really two tickets. This skill is the method that prevents those. The
method is the same on every tracker; only the adapter changes.

## The three levels

Planning runs top-down through three skills. This one is the middle, and owns the tracker
adapters the other two read.

| Skill | Level | Holds |
|---|---|---|
| `vision` | Product | Destination, features F1…Fn, not yet specified, out of scope |
| `shape` | Project | Spec with requirements R1…Rn, testing seams, milestones |
| `tickets` | Work item | One slice, citing the requirements it meets |

`triage` asks the open questions at any level. Five rules hold the levels together:

1. **Read the level above first.** A project starts from one feature of the product. With no
   product, offer `vision` for a minimal one first; a one-off internal tool may stand alone if I
   say so.
2. **Every item cites its parent.** A project names its feature, every requirement serves the
   project's Done, every work item names its requirements. Nothing exists without a parent.
3. **A level is built only from a confirmed parent.** A Draft product gets no projects beyond
   one-line placeholders; a Draft spec gets no build items.
4. **Changes flow down, questions flow up.** A changed feature returns its project's spec to
   Draft. A changed requirement flags every item that cites it. A lower level never edits a
   higher one: a requirement found wrong while building goes up to me as a question.
5. **Status rolls up.** Items close milestones, milestones feed the project update, project
   health feeds the product update.

## 1. Find the tracker and the project's facts

**The tracker.** Stop at the first hit:

1. A pointer in the project's `CLAUDE.md` or `AGENTS.md`, for example `Tracker: Linear, team MP`,
   a Jira URL, or `GitHub issues`.
2. The connected tools: a Linear MCP server means Linear; an Atlassian MCP server or the `acli` CLI
   means Jira; a GitHub remote with `gh` signed in means GitHub.
3. Ask once, and offer to add the pointer line.

Then read the matching adapter. It maps the levels below onto that tracker's objects and names the
tools that reach it.

| Tracker | Adapter |
|---|---|
| Linear | `references/linear.md` |
| Jira (with Confluence for documents) | `references/jira.md` |
| GitHub Issues and Projects | `references/github.md` |
| Asana, ClickUp, Notion, Trello, a markdown file, anything else | `references/other-trackers.md` |

**The project's facts.** Who holds each role, which templates the team has, which areas are too
risky to skip QA, where older specs live. Look for a project reference: a tracker section in
`AGENTS.md` or `CLAUDE.md`, or a file it points to. Project facts override the defaults here. If
there is none, ask only what the task needs. On a solo project one person holds every role.

**Roles** used below:

- **Product owner**: writes intent, priority and requirements, and accepts releases.
- **Approver**: confirms direction, often after a demo. Usually the product owner; sometimes
  someone above them who steers through the product owner.
- **Verifier**: marks work done. QA if the team has it, otherwise the product owner.
- **Engineering**: decomposition, work types, feasibility and the shape of the work.

## 2. The levels in the tracker

| Level | Owner | Holds |
|---|---|---|
| Product | Product owner | The product's destination and features; see `vision`. Projects link to it rather than repeat it. |
| Project | Product owner writes intent, engineering the structure | One feature with an end: Why, What, How, Not in scope, Success. |
| Spec | Product owner writes, engineering formats | The spec template in `references/templates.md`. A status line at the top: Draft, or Confirmed (date, by whom). |
| Engineering document | Engineering | At most one per project; see section 5. |
| Decision | Whoever decided | One per decision; see section 5. |
| Phase | Engineering | One of the fixed phases in `references/phases.md`, as a milestone. Its exit check, not its progress bar, says when it ends. |
| Work item | Engineering writes, product owner approves the Done When | See `tickets`. |
| Done | Verifier | Only a defect against the quoted requirements reopens it. A new ask is a new item. |
| Accepted | Product owner | The released feature checked against the spec's requirements. |

**Structure follows confirmation.** A spec stays one document until the approver confirms it,
and work items are cut from it one slice at a time. When the approver changes direction, which
often happens after a demo, only the document changes, and nothing already cut is thrown away.

## 3. Shape a project

1. **Read the parent.** Open the product and the feature this project serves. Quote the
   feature's line; the project's Done must deliver it.
2. **Settle the decisions.** If any decision about the project is open, run `triage` first.
   The spec records decisions; it is not a place to make new ones, and it invents nothing to fill
   a section.
3. **Agree the testing seams** with me before writing: where the feature will be proven. Prefer
   existing seams to new ones and the highest seam that works; one is ideal.
4. **Write the spec** from the template in `references/templates.md`, as a Draft, in the
   project's own vocabulary. Then draft or update the project description from the same file.
5. **Set the phases** from `references/phases.md` as the project's milestones. A product project
   starts in Demo; an unknown that a prototype can settle becomes a throwaway Demo item, not a
   question for me.
6. **Check the tree** (section 7), then hand back. When the approver marks the spec Confirmed,
   `tickets` cuts the first slice.

## 4. Rules

- **Requirements are statements, not tasks.** Each one says who does what and what they see. They
  never name a data source, vendor, endpoint, model or timing budget, because the product owner
  must be able to confirm them and mechanism buries intent. Mechanism goes in one line of the
  project How and in detail in the engineering document. When a statement mixes the two, keep
  the outcome half and link the decision behind the mechanism.
- **Requirements cover the unhappy paths**: empty, error, slow and edge states, not only the main
  flow.
- **Product and project descriptions use a neutral present tense.** "Buyers save names to a
  shortlist", never "will let", "was moved" or "is being built". Change over time belongs in
  status updates, so the description stays true as the project moves.
- **Phases carry no target date** unless someone asks, and then only Launch. Dates on every phase
  turn the project into a waterfall.
- **The spec is intent, not build instructions.** Build from work items only. A Draft spec never
  has build items cut from it.
- **Convert, never cancel.** A spec filed as a ticket moves into a spec document; the ticket goes
  back to the backlog or becomes the first build slice. Cancelling it reads as a verdict on the
  author's work.
- **Feasibility gate.** No work item is ready until engineering confirms it names only systems the
  team owns or has a contract for. Probe the upstream system first: the answer often removes the
  dependency.
- **Use the tracker's templates** when the team has them, and read their current text in the
  tracker before writing. Don't copy them into files, where they go stale.
- **Don't invent** owners, dates, measurements, dependencies or decisions. Leave them blank or list
  them as open questions.

## 5. Documents

A project has a **spec** for the product owner plus **one** engineering document at a time,
chosen by who reads it:

- **Proposal**: a change another team must accept. Draft, Agreed, Shipped. Once Agreed, its
  interface moves into an API contract, which replaces it.
- **API contract**: an interface one side builds and another consumes, so both can build at once.
- **Technical design**: work that stays inside one codebase.

A small project with nothing to agree skips the engineering document; the project How carries the
mechanism. Don't call any of them "tech spec" or "PRD": "spec" means the product side only.

**Decisions** don't count toward that limit. If the `project-knowledge` skill is installed, it owns
how decisions are found, recorded and superseded. Otherwise file one document per decision titled
`Decision: <Topic>`, with the topic as a plain statement and no number, in the project it belongs
to; superseding changes only the old one's status line.

## 6. Operations

- **Shape a spec** pasted into a ticket, or translated from an old epic or brief: read
  `references/spec-mapping.md`.
- **Set up or move phases:** read `references/phases.md`.
- **Draft or audit a project:** read the project template in `references/templates.md`. First
  check that it is a project at all: one outcome with an end and several work items. Flag a single
  ticket dressed up as a project, a permanent category posing as one, or two unrelated outcomes in
  one, rather than silently repairing it. Read the current project, its product, phases and
  dependencies before revising it.
- **Write a status update:** read the update shape in `references/templates.md`.
- **Cycles or sprints** are a team's cadence for choosing what matters next, not project
  containers or release promises. Assign them to work items, never to project descriptions, and let
  unfinished items roll forward without treating that as failure.

## 7. Writing to the tracker and checking the tree

Drafting, auditing or translating never authorises a write. Before any write, state the exact
item and change; afterwards, read it back and report what the tracker now holds. Show the person
the first write to a shared tracker before making it: the whole team sees it at once, and many
trackers notify a channel on every save, so batch related changes into one write.

After writing, read the tree back from the tracker into the outline in
`references/tree-outline.md` and run `python3 scripts/check_tree.py <outline.json>` from this
skill's folder. Fix every line it prints before handing back, or say why one stays.
