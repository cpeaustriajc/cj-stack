# Claude Code CLI

- No archive tool. Instead of Archive, end the report with the command to remove this worktree
  from the main checkout, such as `git -C <main checkout> worktree remove <path>`, under Run
  yourself: removing the shell's own folder breaks the shell.
- Background shells: a command run with `run_in_background` has a task id; stop it with
  `TaskStop`, then check its PID is gone with `kill -0 <pid>`.
- After a context summary, the inventory may miss items. This session's transcript is
  `~/.claude/projects/<cwd with / replaced by ->/<session id>.jsonl`; grep it for
  `run_in_background`, `docker run`, `git switch -c` and `git stash push`.
- Auto mode blocks a destructive git command and a kill of a process this session did not start.
  Do not work around a block: the item goes under Run yourself.
