# Obsidian adapter

An Obsidian vault is a folder of Markdown files, so the file tools are the adapter. The pointer
names a folder inside the vault, for example `obsidian: ~/Vaults/Work/Projects/renav`.

## Layout

- `Home.md`, `Decisions.md` and one `Decision NNN <Topic>.md` per decision, plus research pages,
  all in that folder. Obsidian allows spaces in file names, and `[[Decision 001 Topic]]` resolves
  to them.
- Put the decision metadata in frontmatter as well as the Status line. Dataview and Bases can then
  build the newest-first index:

```yaml
---
type: decision
number: 7
status: accepted        # proposed | accepted | partly-superseded | superseded
date: 2026-09-18
superseded_by: "[[Decision 009 …]]"
issue: https://github.com/o/r/issues/27
---
```

Keep the hand-written index table in `Decisions.md` anyway. It renders on GitHub, in a plain
editor and on the web, where no Dataview runs.

## Saving

- If the vault is a git repo (Obsidian Git), commit after each change with a descriptive message,
  and do not push unless the user syncs that way.
- If it syncs, saving the file is publishing, so show the user first. Treat a vault as synced when
  any of these hold: its path is under `~/Library/Mobile Documents/` (iCloud) or a Dropbox, Google
  Drive or OneDrive folder; `.obsidian/core-plugins.json` enables `sync`; or `.obsidian/plugins/`
  holds a sync or git plugin. If you can't tell, ask. Don't assume the vault is private.

An Obsidian MCP server, when one is connected, offers the same operations over the vault. Use it
if the vault is not on this machine.
