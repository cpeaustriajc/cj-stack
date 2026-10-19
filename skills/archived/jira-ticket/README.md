# jira-ticket

A skill that told Claude how to write Jira stories, bugs and epics for one project, with acceptance criteria a product owner can read.

> Archived: not maintained.

## When to use it

Use it only if you work with a Jira team and want the format this skill set. To write tickets for any tracker, use [`tickets`](../../planning/tickets/README.md) instead.

The skill covered these parts of a ticket:

- A story sentence in one of three forms: user story, job story or enabler story.
- Acceptance criteria that describe what the reader sees.
- Functional testing requirements, grouped by test category.
- A light format for epics.

Do not use it for Linear projects or issues. Do not use it for engineering detail: that belonged in a GitHub issue, see `github-issue`.

## Example

You say: "Write a story for the shortlist toggle."

1. Claude picks the story form from a decision table and names it.
2. Claude drafts the criteria and the test scenarios.
3. Claude sends the draft to the `qa-ac-critic` agent before it calls the draft done.

You get a draft file for the description, and the title, labels and open questions in chat.

## Install

The `cj-jira` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-jira@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-jira@cj-stack`.

## What it does

The skill writes no files of its own. It changes how Claude drafts a ticket.

- Claude keeps product language in the ticket and moves implementation detail out.
- Claude uses a closed list of labels for themes and cross-team status.
- A draft does not allow a Jira change. Claude asks first.

## Limits

- It was written for one project and still names that project's ticket keys, labels and files. The `qa-ac-critic` agent is not in this repo.
- It is not maintained. The `tickets` skill replaces its job for any tracker.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the full format Claude followed.
- [draft-ticket](../draft-ticket/README.md): the drafting process around this format.
- [github-issue](../github-issue/README.md): where the engineering detail went.
