# draft-ticket

A skill that ran a full loop to draft or revise one Jira ticket. The loop drafts locally, checks test categories, gets a review and moves engineering detail to GitHub.

> Archived: not maintained.

## When to use it

Use it only if you work with a Jira team and want this exact loop. To write tickets for any tracker, use [`tickets`](../../planning/tickets/README.md) instead.

The skill fits a request to write, revise or fix a ticket. The request can be a key, a URL or a sentence.

Do not use it for Linear work. Do not use it to plan a product or split a spec: use `shape` or `vision`.

## Example

You say: "Draft a story for the shortlist export."

1. Claude reads the source and restates the requirement in one sentence.
2. Claude drafts a markdown file outside the repository, not in Jira.
3. Claude checks each test category and sends the draft to the `qa-ac-critic` agent.

You get one file that holds only the Jira description. The title, labels, blocker links and open questions come in chat.

## Install

The `cj-jira` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-jira@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-jira@cj-stack`.

## What it does

- Claude loads the `jira-ticket` skill for the format. It loads `github-issue` when the source holds implementation detail.
- Claude checks the draft against a locked-decisions file in the project. A reversal becomes a named blocker.
- Claude asks before any Jira change.

## Limits

- It was written for one project and still names that project's files and tools. The `qa-ac-critic` agent is not in this repo.
- It is not maintained.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the steps and hard rules Claude followed.
- [jira-ticket](../jira-ticket/README.md): the ticket format.
- [github-issue](../github-issue/README.md): where the engineering detail went.
