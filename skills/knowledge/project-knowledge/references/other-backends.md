# Other backends

The conventions in SKILL.md do not change. Map the four operations — find, read, record,
supersede — onto whatever the backend's MCP server or CLI offers.

## Confluence

Use the Atlassian MCP (or `twg confluence` where installed). A space or parent page is Home; its
child pages are the research pages; a `Decisions` child page holds the index table, and each
decision is a child page of it titled `Decision NNN: <Topic>`. Confluence keeps page history, so a
superseded page still carries only a Status change — history is not a licence to rewrite it.
Confluence page properties (the "Page Properties" macro) can hold Status and Date for a report
view; keep the hand-written table too.

## Google Docs / Drive

Use the Drive MCP. A folder is Home; `Decisions` is one Google Doc holding the index table; each
decision is its own Doc in a `Decisions` subfolder. Drive has no wiki links, so link with the Doc
URL.

## Anything else

Before writing, tell the user which tool you will use for each operation and how a superseded
decision will be marked, and get a yes. Then record the mapping in the user-level map
(`~/.claude/project-knowledge.json`, a `"notes"` field on that entry) so the next session does not
re-derive it.
