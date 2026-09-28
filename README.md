# project-knowledge

A Claude Code skill that keeps a project's **decision log** and **research pages** wherever the team
already writes:

- a GitHub wiki
- Notion
- Linear documents
- Obsidian
- Confluence
- Google Docs

It reads and writes them through that backend's CLI or MCP server at the moment they're needed.
Nothing lands in the code repository except, optionally, one pointer line in `CLAUDE.md`.

## Install

```
/plugin marketplace add cpeaustriajc/project-knowledge
/plugin install project-knowledge@cpeaustriajc
```

## What it does

- **Finds where the knowledge lives.** It checks, in order:
  1. a pointer line in the project's `CLAUDE.md` (a URL or a vault path)
  2. a user-level map in `~/.claude/project-knowledge.json`
  3. detection of a GitHub wiki
  4. asking you once, and saving the answer
- **Keeps one shape on every backend.**
  - A Home page lists what each page answers.
  - A Decisions index runs newest first.
  - Each decision gets one `Decision NNN <Topic>` page that is never rewritten.
  - Research pages are dated and mark unconfirmed claims UNVERIFIED. Superseded text moves under a
    History heading.
- **Answers "what did we decide about X".** It follows each "Superseded by" and "Partly superseded
  by" link to the end of its chain.
- **Records, supersedes and partly supersedes decisions.** Only the old page's Status line changes.
- **Treats dates and reasons as evidence.** They come from git history, an issue or you. A missing
  reason is marked "not recorded" and asked about, never invented.
- **Writes for people.** Pages never mention Claude or agents. It shows you a first write to a
  shared space before publishing.

## Backends

| Backend | How it is reached | Status |
|---|---|---|
| GitHub wiki | `scripts/ghwiki.sh`, one managed clone per wiki, using `gh auth` | tested |
| Obsidian | vault files; sync detection before writing | tested |
| Notion | Notion MCP; the decision log is a database sorted by date | untested |
| Linear documents | Linear MCP; decisions linked to issues | untested |
| Confluence, Google Docs | Atlassian MCP, Drive MCP | untested |

## Evals

`skills/project-knowledge/evals/evals.json` holds five test prompts:

- reading a supersede chain
- recording a decision
- superseding one
- partly superseding one
- bootstrapping an empty Obsidian vault

Across two rounds against real wikis, the skill passed every check. Without it, runs passed 85%.
The runs without it put new rows at the bottom of the index, invented layouts and rules, and wrote
unlinked supersede notes.
