---
name: implement
description: >
  This skill should be used when the user types "/implement" with a ticket or a spec. It builds
  one ready ticket without supervision: it gets the ticket from the tracker, trusts its answers,
  builds it with the feature playbook, reviews after the commit and opens a PR that closes it.
  With a spec or "orchestrate", it coordinates one session per ready ticket.
disable-model-invocation: true
argument-hint: "<ticket | spec> [orchestrate]"
---

# Implement

Build work that is already decided. Arguments: `$ARGUMENTS`. The ticket holds the answers, so the
run never reopens the plan, and it ends with proof that I check later, not with a question.

Tracker commands: `../triage/references/github.md`, or the tracker's own MCP server or CLI. Tool
mechanics (sessions, worktrees, limits): `references/claude-code.md`.

Two modes. **One ticket** is the default. **Orchestrate** runs when the argument is a spec, more
than one ticket, or contains the word `orchestrate`.

## 1. Get the ticket

- Get the item from the tracker by its reference: a URL, `owner/repo#N` or a tracker key. Never
  match a bare number against a list in this conversation or in a file.
- Say its title and link in one line before anything else.
- If the reference can match two items (two trackers, an issue and a PR), stop and ask which.
- If there is no reference and the plan is only in this conversation, write its Done When lines as
  you understood them and wait for my go.

## 2. Gate

Build only when all of these hold. Otherwise stop and say which one failed.

- The item is `ready-for-agent` (or the team's name for it). Any other state goes to `triage`.
- It has Done When or Acceptance lines, each a check that passes or fails.
- Every item that blocks it is closed, or merged into the base branch of this run.

`ready-for-human`: build the part an agent can prove, and list the rest under Needs you.

Never build on the trunk. Branch from a fresh trunk, or from the integration branch in orchestrate
mode, unless the current branch is already for this item.

## 3. Trust the ticket

Do not run `grill` and do not propose a different approach. For a question the ticket does not
answer:

| The answer is | Do |
|---|---|
| Easy to undo | Follow the closest existing pattern. Add it to the PR's Decided list. |
| Costly to undo, or against the spec or a recorded decision | Stop. Post triage notes on the item, move it to `needs-info`, report. |

A Done When line that cannot be met as written is a costly question.

## 4. Build

Run the feature playbook (`playbooks`, `references/feature.md`) from its step 2: the ticket
settled step 1. A Bug item runs the bug playbook instead.

- Each Done When line is a check. A You see line is an end-to-end check in the running app.
- Commit per slice, never red. Save each check's command and evidence.
- Do not touch Out of Scope items. A side discovery goes in the report, not in this run.

## 5. Review after the commit

When the last slice is committed, run `interrogate` on `<base>...HEAD`. Its reviewers are fresh;
the builder does not grade its own work. Fix each Act on row in its own commit and rerun the
checks it touches. Put Consider rows in the PR.

## 6. Close out

A session that an orchestrate brief started pushes its branch and reports; it opens no PR.
Otherwise push and open the PR with `create-pr`. The body holds:

- The close word for the item (`Closes #N`), so the merge closes it. Never close it by hand.
- One row per Done When line: the line, the command, the evidence path, and VERIFIED, NOT
  VERIFIED or INCONCLUSIVE. INCONCLUSIVE is not a pass.
- **Decided:** each answer from step 3 that the ticket did not give.
- **Needs you:** each line only a person can check.

Report the PR link and the same three lists.

## Orchestrate

This session is the coordinator. It owns the program, never the code: it writes briefs, merges
finished branches and decides. Each ticket is built by its own session in its own worktree. A
subagent only scouts or reviews for about five minutes; it never builds a ticket.

1. **Frame.** Read the spec and its items. Build the graph from the blocked-by links. The
   frontier is every `ready-for-agent` item whose blockers are done. State the done predicate as
   a count: "6 of 6 items have a verified branch merged into the integration branch". List the
   items that are not ready as gates. If the frontier is one small item, run one-ticket mode here.
2. **Integration branch.** Branch it from a fresh trunk. Open a draft PR to the trunk after the
   first merge.
3. **Pilot.** Start one session on the riskiest frontier item. When it reports, fix the brief
   from what went wrong before you start more.
4. **Fan out.** Keep a rolling window of sessions, up to the cap in the adapter. Start a new one
   when one finishes; never wait for a whole batch.
5. **Drain.** A session's report is a claim, not proof. Read its verdict table and rerun one of its
   checks on its branch. A clean branch: merge it into the integration branch. A conflict or a
   failed check: back to a fresh session with the remaining work. Then recompute the frontier.
6. **Gates.** A session that stops on a costly question parks its item as `needs-info`. Collect
   gates and route the work around them. Bring them to me in one batch, not one at a time.
7. **Close.** Run `interrogate` on `<trunk>...<integration branch>`; one session fixes the Act on
   rows. Mark the PR ready, with a close word for every item. Report the count against the
   predicate, each item's branch and verdict, the open gates, and what was abandoned and why.

### The brief

Every session gets all of this. A field you cannot fill is an item that is not ready.

```
Run /implement <item link>.
Base: <integration branch>. Reset your worktree onto it before you start.
PR: none. Push your branch and report; the coordinator merges.
Scope: the item's Out of Scope, plus the files other running sessions own: <list>.
Report: branch, head SHA, the Done When verdict table, Decided, Needs you, what you ran.
Standing orders: <the numbered list, pasted word for word>
```

### State on disk

Keep `units.tsv` in the project's gitignored work folder: item, state, session, branch, head SHA,
verdict. The coordinator is its only writer. A new head SHA voids the verdict.

### Failure

- A session that stops with no report: read its branch and log, not its memory. Start one fresh
  session with the remaining work. If that one fails too, abandon the item and add a gate.
- Stop starting sessions when a shared cause makes new ones fail (a broken trunk, a wrong brief).
  Let running ones finish, fix the cause, then go on.
