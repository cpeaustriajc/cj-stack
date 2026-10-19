# github-issue

A skill that told Claude to keep a Jira ticket's engineering detail in a GitHub issue, one issue for each ticket.

> Archived: not maintained.

## When to use it

Use it only if you split product text in Jira from engineering text in GitHub. To write tickets for any tracker, use [`tickets`](../../planning/tickets/README.md) instead.

The skill covered file paths, code symbols, API fields, probe numbers, latency budgets and architecture choices. The product owner and QA read Jira only. The engineer reads both.

Do not use it for the product text of a ticket: that is `jira-ticket`.

## Example

You say: "Move the engineering notes from this draft to GitHub."

1. Claude writes one issue titled with the Jira key and the topic.
2. Claude assigns the sprint milestone and attaches story issues under the epic issue.
3. Claude deletes the engineering section from the local draft.

You get a draft that you can copy to Jira as it is, and an issue that holds the detail.

## Install

The `cj-jira` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-jira@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-jira@cj-stack`.

## What it does

- Claude creates issues with the `gh` command and uses the Jira key in the title as the only link between the two systems.
- Claude states the date and host next to every measured number.
- If it cannot reach GitHub, Claude returns the proposed text and does not claim it was published.

## Limits

- It was written for one project and still names that project's repository and reference files.
- It is not maintained.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the structure and content rules.
- [jira-ticket](../jira-ticket/README.md): the product side of the split.
- [draft-ticket](../draft-ticket/README.md): the loop that calls this skill.
