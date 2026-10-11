# Top-down planning

The shared core of `vision`, `shape` and `tickets`. Each of them reads this file first.

| Skill | Level | Holds |
|---|---|---|
| `vision` | Product | Worth it, destination, features F1…Fn, not yet specified, out of scope |
| `shape` | Project | Spec with requirements R1…Rn, testing seams, milestones |
| `tickets` | Work item | One slice, citing the requirements it meets |

`triage` asks the open questions at the project level; `vision` grills the product itself.
Questions thin out going down, because each level inherits what the one above settled.

## Five rules

1. **Read the level above first.** A project starts from one feature of the product; a work item
   from the spec. With no product, offer `vision` for a minimal one; a one-off internal tool may
   stand alone if I say so.
2. **Every item cites its parent.** A project names its feature, every requirement serves the
   project's Done, every work item names its requirements. An item with no parent is scope nobody
   asked for.
3. **A level is built only from a confirmed parent.** A Draft product gets no projects beyond
   one-line placeholders; a Draft spec gets no build items. Building on an unconfirmed level means
   rework when it changes, and it usually changes after a demo.
4. **Changes flow down, questions flow up.** A changed feature returns its project's spec to
   Draft; a changed requirement flags every item that cites it. A lower level never edits a
   higher one: a requirement found wrong while building comes to me as a question.
5. **Status rolls up.** Items close milestones, milestones feed the project update, project
   health feeds the product update. Nobody retypes a level's progress by hand.

## Find the tracker

Stop at the first hit:

1. A pointer in the project's `CLAUDE.md` or `AGENTS.md`, for example `Tracker: Linear, team MP`,
   a Jira URL, or `GitHub issues`.
2. The connected tools: a Linear MCP server means Linear; an Atlassian MCP server or the `acli`
   CLI means Jira; a GitHub remote with `gh` signed in means GitHub.
3. Ask once, and offer to add the pointer line. For personal software, recommend a Markdown file
   in the repo over setting up a tracker.

Then read the matching adapter in this folder. It maps each level onto that tracker's objects
and names the tools that reach it.

| Tracker | Adapter |
|---|---|
| Linear | `linear.md` |
| Jira (with Confluence for documents) | `jira.md` |
| GitHub Issues and Projects | `github.md` |
| Asana, ClickUp, Notion, Trello, a Markdown file, anything else | `other-trackers.md` |

**The project's facts** override the defaults in these skills: who holds each role, the team's
templates, which areas are too risky to skip QA, where older specs live. Look for a tracker
section in `AGENTS.md` or `CLAUDE.md`, or a file it points to; ask only what the task needs. On a
solo project one person holds every role:

- **Product owner**: writes intent, priority and requirements, and accepts releases.
- **Approver**: confirms direction, often after a demo; usually the product owner.
- **Verifier**: marks work done. QA if the team has it, otherwise the product owner.
- **Engineering**: decomposition, work types, feasibility and the shape of the work.

Use the team's own templates in the tracker when it has them, read fresh each time; copied into
files they go stale. Don't invent owners, dates, measurements or dependencies: leave them blank
or list them as open questions.

## Write, then check the tree

Drafting, auditing or translating never authorises a write. Before any write, state the exact
item and change; afterwards, read it back and report what the tracker now holds. Show me the
first write to a shared tracker before making it: the whole team sees it at once, and many
trackers notify a channel on every save, so batch related changes into one write.

After writing, read the tree back from the tracker into the outline in `tree-outline.md`, save it
as a scratch JSON file, and run `python3 <shape>/scripts/check_tree.py <path to the JSON>`, where
`<shape>` is the parent of this file's folder. Use absolute paths: the session's working
directory is the project, not the skill. Fix every line it prints before handing back, or say
why one stays.
