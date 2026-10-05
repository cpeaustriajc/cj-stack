# Templates

The team's own templates in the tracker win over these. Where the team has none, or its template
is missing a section below, use these shapes.

## Work item (Task, Bug)

```markdown
## Context

<Why this exists now, the evidence, and the links that stop someone rediscovering it.>

## Outcome

<The concrete state that is true when this is done. One sentence.>

## Done When

- [ ] <One observable check. Behaviour someone can see, not test steps.>

## Out of Scope

- <Only the boundaries that prevent a likely misunderstanding. Omit the section if none.>
```

Length limits, because a long item is usually two items and a reviewer stops reading:

- **Context:** 2–4 sentences plus links. Probe data and architecture go in the pull request or the
  engineering document; link them.
- **Outcome:** one sentence.
- **Done When:** 3–5 checkboxes, one check each. A build item quotes the spec statements it
  satisfies here, word for word, plus any finer conditions the verifier needs. No click-by-click
  steps, no "record only" measurements, no "deliberately absent" lists.
- **Out of Scope:** 0–3 bullets.
- **Whole body:** under about 1,500 characters. Longer means split it.
- **No "As a … I want … so that" line** unless the product owner asks for it. That sentence is
  where mechanism and timing tend to sneak in. Keep their acceptance criteria.

A Bug adds what was expected and what happened, with the steps that reproduce it, under Context.

## Chore

The same four headings, plus a check that it really can skip the verifier. If any line is false,
it is a Task.

```markdown
## No-QA check

- [ ] It touches none of the areas the project lists as risky.
- [ ] It renames or removes no route and no test selector.
- [ ] Nothing a user or tester could notice changes.
- [ ] Every user path it changes is covered by an automated test.
```

Its Done When holds checks an engineer can confirm alone: a command that passes, a file state, a
search that finds nothing, or the end-to-end command and where its trace is.

## Project

Return the properties separately from the description, because the properties go in the tracker's
own fields:

```markdown
Name:
Summary:          <one sentence: the user or business outcome>
Lead:
Team(s):
Goal:
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
goal and status; priority and dates; phases; dependencies; links and resources; health.

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
