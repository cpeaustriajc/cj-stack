# Linear adapter

Use the Linear MCP server. Its document tools vary by version: look for tools that list, get,
create and update documents, and for search. If the only Linear tools listed are `authenticate`
and `complete_authentication`, ask the user to connect Linear first. Some versions can read
documents but not write them. If there is no create or update tool, say so, and hand the user the
page text to paste. Do not fake a write through an issue or a comment.

## Layout: no numbers, no index

Linear documents belong to a **project** or an **initiative**, or to the team. They have no
folders, no databases and no sorted views, but they do have search. A hand-kept index can't be
sorted or filtered, and teams stop maintaining it, so on Linear search replaces the index and the
number:

- **`Decision: <Topic>`**: one document per decision, the topic a plain statement ("Decision: Make
  Offer hidden"). No number. Keep the `Decision:` prefix: a title search for it lists every
  decision.
- **First body line, the tag line:** `**Status:** Accepted · **Kind:** Product · **Decided by:**
  <name or role> · **Date:** YYYY-MM-DD`. A search for "Decided by" finds every decision, including
  ones whose title was edited. `Kind` is Architecture, Product, Process or Business. Below it come
  the template's Context, Decision and Consequences sections.
- **No `Decisions` index document.** If the team still keeps one, follow the team, and add the row.
- **`Home`** stays: one paragraph, then the `Page | What it answers` table, listing research pages.
  Decisions don't need rows there, because search finds them.
- **Research documents**: one topic each, as in SKILL.md.

If the team has a `Decision` document template in Linear, start from it: its title and sections
win over the shape above. The project's facts can also name a different title format; follow them.

**Where to file it.** Put a decision that changes one feature in that feature's project, beside the
document it amends. Put one that every project relies on in the team's documents, or on an
initiative when it spans that initiative's projects only.

## Linear's strength: issues are first-class

- The `Issue` field uses a Linear issue identifier (`ENG-123`). Linear renders it as a live link,
  and the issue shows the reference back.
- When a decision comes out of an issue, also comment on that issue with the decision's title.
  Anyone reading the issue can then find the record.

## Operations

- **Find.** Search documents for the topic, for `Decision:` and for "Decided by", across the team
  and the projects it might belong to.
- **Read.** Get each matching document in full, and follow each "Superseded by" to the end of the
  chain.
- **Record.** Create the document from the template, with the tag line first. There is no number
  to take and no index to update.
- **Supersede.** Create the new document. In the old one, change only the tag line's Status to
  `Superseded by <link>` (or `Partly superseded by <link>: <the part>`).
- **A stale detail, not a stale decision.** When only a detail is out of date and the decision
  itself still holds, strike the detail in place with `~~…~~` and add a document comment saying
  what replaced it and where that is recorded.

Linear saves on write, and the whole team sees it at once. So the first write to a team's project
follows SKILL.md section 5: show the user the text first.
