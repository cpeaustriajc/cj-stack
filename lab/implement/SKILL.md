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

In Orchestrate mode, read `references/orchestrate.md` first and follow it. This session is the
coordinator: it writes briefs, merges finished branches and decides. Each ticket is built by its
own session in its own worktree.
