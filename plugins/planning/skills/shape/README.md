# shape

A skill that turns one product feature into a project: a spec with numbered requirements, testing seams and fixed phases, written into your tracker.

## When to use it

Use it when planning goes wrong in predictable ways: a spec filed as a ticket, requirements that name endpoints, or a project that never ends. A tracker is a tool such as Linear, Jira or GitHub Issues.

- You say "shape this", "write the spec" or "set a milestone".
- A project, epic or milestone is created, restructured or audited.
- A spec arrives pasted into one ticket.
- Direction changes after a demo, or you need a project status update.

Do not use it for a vague product idea: use `vision`. Do not use it to cut tickets from a confirmed spec: use `tickets`. Do not use it to ask questions about one change: use `grill`.

## Example

You say: "Write the spec for the saved-searches project. The product lists it as F3."

1. Claude quotes F3 and lists what is still open.
2. Claude asks only the open questions, then asks where the feature is proven.
3. Claude writes a Draft spec with numbered requirements R1 to Rn.
4. Claude sets the phases as milestones and checks the plan tree.

You get a Draft spec, a project description and milestones. When the approver confirms the spec, `tickets` cuts the first slice.

## Install

The `planning` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install planning@dotfiles
```

To turn the plugin off, run `claude plugin disable planning@dotfiles`. This also turns off every other skill in `planning`. For other agents such as Codex, run `scripts/link-skills.sh` in the repo.

## What it does

- Claude finds your tracker and reads the matching adapter in `references/`: `linear.md`, `jira.md`, `github.md` or `other-trackers.md`.
- Claude writes the spec as Draft, with Problem, Done, Requirements, Testing seams, Out of scope and Open questions. A Confirmed spec needs Out of scope filled and no open questions.
- Claude writes each requirement as a statement of who does what and what they see, with no endpoint or vendor.
- Claude sets fixed phases as milestones: Demo, Implementation, Launch and Post Launch. An internal tool has no Demo. Phases carry no dates unless you ask.
- Claude converts a spec filed as a ticket into a spec document. It never cancels the ticket.
- Claude drafts a project status update with a health of on track, at risk or off track. The project lead confirms the health.
- Claude states each write before it makes it, and shows you the first write to a shared tracker.
- After a write, Claude saves the plan tree as JSON and runs `scripts/check_tree.py`. Add `--launch` when the project enters Launch.

## Limits

- It cuts no tickets. `tickets` does that.
- It does not mark a spec Confirmed. The approver does.
- A lower level never edits a higher one. A requirement found wrong while building comes back to you as a question.
- Claude cannot create what a tracker lacks. It hands you the text to paste.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [references/top-down.md](references/top-down.md): the five rules, roles and the tracker lookup.
- [references/templates.md](references/templates.md), [phases.md](references/phases.md), [spec-mapping.md](references/spec-mapping.md) and [tree-outline.md](references/tree-outline.md): the spec, the phases, old-spec translation and the tree JSON.
- [scripts/check_tree.py](scripts/check_tree.py) and [scripts/test_check_tree.py](scripts/test_check_tree.py): the tree check and its tests.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
