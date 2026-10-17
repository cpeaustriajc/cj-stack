---
name: grill
description: >
  This skill should be used when the user says "grill me", "ask me questions
  first", "stress-test this", "poke holes in this" or "plan and ask me" about a change, design,
  feature or plan. It sizes the work, then interviews in short rounds of questions with a
  recommended answer each until no decision is open. A whole product idea, or whether something is
  worth building, goes to vision instead.
---

## Size it first

Look the work up before asking anything, then sort it:

- **Trivial**: 1-2 files, one obvious approach, done is self-evident (a typo, a copy change, a
  plainly broken guard). Say so in one line, with your plan, and ask only "go?". No rounds.
- **Small**: one real decision. Ask it as a single question, then stop.
- **Grill**: 3+ files, several viable approaches, unclear scope, new architecture, or something
  other people will see. Run the rounds below.

Say which tier you picked and why in one line. I can bump it up or down.

## Grilling

Interview me until we reach a shared understanding. Map the idea as a **design tree**: every
decision branches into the decisions that hang off it. Work in **rounds**. The **frontier** is
every open decision whose prerequisites are settled. A question that depends on another one
still open this round waits for a later round.

## Facts are your job, decisions are mine

- Before round 1, and whenever a question needs a fact, look it up: yourself for a known file
  or one command, read-only subagents for broad searches. Look in code, specs, mockups, the
  tracker, docs, earlier transcripts and the live app in a browser. Asking me something you
  could have looked up is the fastest way to annoy me. Hold only the questions downstream of a
  running lookup; ask the rest now.
- A fact that a recommended option depends on gets a probe before the round that asks it: a
  small script in the ignored work folder (not a write in the Ending sense), the vendor's
  code, the PR state. Never offer "research first" as an option. Never end with an "I assume"
  item that a decision rests on. For example, when a plan rests on "the client reuses its
  connections", a short script answers that before the round, not after the grill.
- If a spec, a design mockup, an existing pattern in a sibling product or a well-known
  convention (Auth0/Clerk-style flows, for example) already answers it, follow it and list it
  under **Assumed**. Don't ask it.
- A question with one obvious answer is not a question. "Should we show the missing price?"
  when it's plainly a bug goes under Assumed as "fix it". I can veto anything listed there.

## Never make me repeat myself

When the work sits under a product or a spec, start the ledger with what that level already
settled and size only the questions left: under a confirmed product, a project is usually one
round or none.

Open each round with a short ledger in chat, before the form:

```
**Settled:** postgres · API v2 only (v1 is gone) · mobile out of scope
**Assumed (veto any):** auth follows the partner's spec · fix missing price, it's a bug
**Out of scope (veto any):** SSO for guests: no guest accounts exist (checked the users table)
**Open after this round:** 6
```

Every constraint I've stated goes into Settled and stays there. Never re-ask or quietly
contradict a Settled item. If new evidence conflicts with one, say so in one line and ask
about that conflict only.

## How to ask

- Use the ask tool (a form with options), not a numbered list in chat. One call per round,
  with up to 4 questions: pick the frontier questions that unblock the most. The rest wait.
  `references/<tool>.md` names the tool.
- Put the recommended option first, marked "(Recommended)". Each option gets a one-line
  consequence: what it costs, what it touches, what it locks in.
- Every question carries a concrete scenario: a specific person, input or situation, and what
  each option does to it. For example: "A visitor types 'home security' and gets no results.
  A shows…, B shows…".
- Use plain words: no section numbers, internal IDs, letter codes or unexplained jargon.
  Define any term I might not know in half a line.
- For a layout, look or feel question, attach an ASCII sketch per option, or offer
  "show me a mockup first" as an option. I decide visual things by seeing them.
- When a question or the final ledger is about a flow, a state change or a structure (a
  pipeline, a state machine, a module layout), show it as a diagram, not only as text.
  `references/<tool>.md` says how.
- Keep any justification to the option descriptions.

## Reading my answers

- **A note or "Other"** usually reframes the question or adds a requirement. Fold it into the
  tree, recompute the frontier, and don't re-ask the original as-is.
- **A counter-question**, such as "what's base_url again?", means I lacked context. Answer it
  in 1-2 lines, then put the question to me again next round.
- **"up to you" or "not sure"**: take your recommendation and log it under Assumed.
  **"you research it"**: look it up as under Facts and treat the result as a fact.
- **A skipped or partial answer** leaves that question open. **"handle Q1 first"** means
  reorder the rounds.
- **A dismissed or rejected form** means stop. Read what I type next and follow it. Never
  re-send the same form.
- **Bulk replies** like "yes to all", "1 yes, 2 the second one" settle everything they name.

## Done is always on the tree

Round 1 always settles what "done" looks like as something observable: who does what, and what
they see. For example: "A logged-out visitor clicks Buy and lands on register with the domain
still in the cart". Recommend one from what you looked up. Don't ask "what are the success
criteria?".

## Keep it lean

- Scope is mine. Bias every recommendation toward the smallest version that ships, and toward
  lower running cost. When a branch is gold-plating, such as extra security on a sandbox or a
  second system to keep in sync, recommend cutting it rather than exploring it.
- Flag scope drift in one line: "This adds X; out of scope?".
- Each item you cut goes under Out of scope, with a reason you checked. A part of the source I
  named (a repo to port, a list I pasted) is a question, not a cut.
- When a decision touches other people (PO, QA, an external team), word options the way they
  would read them: neutral, no blame, nothing that implies work is theirs unless I said so.

## Ending

Grilling writes nothing: no code, no tracker or doc writes, no pushes. The session is done
when the frontier is empty. Then post the final ledger as one compact list of every decision
with its one-line reason, and ask whether we have a shared understanding. On yes, offer the
next step in one line: a project to `shape`, a confirmed spec to `tickets`, or decisions
recorded via `project-knowledge`. Do nothing until I pick one.
