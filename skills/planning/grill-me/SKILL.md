---
name: grill-me
description: Interview me relentlessly about a plan, idea or design until we share one understanding, in short rounds of ask-tool questions with a recommended answer each. Use when I say "grill me", "ask me", "stress-test this", or "plan and ask me".
---

Interview me until we reach a shared understanding. Map the idea as a **design tree**: every
decision branches into the decisions that hang off it. Work in **rounds**. The **frontier** is
every open decision whose prerequisites are settled. A question that depends on another one
still open this round waits for a later round.

## Facts are your job, decisions are mine

- Before round 1, and whenever a question needs a fact, dispatch read-only subagents to look
  it up: code, specs, mockups, the tracker, docs, earlier transcripts, the live app in a
  browser. Asking me something you could have looked up is the
  fastest way to annoy me. Ask only the questions downstream of a running lookup later; ask
  the rest now.
- If a spec, a design mockup, an existing pattern in a sibling product or a well-known
  convention (Auth0/Clerk-style flows, for example) already answers it, follow it and list it
  under **Assumed**. Don't ask it.
- A question with one obvious answer is not a question. "Should we show the missing price?"
  when it's plainly a bug goes under Assumed as "fix it". I can veto anything listed there.

## Never make me repeat myself

Open each round with a short ledger in chat, before the form:

```
**Settled:** postgres · API v2 only (v1 is gone) · mobile out of scope
**Assumed (veto any):** auth follows the partner's spec · fix missing price, it's a bug
**Open after this round:** 6
```

Every constraint I've stated goes into Settled and stays there. Never re-ask or quietly
contradict a Settled item. If new evidence conflicts with one, say so in one line and ask
about that conflict only.

## How to ask

- Use the `AskUserQuestion` tool, not a numbered list in chat. One call per round, with up to
  4 questions: pick the frontier questions that unblock the most. The rest wait.
- Put the recommended option first, marked "(Recommended)". Each option gets a one-line
  consequence: what it costs, what it touches, what it locks in.
- Every question carries a concrete scenario: a specific person, input or situation, and what
  each option does to it. For example: "A visitor types 'home security' and gets no results.
  A shows…, B shows…".
- Use plain words: no section numbers, internal IDs, letter codes or unexplained jargon.
  Define any term I might not know in half a line.
- For a layout, look or feel question, attach an ASCII `preview` per option, or offer
  "show me a mockup first" as an option. I decide visual things by seeing them.
- No preamble. Keep any justification to the option descriptions.

## Reading my answers

- **A note or "Other"** usually reframes the question or adds a requirement. Fold it into the
  tree, recompute the frontier, and don't re-ask the original as-is.
- **A counter-question**, such as "what's base_url again?", means I lacked context. Answer it
  in 1-2 lines, then put the question to me again next round.
- **"up to you" or "not sure"**: take your recommendation and log it under Assumed.
  **"you research it"**: dispatch a subagent and treat the result as a fact.
- **A skipped or partial answer** leaves that question open. **"handle Q1 first"** means
  reorder the rounds.
- **A dismissed or rejected form** means stop. Read what I type next and follow it. Never
  re-send the same form.
- **Bulk replies** like "yes to all", "1 yes, 2 the second one" settle everything they name.

## Keep it lean

- Scope is mine. Bias every recommendation toward the smallest version that ships, and toward
  lower running cost. When a branch is gold-plating, such as extra security on a sandbox or a
  second system to keep in sync, recommend cutting it rather than exploring it.
- Flag scope drift in one line: "This adds X; out of scope?".
- When a decision touches other people (PO, QA, an external team), word options the way they
  would read them: neutral, no blame, nothing that implies work is theirs unless I said so.

## Ending

Grilling writes nothing: no code, no tracker or doc writes, no pushes. The session is done
when the frontier is empty. Then post the final ledger as one compact list of every decision
with its one-line reason, and ask whether we have a shared understanding. On yes, offer the
next step in one line, for example a spec in the tracker via `work-planning`, or
decisions recorded via `project-knowledge`. Do nothing until I pick one.
