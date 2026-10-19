# linear-planning

A skill that told Claude where a spec, story, milestone or decision lands in Linear, and who owns each level.

> Archived: not maintained.

## When to use it

Use [`shape`](../../planning/shape/README.md) instead. It replaces this skill and works in any tracker.

Use this skill only if you want to read how one team mapped a product owner's spec onto Linear objects. The skill covered these parts:

- Which object holds what: initiative, project, document, milestone, issue.
- Fixed phase milestones, with no target dates.
- A short `Task` template for the issue body.
- A table that maps each section of a spec to its destination.

Do not use it for the text of a single project: that was `linear-project`.

## Example

You say: "The PO sent the new spec as one big ticket."

1. Claude moves the spec into a project document.
2. Claude sends the old issue back to the backlog and does not cancel it.
3. Claude splits issues from the spec one slice at a time, after the spec is confirmed.

You get a project with a spec document and the next slice of issues.

## Install

No plugin ships this skill. The folder stays in the repository for reference only.

## What it does

The skill writes no files. It changes how Claude plans in Linear.

- Claude reads the project's own Linear reference first, and asks if none exists.
- Claude keeps acceptance criteria as statements, with no vendor, endpoint or timing budget.
- Claude splits issues from a spec only after the spec is confirmed.

## Limits

- It handles Linear only. It was written for one project and still names that project's roles and files.
- It does not write the text of a project. See [linear-project](../linear-project/README.md).
- It is not maintained.

## More

- [SKILL.md](SKILL.md): the owner table, the rules, the templates and the spec mapping.
