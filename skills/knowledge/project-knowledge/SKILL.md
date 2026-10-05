---
name: project-knowledge
description: >
  Read and keep a project's decision log and research pages wherever the team keeps them: GitHub
  wiki, Notion, Linear documents, Obsidian, Confluence or Google Docs. Use it whenever a decision is being made,
  changed, reversed or questioned ("what did we decide about X", "record this decision", "we
  changed our mind on…", "why is it like this"). Also use it when writing up research, when moving
  rationale, evidence or history out of CLAUDE.md, rules files or the README, and when a
  project's CLAUDE.md points at a wiki, Notion page, Linear project or vault. Use it even when the user just says
  "note that down" about a product or architecture choice.
---

# Project knowledge

A project's knowledge has two parts:

- **The decision log**: one page per decision.
- **Research pages**: the evidence behind the decisions.

It lives wherever the team already writes. That can be a GitHub wiki, a Notion workspace, an
Obsidian vault or Confluence. It never lives in the code repository: it is read and written
through a CLI or an MCP server at the moment it is needed. The conventions below are the same on
every backend; only the adapter changes.

The knowledge is written **for people**. It never mentions Claude, agents, `CLAUDE.md`, `.claude/`,
rules files or "context". An instruction aimed at an agent belongs in `CLAUDE.md` or a rules file.
A reason, a finding or a piece of history belongs here.

## 1. Find where it lives

Resolve the location in this order, and stop at the first hit:

1. **A pointer in the project's `CLAUDE.md`**: a line naming the decision log by URL or path, for
   example `Decisions: https://github.com/o/r/wiki/Decisions`, a `notion.so/…` link, or
   `obsidian: ~/Vaults/Work/Projects/renav`. Infer the backend from the URL or path.
2. **The user-level map** `~/.claude/project-knowledge.json`. It maps a git remote, or an absolute
   repo path, to a location string in the same format.
3. **Detection.** If the repo has a GitHub remote, run `scripts/ghwiki.sh detect`. It reports
   whether the repo's wiki exists.
4. **Ask the user once.** Offer the backends that their connected tools make possible, then save
   the answer to the user-level map so no one is asked again. Add a pointer line to `CLAUDE.md` only
   if the user wants the repo to carry it.

Then read the matching adapter:

| Backend | Adapter |
|---|---|
| GitHub wiki | `references/github-wiki.md` |
| Notion | `references/notion.md` |
| Linear documents | `references/linear.md` |
| Obsidian vault | `references/obsidian.md` |
| Confluence, Google Docs, anything else | `references/other-backends.md` |

## 2. The shape of the knowledge

- **Home** (or the workspace's root page). One paragraph says the README is the product spec,
  meaning what we build, and the decisions record why. Below it, a `Page | What it answers` table
  lists every page.
- **Decisions index.** A table, **newest first by date**, with columns `# | Decision | Status |
  Date | Issue`. A new row goes at the top. Sort by date, not by number: numbers follow the order
  decisions were recorded, and they can be out of date order.
- **`Decision NNN <Topic>`.** One page per decision, numbered with zero padding (`001`). **It is
  never rewritten.** Its facts and wording stay as they were decided. That lets a reader trust any
  old decision page as a record of what was known then.
- **Research pages.** One topic each. Date the research, and mark anything not confirmed on a
  primary source as **UNVERIFIED**. When newer facts replace what a page describes, rewrite the page
  to describe the current state, and move the old description under `## History` at the foot, saying
  what replaced it. Deleting it would erase the evidence behind older decisions.

### Decision template

```markdown
# Decision NNN: <Topic>

**Status:** Proposed | Accepted | Superseded by [[Decision NNN …]] | Partly superseded by [[Decision NNN …]]: <the part>
**Date:** YYYY-MM-DD · **Issue:** [#N](link) or "none recorded"

## Context
The problem, and links to the research pages.

## Decision
What we chose.

## Consequences
What it rules out and what it costs.
```

Use the backend's own link syntax: `[[Page]]` on a wiki or in Obsidian, a page mention in Notion.

## 3. Operations

**Answer "what did we decide about X".**
1. Search the decisions index and the decision pages, and read every match in full.
2. Follow each "Superseded by" and "Partly superseded by" link to the end of its chain before
   answering. For a partial one, say which part still stands.
3. Report the current decision first, then whatever it replaced.
4. Quote its date and its page name, so the user can check it.
5. If nothing matches, say so. Don't answer from the code or from memory as if it were the record.

**Record a decision.**
1. Read the index and take the next number.
2. Write the page from the template.
3. Add its row to the top of the index.
4. Add or update the Home row, if the decision creates a page.
5. Link the research pages it rests on.

**Supersede a decision.**
1. Record the new decision as a new page, and have its Context say what changed since the old one.
2. On the old page, change **only** the Status line to `Superseded by [[Decision NNN …]]`.
3. In the index, update the old row's Status and add the new row at the top.

Never edit the body of the old page.

**When only part of it is replaced**, the rest still stands, so the old decision stays in force.
Write its Status as one line: `Partly superseded by [[Decision NNN …]]: <the part replaced>`, for
example `Partly superseded by [[Decision 010 Polar Web Checkout]]: the App-Store-only rule`. Put the
same words in its index row. The new page's Context names the part it replaces and says the rest
of the old decision stands. When several decisions each replace a different part, list them in one
Status line, separated by `;`. Once no part is left, the Status becomes plain `Superseded by`.

**File research.** Write the page or add to one, date it, and add the Home row. If it replaces
earlier findings, move them under `## History`.

**Move rationale out of a repo.**
1. Take text that explains why, gives evidence, measures something, records a rejected
   alternative, or tells history.
2. Put it on the matching research page or decision page.
3. Rewrite anything addressed to an agent so it reads as project history, for people.
4. Leave the instruction itself in the repo, where agents load it.

## 4. Dates and reasons are evidence

A decision's date comes from somewhere checkable:

- the commit or session that acted on it (`git log --all --date=short --grep=…`, or the log of
  the files it changed)
- an issue
- the user's word

If none exists, write the month and say that the day is not recorded. A decision and its build
are different events, so a page may carry both: `**Built:** YYYY-MM-DD (<sha>)`.

**Never invent a reason.** If the record does not say why something was chosen, the page says the
reason is not recorded, and you ask the user. A plausible reason that nobody gave is worse than a
gap: every later decision builds on it.

## 5. Writing safely

- **Show the user new or changed pages before publishing** a first write to a shared space.
  Publishing to a team's Notion, Confluence or public wiki is visible to everyone. After the user
  has approved the shape once, a routine new decision can be published and then reported.
- **Never lose work.** Commit or save after every change. See each adapter for how. With parallel
  agents, give each one its own working copy, or make one agent own the writes.
- **Before publishing, check that:**
  - no page mentions Claude or agents
  - every internal link resolves
  - Home lists every page
  - the index is newest first
