# Claude Code

In the desktop app (the tool `mcp__ccd_session_mgmt__search_session_transcripts` is there), search
with `claude-desktop.md` first. This file is for the CLI, and for reading a transcript file.

- Transcripts: `~/.claude/projects/<cwd with / and . replaced by ->/<session id>.jsonl`, one per
  session; worktree sessions sit in folders that add `--claude-worktrees-<name>`.
- Filter by date with `find <folders> -name '*.jsonl' -mtime -<days>`, then `grep -l` the topic.
  Skip the `subagents/` folders.
- A line is one JSON event; user and assistant text is under `message.content`. The first event's
  `entrypoint` is `sdk-cli` for a headless or eval run: skip those.
- `claude agents --json` lists background sessions that are still running.
