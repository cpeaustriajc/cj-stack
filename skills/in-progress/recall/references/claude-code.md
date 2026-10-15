# Claude Code

- Transcripts: `~/.claude/projects/<cwd with / and . replaced by ->/<session id>.jsonl`, one per
  session; worktree sessions sit in folders that add `--claude-worktrees-<name>`.
- Filter by date with `find <folder> -name '*.jsonl' -mtime -7`, then `grep -l` the topic.
- A line is one JSON event; user and assistant text is under `message.content`.
- `claude agents --json` lists background sessions that are still running.
