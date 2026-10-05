---
name: work-planning
description: >
  Shape and keep product work in the team's tracker (Linear, Jira, GitHub Issues and Projects, or
  another), from a goal and a spec down to work items. Covers where a goal, spec, story, acceptance
  criterion, dependency, risk or decision lands, who owns each level, the work-item and project
  templates, project audits and status updates. Use it before creating, splitting or restructuring
  any project, epic, milestone or issue; whenever someone says "ticket", "story", "write the issue"
  or "fix ABC-123"; when a spec arrives pasted into a single ticket; when direction changes after a
  demo; and when drafting or auditing a project description or a weekly update.
---

# Work planning

Planning goes wrong in a few predictable ways. A spec gets filed as a ticket and built before
anyone confirmed it. Acceptance criteria name endpoints instead of behaviour. A project never ends,
or a ticket is so long it is really two tickets. This skill is the method that prevents those. The
method is the same on every tracker; only the adapter changes.

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

- **Product owner**: writes intent, priority and acceptance statements, and accepts releases.
- **Approver**: confirms direction, often after a demo. Usually the product owner; sometimes
  someone above them who steers through the product owner.
- **Verifier**: marks work done. QA if the team has it, otherwise the product owner.
- **Engineering**: decomposition, work types, feasibility and the shape of the work.

## 2. The levels

| Level | Owner | Holds |
|---|---|---|
| Goal | Product owner | The product goal and its business and customer value. Projects link to it rather than repeat it. |
| Project | Product owner writes intent, engineering the structure | One feature or tool with an end: Why, What, How, Not in scope, Success. |
| Spec | Product owner writes, engineering formats | Intent, flows and acceptance criteria as statements, verbatim, no checkboxes, no dates. A status line at the top: Draft, or Confirmed (date, by whom). |
| Engineering document | Engineering | At most one per project; see section 4. |
| Decision | Whoever decided | One per decision; see section 4. |
| Phase | Engineering | One of the fixed phases in `references/phases.md`. Its exit check, not its progress bar, says when it ends. |
| Work item | Engineering writes, product owner approves the acceptance criteria | A plain task title and the work-item template. |
| Done | Verifier | Only a defect against the quoted statements reopens it. A new ask is a new item. |
| Accepted | Product owner | The released feature checked against the spec's statements. |

**Structure follows confirmation.** A spec stays one document until the approver confirms it,
and work items are split from it one slice at a time. When the approver changes direction, which
often happens after a demo, only the document changes, and nothing already split is thrown away.

## 3. Rules

- **Acceptance criteria are statements, not tasks.** They describe what a user sees and does. They
  never name a data source, vendor, endpoint, model or timing budget, because the product owner
  must be able to confirm them and mechanism buries intent. Mechanism goes in one line of the
  project How and in detail in the engineering document. When a statement mixes the two, quote the
  outcome half and link the decision behind the mechanism.
- **Goal and project descriptions use a neutral present tense.** "Buyers save names to a
  shortlist", never "will let", "was moved" or "is being built". Change over time belongs in status
  updates, so the description stays true as the project moves.
- **Phases carry no target date** unless someone asks, and then only Launch. Dates on every phase
  turn the project into a waterfall.
- **The spec is intent, not build instructions.** Build from work items only. A Draft spec never
  has work items split from it.
- **Convert, never cancel.** A spec filed as a ticket moves into a spec document; the ticket goes
  back to the backlog or becomes the first build slice. Cancelling it reads as a verdict on the
  author's work.
- **Feasibility gate.** No work item is ready until engineering confirms it names only systems the
  team owns or has a contract for. Probe the upstream system first: the answer often removes the
  dependency.
- **Labels, not separate items, split frontend from backend**, unless the halves ship separately.
  Sub-items hold the tasks under a story that is longer than one cycle.
- **A bug found after Done is a new item**, labelled Bug and related to the original. Reopening
  hides the history.
- **Work types.** `Task` for anything a user can see, `Bug` for a defect, and `Chore` for work with
  no visible change: docs, tooling, dependencies, or a refactor that automated tests prove changes
  no behaviour. A Chore skips the verifier, so it must not touch the areas the project lists as
  risky (sign-in and payment, typically). When unsure, it is a Task.
- **Use the tracker's templates** when the team has them, and read their current text in the
  tracker before writing. Don't copy them into files, where they go stale.
- **Don't invent** owners, dates, measurements, dependencies or decisions. Leave them blank or list
  them as open questions.

## 4. Documents

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

## 5. Operations

- **Shape a spec**, including one pasted into a ticket or translated from an old epic or brief:
  read `references/spec-mapping.md`.
- **Write or review a work item:** read the work-item template in `references/templates.md`.
- **Set up or move phases:** read `references/phases.md`.
- **Draft or audit a project:** read the project template in `references/templates.md`. First
  check that it is a project at all: one outcome with an end and several work items. Flag a single
  ticket dressed up as a project, a permanent category posing as one, or two unrelated outcomes in
  one, rather than silently repairing it. Read the current project, its goal, phases and
  dependencies before revising it.
- **Write a status update:** read the update shape in `references/templates.md`.
- **Cycles or sprints** are a team's cadence for choosing what matters next, not project
  containers or release promises. Assign them to work items, never to project descriptions, and let
  unfinished items roll forward without treating that as failure.

## 6. Writing to the tracker

Drafting, auditing or translating never authorises a write. Before any write, state the exact
item and change; afterwards, read it back and report what the tracker now holds. Show the person
the first write to a shared tracker before making it: the whole team sees it at once, and many
trackers notify a channel on every save, so batch related changes into one write.
