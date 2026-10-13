# project-wiki

A skill that kept a repository's GitHub wiki as a decision log with the research pages behind it.

> Archived: not maintained.

## When to use it

Use [`project-knowledge`](../../knowledge/project-knowledge/README.md) instead. It replaces this skill and works with the wiki, Notion, Linear, Obsidian or Confluence.

Use this skill only if the project keeps its decisions in a GitHub wiki and you want its page layout.

## Example

You say: "Record that we chose Postgres over SQLite."

1. Claude writes a numbered `Decision` page with status, date, context, decision and consequences.
2. Claude adds the new row at the top of the Decisions index.
3. Claude checks that Home lists the page.

You get a committed wiki page. Claude pushes only after you have seen the pages.

## Install

The `cj-jira` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-jira@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-jira@cj-stack`.

## What it does

- Claude clones the wiki into the scratchpad and commits after every change.
- A decision page is never rewritten. A new page supersedes the old one, and the old status line points to it.
- Research pages carry a date. Unconfirmed claims are marked UNVERIFIED.
- Claude takes a decision's date from git history, an issue or you. It does not guess.

## Limits

- It handles a GitHub wiki only. A private repository has a private wiki, so a fetch without sign-in returns 404.
- The wiki repository does not exist until someone creates the first page in the web UI.
- It is not maintained.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the page layout, decision template and checks.
