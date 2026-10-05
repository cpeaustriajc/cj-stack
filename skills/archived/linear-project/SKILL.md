---
name: linear-project
description: Draft, audit, create, or update Linear projects, including translating Jira epics or product briefs into outcome-sized projects. Use for project descriptions, project properties, milestones, dependencies, lifecycle, and project updates; do not use for issue-sized work.
---

# Linear projects

Treat a Linear project as a time-bounded product outcome containing multiple
issues. Do not mirror Jira epics one-for-one or use projects as permanent
backlog categories.

## Choose the right Linear object

Before drafting, classify the request:

- **Initiative** — a strategic outcome that groups multiple projects.
- **Project** — a feature or meaningful outcome with a completion condition,
  normally involving multiple issues and contributors.
- **Issue** — independently deliverable implementation, design, QA, research,
  or defect work.
- **Document** — research, a specification, or a decision record without a
  delivery lifecycle.
- **Ongoing program** — prefer an initiative with time-bounded projects.
  Recommend a project without an end only when the continuing container is
  deliberate, such as maintenance or recurring quality work.

Flag rather than silently repair work that is too broad, combines unrelated
outcomes, lacks a completion condition, or is a single issue disguised as a
project.

## Evidence and current state

Read the current Linear project, related initiative, teams, milestones, and
dependencies before revising it. When Jira is a source, use TWG read-only
queries and inspect the requested epics; Jira titles alone are not sufficient
when their descriptions conflict or overlap.

Treat an old Jira epic as evidence of the problem someone wanted solved, not as
an authoritative technical specification. Its architecture, named services,
data flows, estimates, and implementation acceptance criteria are hypotheses
unless current code, tests, contracts, or a newer explicit decision confirm
them. This is especially important when the author did not have the current
engineering context.

Current product decisions and current code outrank stale Jira implementation
plans. Preserve Jira keys as source provenance, recover the user or business
intent, and draft from the verified present state rather than copying Jira
structure or prose. When sources conflict, ask the user about the unresolved
product choice; do not ask them to settle a technical question the repository
or current contract already answers.

Account for every source epic as one of:

- translated into a project;
- consolidated with another epic;
- split into multiple outcome-sized projects;
- retained as initiative/reference context; or
- held for a product decision.

Consolidate multiple Jira epics when they describe one current Linear outcome.
Do not preserve a one-file-per-epic structure when it would create duplicate
project descriptions; list every contributing Jira key on the consolidated
draft instead.

Do not invent owners, dates, measurements, dependencies, or decisions. Leave
unknowns blank or record them under Open questions.

## Project draft

Return project properties separately from the description:

```markdown
Name:
Summary:
Lead:
Team(s):
Initiative:
Status:
Start:
Target:
Dependencies:

Description:
```

The summary is one sentence describing the user or business outcome. The
description is a timeless, small specification of how the project works. It
must remain useful as the project progresses: do not put status narration,
completed work, dated updates, migration history, temporary blockers, or next
steps in it. Put those in Linear project updates or native fields instead.

Use this description template unless the user supplies another structure:

```markdown
## Why

The enduring problem, who it hurts, and the evidence.

## What

- Three to five user-visible capabilities or changes.
- Describe behavior, not implementation.
- Keep issue-level acceptance criteria out of the project.

## How

The key product and technical decisions that define how the project works, plus
any genuinely open decision. Include only constraints that materially shape
the project; put detailed implementation plans in linked documents or issues.

## Not in scope

The closest adjacent problems this project deliberately leaves alone.

## Success

The one completion condition, measure, or observation that tells us it worked.
Add a guardrail only when needed.

## Open questions

| Question | Owner | Needed by |
| --- | --- | --- |
|  |  |  |
```

Omit an empty Open questions section when the scope is settled. Preserve a
user-supplied template unless a correction prevents ambiguity or misuse; call
out the correction rather than silently changing their structure.

Project descriptions and project updates are complementary. Keep the
description stable as the small product spec; use progressive updates for what
changed, what was learned, health, risks, and what happens next. Revise the
description only when the project's intended behavior or boundary changes.

## Native project structure

Keep these out of the prose description and represent them with Linear's
native fields or objects:

- lead, members, and team ownership;
- initiative and project status;
- priority, start, and target timeframe;
- milestones and their target dates;
- project dependencies;
- resources, specifications, and external links;
- project health updates.

Milestones are the fixed phases from the `linear-planning` skill: Demo,
Implementation, Launch, Post Launch for a `Product Outcome` project, and
Implementation, Launch, Post Launch for an `Internal Tool` project, whose users
are the team rather than buyers. Do not invent others, and do not split
milestones into frontend and backend.

## Cycles and momentum

This team follows Linear's Cycles and Build Momentum practices, not Scrum.
Translate legacy delivery-process language into Linear's native model rather
than preserving roles, ceremonies, or sprint commitments.

- Initiatives set strategic direction; projects define bounded outcomes;
  issues are the small executable work pulled into cycles.
- Cycles are a repeating team cadence for deciding what matters next. They are
  not project containers, release promises, or miniature project plans.
- Plan cycles from project priorities and observed capacity. Keep scope
  reasonable, mix feature and quality work, and allow unfinished issues to
  roll forward rather than treating rollover as failure.
- Keep issues small enough to finish and review regularly so visible progress
  compounds. Prefer a shipped increment and new evidence over a large,
  speculative batch.
- Project milestones and target dates describe outcome stages across cycles.
  Assign cycle membership to issues, not to the project description.
- Use a cooldown only when configured for the team; never invent one from the
  methodology.

When a source uses Scrum or sprint language, preserve only the underlying
intent and translate it into initiatives, projects, issues, cycles, ownership,
and updates. Keep historical wording only when it is necessary provenance for
an explicit conflict.

## Project updates

For an active-project update, read changes since the previous update and
draft a native health value (`onTrack`, `atRisk`, or `offTrack`) plus concise
prose:

```markdown
Progress:
Risks:
Next:
```

Report changed scope, dates, leads, dependencies, or milestones. Quantitative
issue progress does not replace the project lead's qualitative judgment.

## Mutation boundary

Drafting, auditing, or translating does not authorize a Linear mutation.
Creating a project, changing properties, adding milestones or dependencies,
publishing an update, or completing/canceling a project requires explicit
authorization. Before any mutation, state the exact project and changes;
afterward, read the project back and report the verified result.

Keep external references attached as resources when useful. Never publish to
Linear, Jira, Slack, or another system merely because the draft is complete.
