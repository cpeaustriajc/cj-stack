# Claude desktop app

- Archive this session: `mcp__ccd_session_mgmt__archive_session` with `session_id: "self"`. It
  stops the session and removes its worktree, so never `git worktree remove` your own worktree
  first. A worktree with uncommitted changes stays on disk. The conversation ends after the call.
- A session started from this one (`list_sessions` with `linked: true`) is archived with it if it
  shares the worktree or is idle. One that is still working blocks the archive: name it under Kept.
- Live sessions for the repo sweep: `mcp__ccd_session_mgmt__list_sessions`; a worktree whose path
  is the `cwd` of an unarchived session is Keep.
- Worktrees of sessions idle for 30 days or more: `mcp__ccd_host__clean_up_worktrees` shows its own
  approval card. Use it in the sweep instead of `git worktree remove` for those.
- `auto_archive_on_pr_close` (`mcp__ccd_settings__get_settings`) archives a session when its PR
  closes, but it leaves processes, containers, stashes and evidence. Run Session cleanup anyway.
