# Other trackers

For Asana, ClickUp, Notion databases, Trello, Height, Shortcut, or a plain markdown file. Read the
tool's own MCP server or CLI to see what it can create, then map the levels onto what exists.

| Level | Look for | Fallback |
|---|---|---|
| Goal | A portfolio, goal, initiative or top-level folder | A pinned page the projects link to |
| Project | A project, list, board or epic | A parent item with child items |
| Spec, engineering document | A doc or page attached to the project | A page in the team's wiki, linked from the project |
| Phase | A milestone or section | A single-select "Phase" field, or a section per phase |
| Work item | Task, card or item | — |
| Work type | An item type or template | A label: `Task`, `Bug`, `Chore` |
| Dependency | A native "blocked by" | A line in the item's Context with a link |

- **Keep the method, bend the container.** The rules about statements, confirmation before
  splitting, one engineering document and fixed phases hold whatever the tool calls things.
- **A markdown file as the tracker** (`TODO.md`, `ROADMAP.md`): one heading per project, the spec
  linked rather than inlined, phases as subheadings, work items as checkboxes with the template's
  Outcome as the line and Done When nested beneath.
- **No checkbox rendering?** Use a plain numbered list for Done When and say so once.
- **If the tool can't create something** the method needs, say what's missing and hand the person
  the text to paste. Don't fake it through a comment or an unrelated object.
