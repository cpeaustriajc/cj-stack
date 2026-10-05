---
name: jira-ticket
description: Writing or editing Jira tickets, stories, bugs, epics, or acceptance criteria for this project. Use before drafting any Jira issue title or description.
---

# Jira tickets — PM-readable

Write every ticket in user-visible behavior terms. Stories follow this format
(3 Cs + INVEST, with three story forms):

1. **Story** — one prose sentence, never bullets or line breaks. **Pick the
   form by the decision table below, and name which form you used.** Do not
   default to Connextra and do not treat "this is an internal change" as
   licence to drop the template.

   | Does a user observe a difference? | Is the triggering situation the point? | Form |
   | --- | --- | --- |
   | Yes | No — the role is the point | **User story** (Connextra) |
   | Yes | Yes, or the role is generic/unknown | **Job story** |
   | No — nothing user-visible changes | — | **Enabler story** |

   - **User story** — "As a `<named role>`, I want `<capability>`, so that
     `<benefit>`." Connextra, 2001; popularised by Mike Cohn. Name a real role
     (domain investor, buyer, QA tester, team member). "As a user" means the
     role is unknown — that is a signal to use a job story, not to write
     "user".
   - **Job story** — "When `<situation>`, I want `<motivation>`, so I can
     `<outcome>`." Intercom / Alan Klement, 2013. Use it when the situation
     carries the meaning and a persona would be invented filler. **A rewritten
     engine, provider swap or migration whose OUTPUT the user sees is a job
     story, not an enabler** — the implementation is internal, the observable
     result is not.
   - **Enabler story** — state the outcome plainly, no persona. Reserved for
     work with genuinely no user-observable change. SAFe's four enabler kinds
     are the test: **exploration** (research, prototypes, evaluating
     alternatives), **architecture** (build the runway for later delivery),
     **infrastructure** (build/test/deploy/runtime environments), and
     **compliance** (V&V, audits, approvals, policy automation). If the work
     fits none of those four, it is not an enabler — find the user and write a
     user or job story.
   - Keep the so-that / so-I-can clause unless it genuinely adds nothing.
   - The acceptance criteria still say what the reader SEES, whichever form the
     story sentence takes. "The buyer sees…" in an AC names who observes the
     behaviour; it is not a persona claim and does not make the story a
     Connextra one.
2. **Problem / User impact** — optional context paragraphs when the story
   sentence alone doesn't carry why the work matters. Short.
3. **Blocker** — only if something gates the work. When the gate is another
   Jira ticket, express it with Jira's native linked work items ("is blocked
   by" → the gating key), not description prose. In a local
   draft, report the proposed blocker link in chat, outside the description
   file; CJ transcribes it as the link. Prose Blocker
   sections are only for gates Jira cannot link (an external team, an
   unwritten decision).
4. **Acceptance criteria** — behavior-phrased, testable checks. Plain
   declarative bullets by default (the PO's chosen style — preserve the PO's
   wording verbatim when the criteria come from them). Given/When/Then is
   allowed only where a flow's boundaries are unclear without it.
   Describe behavior, never implementation: "a signed-in buyer", not "the
   session cookie validates".
5. **Functional Testing Requirements** — this team's extension of the
   standard (manual-testable, complemented by Playwright): grouped under short sub-headings,
   each item a **bold-named scenario** plus a "Verify that…" sentence with
   concrete example inputs (`google.com`, `Test-Domain.com`).

   **Category sweep — do this before calling the section done.** Enumerate the
   categories the ticket already has and carry EVERY one forward. An untestable
   category is **translated**, never dropped: authorization with no attackable
   endpoint becomes DevTools request replay; an SLA with no APM becomes a
   stopwatch/DevTools recording with a stated method and threshold. Then check
   the draft against this standard set and add what the feature touches:

   - **Functional** — happy paths, toggles, persistence.
   - **Validation** — the accept rule stated POSITIVELY, boundaries at
     max/max±1, hostile input at every entry point.
   - **Security** — cross-account and no-session request replay, revoked
     session × every mutating action, injection in every render sink
     (including toasts).
   - **Performance** — browser-measured, with the method and threshold written
     down. There is no APM and no server-side logging in this app.
   - **Concurrency** — two tabs one account, interrupted and repeated flows.
   - **Responsive & browsers** — 375px and 768px; run key flows once in
     an additional supported browser when relevant. Inspect `e2e/README.md`
     for the current suite setup, not retired browser-extension constraints.
   - **Accessibility** — named keys and their outcomes, announcements, reduced
     motion.
   - **Regression touch list (RCRCRC)** — recent, core, risky, configuration,
     repaired, chronic. Check header, affected tools, cart, shortlists,
     and signed-out behavior against current code.

   A category the ticket deliberately omits gets **one line saying why** —
   silence reads as an oversight. Load testing and localization are the usual
   two.

Before a story is estimable it must pass INVEST: Independent, Negotiable,
Valuable, Estimable, Small, Testable. A story that fails Small or Independent
gets flagged for decomposition, not padded.

The written story is a promise of a conversation (3 Cs: Card, Conversation,
Confirmation) — do not gold-plate template compliance; flag open scope
questions for the PO rather than answering them in the draft.

## AC critique gate — mandatory before a draft is final

Once the acceptance criteria and Functional Testing Requirements are drafted,
dispatch the `qa-ac-critic` agent on the full draft BEFORE presenting it as
done. The agent judges each criterion against standardized gates (ISO 29148,
INCOSE, ISTQB) and proposes the scenarios the draft misses — it must never be
skipped because the draft "looks complete"; the gate exists precisely to not
trust the drafter's own view. Then:

- Apply the per-criterion fixes (ambiguity, boundaries, testability) directly.
- Scenarios the critic marks `[proposed — not in ticket]` are scope: add the
  clearly-in-scope ones to Functional Testing Requirements, and surface the
  rest to CJ as open questions — never silently widen the PO's criteria.
- PO-authored criteria stay verbatim; attach the critique as notes for the
  conversation instead of rewriting their wording.

## Where content lives — Jira vs GitHub

Jira holds product content only: the story sentence, problem/user impact,
behaviour-phrased acceptance criteria, and Functional Testing Requirements.
Implementation detail — file paths, code symbols, API fields, probe data,
latency budgets, architecture choices — lives in GitHub Issues, never in a
Jira description: the Jira audience (PO and QA) does not need to read GitHub,
and the issue title carrying the Jira key is the only cross-reference (no
links in either direction). When a Jira draft contains something like
`afternic_price` or `tld-lens.tsx`, either rewrite that sentence as what the
user sees on screen or move it to the GitHub issue. The issue structure,
naming, milestones, sub-issue hierarchy and workflow live in the
`github-issue` skill — load it when creating or updating those issues.

## Labels — themes and cross-cutting status only

Labels are for grouping Jira can't express with the epic link or (future, admin-created) Components — never for ownership routing. Closed vocabulary, exact kebab-case strings:

**Theme (one per story, matching its epic):**
- `v1-fast-finding` — Search & Discovery (MP-17)
- `go-live` — Production Go-Live
- `sso` — Auto-Login / shared-session handoff
- `data-contracts` — data model & external contracts

**Cross-cutting status (add when applicable, spans epics):**
- `blocked-cross-team` — gated on the checkout or SSO team
- `on-hold` — deliberately not scheduled (e.g. AI Finder, per CEO)

Keep draft files description-only in the client's temporary artifact directory outside the repository. Report title, labels, story form, blocker links, and open questions in chat, not the story body. Drafting does not authorize a Jira mutation. If tools or independent delegation are unavailable, disclose that and leave the relevant gate pending. Filter e.g. `project = MP AND labels = blocked-cross-team` for cross-team gates.

## Epics — light epic format

At single-team scale an epic is just a large story (Cohn), kept deliberately
coarse and refined just-in-time (Pichler); the parent stays open in Jira after
its stories split out (Patton). Two structured fields are borrowed from SAFe's
Epic Hypothesis Statement because outcome-oriented framing has independent
empirical backing (RIGHT model, JSS 2017; FACE, EMSE 2023): Business Outcome
and Leading Indicator. SAFe's full 7-field template is a portfolio *funding*
artifact (business case, MVP, cost estimate) — do not apply it to a one-team
backlog item.

Fields, in order — only the first three are mandatory at creation; refine the
rest just-in-time rather than gold-plating up front:

1. **Title** — verb + user-visible capability.
2. **Goal** — one prose sentence: the outcome, not the build. Never a list.
3. **Business outcome** — the measurable benefit if the bet is right.
4. **Leading indicator** — the earliest observable signal that the bet is
   right or wrong; state the falsifier ("if X instead, recalibrate/stop").
5. **Scope boundary** — In / Out bullets; name what is deliberately excluded.
6. **Child stories** — the split, each in Connextra form, linked as child
   work items. The epic is not hollowed out when they split.
7. **Done when** — every child shipped, QA executed, and the leading
   indicator readable.

Technical detail (fields, probe numbers, latency budgets, guard rails) does
not belong in the epic statement — it is just-in-time refinement material for
the child stories. It follows the "Where content lives" rule above: a GitHub
issue named after the epic's Jira key (see the `github-issue` skill).

Sizing rule: if a proposed child "story" spans multiple
architectural concerns (queue + external integration + caching + streaming,
or input UI + state + virtualized rendering + export), it is itself an epic —
flag it and propose decomposition into INVEST-sized stories rather than
estimating it as one.

### Legacy: the PO's MP-10 structure

Older epics (canonical example: MP-10 "Unified Marketplace & Broker Offer
Workflow") use the PO's heavier structure: Capability summary, Scope
Assessment ending in a bold **Verdict:** line, Functional Boundaries
(Backend/Frontend Concern), Scalability & Technical Requirements with
concrete figures, Recommended Story Breakdown ("Story 1 (Backend): …"),
Definition of Done checklist, Additional Recommended Stories with one-line
**Goal:** items, and a Blockers table (Blocker Area | Potential Issue |
Engineering Mitigation Strategy). When *editing* one of those, mirror its
existing sections instead of converting it; write plain figures, not the
LaTeX-style `$1.5\text{s}$` notation MP-10's source contains. New epics use
the light format above.
