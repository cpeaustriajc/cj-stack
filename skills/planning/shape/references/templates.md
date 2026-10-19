# Templates

The team's own templates in the tracker win over these. Where the team has none, or its template
is missing a section below, use these shapes.

## Spec

Written from decisions already made (`grill`), never to make new ones. A section with nothing
real to say is left out rather than filled.

```markdown
Status: Draft | Confirmed (<date>, <approver>)
Feature: <the product feature this serves, quoted>

## Problem

<Whose problem, in their words, and the evidence.>

## Done

<The observable outcome: who does what, and what they see. One or two sentences.>

## Requirements

R1. <Who> <does what> and <sees what>.
R2. <An empty, error or edge state, stated the same way.>

## Testing seams

- <Where the feature is proven, highest first. One is ideal.>

## Approaches considered

- <The approach not taken, in one line, and why.>

## Out of scope

- <What was asked for or obvious, and deliberately left out.>

## Open questions

- <Must be empty before the spec is Confirmed.>
```

- **Requirements** are numbered once and never renumbered; a dropped one is struck through, so
  work items that cite it still resolve. A long list is fine: it should cover the feature.
- **Out of scope** is never empty on a Confirmed spec. The things refused are the most useful
  lines on the page.
- The spec cites no file paths or code; they go stale. A prototype's snippet that pins a decision
  (a state machine, a schema) may be inlined, marked as from a prototype.

## Project

Return the properties separately from the description, because the properties go in the tracker's
own fields:

```markdown
Name:
Summary:          <one sentence: the user or business outcome>
Lead:
Team(s):
Product:
Status:
Start:
Target:
Dependencies:

Description:
```

The description is a small, timeless spec of how the project works. It stays useful as the project
moves, so it holds no status narration, completed work, dated updates, migration history,
temporary blockers or next steps; those go in status updates or native fields.

```markdown
## Why

The enduring problem, who it hurts, and the evidence.

## What

- Three to five capabilities or changes a user can see.
- Behaviour, not implementation. No work-item acceptance criteria.

## How

The product and technical decisions that define how it works, plus any open decision. Only
constraints that shape the project; detailed plans go in the engineering document.

## Not in scope

The nearest problems this project deliberately leaves alone.

## Success

The one condition, measure or observation that says it worked. A guardrail only when needed.

## Risks

Only risks that change what gets built. Omit if none.

## Open questions

| Question | Owner | Needed by |
| --- | --- | --- |
```

Leave Owner blank unless someone named the owner; a role guessed from the question's topic is an invented owner.

Omit Open questions once the scope is settled. Revise the description only when the intended
behaviour or boundary changes.

A project for an **internal tool** (one only the team uses: a test harness, a mock of another
team's system, a QA panel) uses the same sections, and its How also says:

- whose behaviour it copies, if it stands in for another team's system, and where it deliberately
  differs, with the decision that allowed each difference;
- whether one person's use affects anyone else's, because testers share these tools.

If buyers or end users will ever see the result, it is a product project, even when the team uses
it first.

**Keep out of the description**, in the tracker's native fields instead: lead, members and teams;
product and status; priority and dates; phases; dependencies; links and resources; health.

## Status update

```markdown
Health: on track | at risk | off track

Progress:
Risks:
Next:
```

Health is the project lead's judgement: if the facts given don't settle it, propose one and say it needs their confirmation. Only rate health when an update was asked for. Read what changed since the previous update first. Report changed scope, dates, lead, dependencies
or phases. Counting finished items does not replace the lead's judgement: a project with most items
done can still be at risk if the remaining one is blocked on another team.
