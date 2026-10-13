# linear-project

A skill that told Claude how to draft, check and update a Linear project, and how to turn Jira epics into projects.

> Archived: not maintained.

## When to use it

Use [`shape`](../../planning/shape/README.md) instead. It replaces this skill and works in any tracker.

Use this skill only if you want to read how one team wrote Linear projects. The skill covered these parts:

- How to tell an initiative, a project, an issue and a document apart.
- A project description with the headings Why, What, How, Not in scope and Success.
- A project update with a health value, then Progress, Risks and Next.
- How to treat an old Jira epic as evidence of a problem, not as a specification.

Do not use it for issue-sized work or for where a spec lands: that was `linear-planning`.

## Example

You say: "Turn these three Jira epics into Linear projects."

1. Claude reads the current Linear state and the epics, not only their titles.
2. Claude accounts for each epic: translated, merged, split, kept as context or held for a decision.
3. Claude returns the project properties and the description as a draft.

You get a draft for each project. Claude changes nothing in Linear until you allow it.

## Install

No plugin ships this skill. The folder stays in the repository for reference only.

## What it does

The skill writes no files. It changes how Claude drafts.

- Claude keeps status, dates and next steps out of the description. They go in project updates.
- Claude does not invent owners, dates or measures. Unknowns stay blank or become open questions.
- Claude states the exact change and reads the project back after any change you allow.

## Limits

- It handles Linear only. It was written for one project and still names that project's practices.
- It is not maintained.

## More

- [SKILL.md](SKILL.md): the object choice, the description template and the update format.
- [linear-planning](../linear-planning/README.md): the owner table and the phase milestones that this skill points to.
