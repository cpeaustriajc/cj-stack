# Linear adapter

Use the Linear MCP server. Its document tools vary by version: look for tools that list, get,
create and update documents, and for search. If the only Linear tools listed are `authenticate`
and `complete_authentication`, ask the user to connect Linear first. Some versions can read
documents but not write them. If there is no create or update tool, say so, and hand the user the
page text to paste. Do not fake a write through an issue or a comment.

## Layout

Linear documents belong to a **project** or an **initiative**. They have no folders and no
databases. The pointer names the project, for example `linear: project "Renav"` or a
`linear.app/<team>/project/…` URL. Inside that project:

- **`Home`**: one paragraph, then the `Page | What it answers` table.
- **`Decisions`**: the index table, newest first. Linear has no sorted views for documents, so the
  table is the only index, and each new row goes at the top by hand.
- **`Decision NNN: <Topic>`**: one document per decision, from the template.
- **Research documents**: one topic each.

Pick the scope by who decides. Use an **initiative** for decisions that span several projects, and
the **project** otherwise. Keep them in one place, so nobody has to search two.

## Linear's strength: issues are first-class

- The `Issue` field uses a Linear issue identifier (`ENG-123`). Linear renders it as a live link,
  and the issue shows the reference back.
- When a decision comes out of an issue, also comment on that issue with the decision's title.
  Anyone reading the issue can then find the record.

## Operations

- **Find.** List the documents in the project and match their titles.
- **Read.** Get each matching document in full, and follow each "Superseded by" to the end of the
  chain.
- **Record.** Take the highest number in `Decisions` plus one, create the document, then update
  `Decisions` by adding the row at the top.
- **Supersede.** Create the new document. In the old document, change only its Status line. Update
  the old row in `Decisions`.

Linear saves on write, and the whole team sees it at once. So the first write to a team's
project follows SKILL.md §5: show the user the text first.
