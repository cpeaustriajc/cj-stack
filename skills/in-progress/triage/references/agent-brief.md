# Agent brief and triage notes

The brief is the contract. The issue body and its comments are only context. The item may wait
for weeks, so the brief must stay true when files move.

- Name behaviour, types, commands, routes and config keys. No file paths, no line numbers.
- Say what the system does when the work is done, not how to build it.
- Each acceptance item is a check one person or agent can run and see pass or fail.
- List what is out of scope, so the agent adds nothing next to it.

## Agent brief

```markdown
## Agent brief

**Category:** bug | enhancement
**Summary:** <one line>

**Now:** <what happens today; for a bug, the broken behaviour and the reproduce steps>

**After:** <what happens when the work is done, with edge cases and errors>

**Key interfaces:**
- `<type, command, route or config key>`: <what changes>

**Acceptance:**
- [ ] <a check with an input and the result you see>

**Out of scope:**
- <a near feature this item does not touch>
```

For a PR, **Now** describes the diff as it is, and **After** says what is left: gaps, failed
checks, review points.

## Needs a person

Add this section to the brief for `ready-for-human`:

```markdown
**Needs a person:**
- <Done-when item>: <why an agent cannot prove it, for example "needs the merge to main first">
```

## Triage notes (needs-info)

```markdown
## Triage notes

**Settled so far:**
- <fact or decision>

**We need from @<reporter>:**
- <one specific question, with the example that shows why it matters>
```
