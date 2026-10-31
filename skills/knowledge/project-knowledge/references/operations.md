# Operations that change the record

Read this before you supersede a decision, in full or in part, file research, or move rationale out of a repo. The other operations are in `SKILL.md`.

**Supersede a decision.**
1. Record the new decision as a new page, and have its Context say what changed since the old one.
2. On the old page, change **only** the Status line to `Superseded by [[Decision NNN …]]`.
3. In the index, update the old row's Status and add the new row at the top.

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
