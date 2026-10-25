---
name: cleanup
description: >
  This skill should be used when the user says "cleanup", "clean up after yourself", "tear down
  the dev server", "archive this session" or "clean up stale branches and worktrees". It removes
  what a session left behind (servers, containers, branches, stashes, evidence) once each item is
  proven safe, names what it keeps, then archives if asked. "/cleanup repo" sweeps the whole
  repo. Tidying code is simplify, not this skill.
---

# Cleanup

When I say "clean up", that is the go. Never ask "remove it too?" for an item this skill proves
safe; ask only in the repo sweep. Tool mechanics (archive, worktrees, transcripts):
`references/<tool>.md`.

## Session cleanup (default)

1. **Inventory** what this session made, from this conversation: background processes and their
   PIDs, dev servers, Docker containers and volumes, branches (local and remote), stashes, edits
   to tool config such as `.claude/launch.json`, evidence (videos, screenshots, `test-results/`,
   `artifacts/`, `.claude/work/<topic>/`) and temp files. A thing you cannot tie to this session
   goes under Keep, never Remove: another session may own it.
2. **Prove** each item safe with a live check, never from memory:
   - process or server: `kill -0 <pid>` is alive and `lsof -a -p <pid> -d cwd` is this checkout;
   - branch: its PR is MERGED or CLOSED (`gh pr view <branch> --json state,headRefOid`) and the
     branch tip equals `headRefOid`; with no PR, `git cherry origin/main <branch>` prints no `+`;
   - remote branch: the same, and the PR author is me;
   - stash: its message is a tag this session wrote;
   - evidence: the PR it proves is merged, or the file is already attached to the PR or ticket;
   - config edit: `git diff` shows only this session's change.
3. **Remove** the proven items, in this order, so one step does not block the next:
   1. Stop processes by their PID: `kill <pid>`, never by name or port.
   2. `docker rm -f <name>` and `docker volume rm <name>` for containers this session named.
   3. `git stash drop <sha>` for each own stash, found again by its tag.
   4. Restore config edits by path: `git restore -- <file>`.
   5. Delete the evidence paths.
   6. Leave the branch: `git switch --detach origin/main`.
   7. Delete the local branch with `git branch -d <branch>` while its upstream remote branch
      still exists: git allows `-d` for a branch merged into its upstream, so a squash merge
      passes.
   8. Then `git push origin --delete <branch>`. If GitHub already deleted the remote branch and
      `-d` refuses, put `git branch -D <branch>` under "Run yourself"; never force it.
4. **Keep** each item that failed a check, with the reason in one line: unpushed commits (count
   them), uncommitted edits, an open PR, not this session's.
5. **Report** in the chat, before archiving: Removed (one line each, with the size freed for
   evidence), Kept (with reason), Run yourself (exact commands). No "Removed" line without the
   command output that proves it.
6. **Archive** only if I said "archive" or "close": `references/<tool>.md`. It is the last call,
   because it ends the session. With a Kept item that holds unpushed work, do not archive: say so.

## Repo sweep (`/cleanup repo`)

For branches and worktrees from many sessions.

1. List every worktree (`git worktree list --porcelain`), local branch and remote branch, and
   the PRs (`gh pr list --state all --limit 500 --json number,state,headRefName,headRefOid,author`).
   Use `gh`, not `git branch --merged`: it misses squash merges.
2. Classify each branch and worktree with the checks of step 2 above, in one table: Remove,
   Keep (reason) or Ask (no PR and unique commits: say what the commits change, from
   `git log --oneline origin/main..<branch>`).
3. Never touch a worktree a live session uses (`references/<tool>.md`), a dirty worktree, or a
   remote branch whose PR author is someone else.
4. Before any delete, save every branch tip to remove:
   `git bundle create .claude/work/cleanup/<date>.bundle <branches>` and a `restore.sh` with one
   `git branch <name> <sha>` line per branch.
5. Show the table and ask once, with the ask tool: remove all, remove all but Ask rows, or pick.
   Then run steps 3.6 to 3.8 of Session cleanup for each approved branch, and
   `git worktree remove <path>` (never `--force`) for each approved worktree.
6. Report the counts, the bundle path and the Kept rows.
