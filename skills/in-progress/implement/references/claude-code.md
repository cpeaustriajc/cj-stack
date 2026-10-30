# Claude Code adapter

Mechanics checked against `claude --help` in October 2026; check again when a detail matters.

## One session per item

A session is a full Claude Code session, not a subagent. Start each one fresh, in its own
worktree, on Opus at medium effort.

- **Desktop app:** start a session with a fresh context and its own worktree, based on the
  integration branch. Its reports come back as notes; never poll them.
- **CLI:** `claude --bg -w <item-id> --model opus --effort medium "<brief>"`. `claude agents`
  lists the sessions; `claude logs <id>` reads one. `-w` does not take a base branch, so the
  brief tells the session to reset onto the integration branch.

Cap: three sessions at a time. More burns the weekly usage faster than drains can check the work.

## Work with no tickets

`/batch <instruction>` researches the code, splits the work into 5 to 30 independent units and
shows a plan. After approval it starts one background subagent per unit, each in its own
worktree; each one builds its unit, runs the tests and publishes its change. It reads no
tracker, keeps no blocked-by order and closes no ticket, so use it only when no unit blocks
another. Source: https://code.claude.com/docs/en/commands (`/batch`).

## Traps

- **Close words act only on the default branch.** On GitHub, `Closes #N` in a PR into the
  integration branch closes nothing. Put every item's close word in the integration PR to trunk.
- **The stash is shared by all worktrees.** A session never runs `git stash`; it makes a WIP
  commit instead.
- **Two sessions in one checkout** share the index and HEAD, and amend or commit onto each other.
  Every building session gets its own worktree.
