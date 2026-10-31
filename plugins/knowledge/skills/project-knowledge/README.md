# project-knowledge

A skill that keeps a decision log and research pages for your team. The pages live in the place your team already writes, such as a wiki or Notion, and they are written for people.

## When to use it

Use it when a decision or a finding must outlive the chat.

- You say "note that down as a decision" or "supersede that decision".
- You ask "what did we decide about X".
- You ask Claude to record research or a finding.
- A decision made in conversation will matter to others.

Do not use it for instructions to an agent: those belong in `CLAUDE.md`. It never stores the log in your code repository.

## Example

You say: "Note that down as a decision: we move from REST to tRPC for the internal API."

1. Claude finds your decision log, or asks you once where it lives.
2. Claude writes a `Decision NNN: <Topic>` page with Context, Decision and Consequences.
3. Claude adds the page to the top of the decisions index.

You get one new page and one new index row. In a shared space, Claude shows you the first write before it publishes.

## Install

The `knowledge` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install knowledge@dotfiles
```

To turn the plugin off, run `claude plugin disable knowledge@dotfiles`. This also turns off every other skill in `knowledge`.

A GitHub wiki needs the `gh` CLI signed in. Notion and Linear need their MCP server connected.

## What it does

- It finds the log in this order: a pointer line in your project `CLAUDE.md`, `~/.claude/project-knowledge.json`, GitHub wiki detection, then a question to you.
- It saves your answer to `~/.claude/project-knowledge.json`, so it asks once.
- Backends: GitHub wiki, Notion, Linear documents, Obsidian vault, and Confluence or Google Docs through MCP.
- A decision page is never rewritten. To supersede it, Claude changes only the Status line and adds a new page.
- When it answers "what did we decide", it follows each "Superseded by" link to the current decision.
- Research pages carry a date, and unconfirmed facts are marked UNVERIFIED. Replaced findings move under a `## History` heading.
- A decision date comes from a commit, an issue or your word. If none exists, Claude writes the month only.
- Claude does not invent a reason. If the record does not say why, the page says so and Claude asks you.
- Before it publishes, Claude reads each page for AI-sounding prose, such as arrows and metaphor nouns, and rewrites it.
- For a GitHub wiki, `scripts/ghwiki.sh` keeps one managed clone under `~/.cache/project-knowledge/github/<owner>/<repo>`.

## Limits

- It does not write agent instructions.
- It does not fake a write. If a backend has no create tool, Claude gives you the page text to paste.
- It never force-pushes a wiki.
- A GitHub wiki that was never initialised needs a first page, created in the web UI.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [references/github-wiki.md](references/github-wiki.md), [notion.md](references/notion.md), [linear.md](references/linear.md), [obsidian.md](references/obsidian.md) and [other-backends.md](references/other-backends.md): one adapter for each backend.
- [references/operations.md](references/operations.md): supersede a decision, file research, move rationale out of a repo.
- [references/plain-prose.md](references/plain-prose.md): the prose patterns to rewrite before a page is published.
- [scripts/ghwiki.sh](scripts/ghwiki.sh): the GitHub wiki helper.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
- [evals/evals.json](evals/evals.json): test cases in skill-creator format.
