# Notion adapter

Use the Notion MCP server. Its tool names vary by version; look for search, fetch/retrieve, create
pages, and update page (or append blocks). If the only Notion tools listed are `authenticate` and
`complete_authentication`, ask the user to connect Notion first. Nothing else will work until they
do.

## Layout

- **A root page** plays the role of Home: one paragraph, then a table or list of child pages with
  what each answers.
- **The decision log is a database** under the root, named `Decisions`, with these properties:
  - `Name` (title), the full "Decision NNN: <Topic>"
  - `Number`
  - `Status`: a select with Proposed, Accepted, Partly superseded and Superseded
  - `Superseded part`: text naming what a partial supersede replaced
  - `Date`
  - `Issue`, a URL
  - `Superseded by`, a relation to the same database

  Its default view sorts by `Date` descending, which gives "newest first" for free. Each row's page
  body holds Context, Decision and Consequences as headings.
- **Research pages** are ordinary child pages of the root.

If the team already has a decisions database with other property names, map onto theirs rather
than creating a second one.

## Operations

- **Find.** Search for the root page or database named in the pointer, and fetch it. A pointer
  URL's trailing 32-character hex string is the page or database id.
- **Read.** Query the database, filtering on the topic, then fetch each matching page's content.
  Follow `Superseded by` relations to the end of the chain.
- **Record.** Take the highest `Number` plus one, then create a page in the database with the
  properties and body filled.
- **Supersede.** Create the new row. On the old row, set `Status` to Superseded (or Partly superseded, filling `Superseded part`) and fill the
  `Superseded by` relation. Leave its body untouched.
- **Link.** Use a page mention, not a pasted URL, so a rename does not break it.

Notion saves as you write, so there is no separate commit step. That also means a write is
immediately visible to the whole workspace. That is why SKILL.md §5 asks for the user's review
before the first write.
