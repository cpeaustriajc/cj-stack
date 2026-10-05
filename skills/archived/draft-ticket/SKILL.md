---
name: draft-ticket
description: End-to-end workflow for drafting or revising a Jira ticket — draft locally, sweep test categories, gate through qa-ac-critic until clean, route engineering detail to GitHub. Use when asked to write, revise, or fix a ticket (a key, a URL, or "draft a story for X").
---

# /draft-ticket — the ticket-writing standard

This command runs the full drafting loop. The `jira-ticket` skill defines the
format; this skill defines the process around it.

## Steps

1. **Read the source in full.** The Jira ticket (via `twg jira workitem get` +
   `comment query`), the correction comment, or the verbal request. Restate the
   requirement in one sentence before drafting.

2. **Load `jira-ticket`** (always) and `github-issue` (when the source contains
   implementation detail that needs a home).

3. **Draft in the client's temporary artifact directory outside the repository** — never in `docs/`, never straight into
   Jira. One markdown file per ticket. CJ transcribes to Jira personally; ask
   before ANY Jira mutation.

4. **Category sweep.** Enumerate the original ticket's test categories and
   carry every one forward. An untestable category (JWT middleware wording,
   SLAs with no APM) gets TRANSLATED into browser-testable equivalents —
   request replay for authorization, DevTools recordings for performance —
   never dropped. Then check the draft against the standard set and add what
   the feature touches:
   - Functional (happy paths, toggles, persistence)
   - Validation (accept rule stated positively, boundaries at max/max±1,
     hostile input at every entry point)
   - Security (cross-account and no-session request replay, revoked session ×
     every mutating action, injection in every render sink incl. toasts)
   - Performance (browser-measured with a stated method and threshold — there
     is no APM or server logging)
   - Concurrency (two tabs one account, interrupted/repeated flows)
   - Responsive & browsers (375px/768px and an additional supported browser
     when relevant; inspect the suite's current browser setup)
   - Accessibility (named keys and outcomes, announcements, reduced motion)
   - Regression touch list (RCRCRC: header, affected tools, cart, shortlists,
     and signed-out behavior; inspect current routes)
   Deliberately absent categories (load testing, localization) get one line
   saying why.

5. **Check locked decisions.** Grep `.agents/references/locked-decisions.md` for
   every mechanism the draft touches. A draft that reverses a locked decision
   is not wrong per se — but the reversal is a named blocker needing a dated
   PO/CJ entry, never a silent contradiction.

6. **Gate through `qa-ac-critic`.** Use native independent delegation with
   `.agents/skills/qa-ac-critic/SKILL.md` on the whole draft. If unavailable
   or prohibited, mark the draft "independent review pending"; inline review
   does not satisfy the gate.
   Apply every finding or decline it explicitly in the reply to CJ — never
   leave findings half-applied. Re-run after major edits (new sections, PO
   decisions folded in). The draft is done when a pass returns only items that
   need a PO answer.

7. **Route content.** Product language in the ticket draft; implementation
   detail (paths, symbols, fields, budgets, traps found in code) into the
   GitHub issue titled with the Jira key (`github-issue` skill), then delete
   it from the draft so the file is Jira-transcribable as-is.

8. **Deliver.** Link or attach the file using the current client's capability.
   The file contains only the Jira description. Put title, labels, blocker
   links, story-form explanation, critique summary and PO questions in chat
   (or a separately requested comment draft).

## Hard rules

- Every AC singular, active-voice, with an observable pass/fail. No "quickly",
  "immediately", "user-friendly", "any action".
- State accept rules positively ("accepted iff X"), not as failure examples.
- Universal negatives ("never grants access") become named executable attempts.
- "Every page" becomes an enumerated route list.
- Fixture rule: never invent domain data — setup steps find live rows ("first
  row that shows a price"), state the live-data-block fallback, and seeded
  accounts use real feed rows only.
- Anything QA cannot verify without a developer (expiry clocks, backdated
  records) says so in the step and is blocked, not passed, without that help.
- Decisions the ticket cannot make (retention, caps, cart actions, decision
  reversals) are open questions in chat, not invented answers in the story body.
- Ticket-on-ticket gates are proposed Jira "is blocked by" links in chat,
  not description prose. Ask before any external issue mutation.
