# Orchestrate

Read this in Orchestrate mode: the argument is a spec, more than one ticket, or contains the word `orchestrate`. One-ticket mode is in `SKILL.md`.

This session is the coordinator. It owns the program, never the code: it writes briefs, merges
finished branches and decides. Each ticket is built by its own session in its own worktree. A
subagent only scouts or reviews for about five minutes; it never builds a ticket.

Work with no tickets that splits into independent units, such as a migration across the
codebase, goes to the harness's batch command (Claude Code: `references/claude-code.md`), not
here. This mode is for tickets with blocked-by links that must close.

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

## The brief

Every session gets all of this. A field you cannot fill is an item that is not ready. The
command stays the first line (why: `references/claude-code.md`).

```
/implement <item link>
Base: <integration branch>. Reset your worktree onto it before you start.
PR: none. Push your branch and report; the coordinator merges.
Scope: the item's Out of Scope, plus the files other running sessions own: <list>.
Report: branch, head SHA, the Done When verdict table, Decided, Needs you, what you ran.
```

## State on disk

Keep `units.tsv` in the project's gitignored work folder: item, state, session, branch, head SHA,
verdict. The coordinator is its only writer. A new head SHA voids the verdict.

## Failure

- A session that stops with no report: read its branch and log, not its memory. Start one fresh
  session with the remaining work. If that one fails too, abandon the item and add a gate.
- Stop starting sessions when a shared cause makes new ones fail (a broken trunk, a wrong brief).
  Let running ones finish, fix the cause, then go on.
