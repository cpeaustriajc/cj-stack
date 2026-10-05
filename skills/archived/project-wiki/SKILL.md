---
name: project-wiki
description: >
  Keep a repo's GitHub wiki: the decisions log (one "Decision NNN <Topic>" page per decision,
  indexed newest first) and the research pages behind it. Use when recording or changing a
  decision, moving rationale, evidence or history out of CLAUDE.md, .claude/rules or README,
  writing up research, or when a project CLAUDE.md points at its wiki.
---

# Project wiki

The wiki holds **why**: decisions and the research behind them. It is written for people. It never
mentions Claude, agents, `CLAUDE.md`, `.claude/` or "auto-loaded". If a sentence is an instruction to
an agent, it belongs in `CLAUDE.md` or a rule, not here.

## Pages

- **Home**: one paragraph (the README is the spec, meaning what we build; [[Decisions]] records why;
  the research pages are below so nothing is re-derived), then a `| Page | What it answers |` table
  listing every page. End with a line saying that anything marked **UNVERIFIED** was not confirmed
  on a primary source.
- **Decisions**: the index and the template below. The table runs **newest first**, sorted by
  date, not by number. A new row goes at the top.
- **`Decision NNN <Topic>`**: one page per decision, numbered in the order recorded. It is **never
  rewritten.** To change a decision, write a new page, set the old one's status to
  `Superseded by [[Decision NNN …]]`, and update its index row.
- **Research pages**: one topic each (competitors, a vendor's terms, a naming round, an
  investigation). Date the research, and mark anything unconfirmed as **UNVERIFIED**. When newer facts
  replace what a page describes, the page describes the current state and the old text moves under
  `## History` at the foot, saying what replaced it. Do not delete it.

## Decision template

```markdown
# Decision NNN: <Topic>

**Status:** Proposed | Accepted | Superseded by [[Decision NNN …]]
**Date:** YYYY-MM-DD · **Issue:** [#N](../issues/N)

## Context
The problem, and links to the research pages.

## Decision
What we chose.

## Consequences
What it rules out and what it costs.
```

## Dates are evidence, not guesses

Take a decision's date from `git log` (the commit or session that acted on it), from an issue, or
from the user. If none exists, write the month and say the day is not recorded. A decision is not
the same as its build, so a page may carry both (`**Built:** YYYY-MM-DD (<sha>)`). Ask the user for
a reason that is not written down; do not invent one.

## Working on the wiki

- Clone `https://github.com/<owner>/<repo>.wiki.git` into the scratchpad. The wiki repo does not
  exist until the first page is created in the web UI.
- **Commit after every change.** An uncommitted wiki clone in a shared folder is lost the moment
  another agent re-clones it. Give each agent that reads the wiki its own clone path.
- Push once the user has seen the pages. Wiki pages bypass the pull-request flow.
- Link pages as `[[Page Name]]`. Keep dots out of page names, because the file name is the page
  name with spaces turned into hyphens.
- Before pushing, check: `grep -ril claude *.md` finds nothing, every `[[link]]` resolves to a
  file, and Home lists every page.
- Link from the repo with the full URL, `https://github.com/<owner>/<repo>/wiki/<Page-Name>`. A
  private repo has a private wiki, so an unauthenticated fetch returns 404 even when the page exists.
