# Claude Code adapter

- Hunters are `Agent` calls with `model: "opus"` and `effort: "high"`, unless I name another
  model. Send all three `Agent` calls in one message.
- Do not use `/code-review` as the hunter. Its `--fix` applies the findings after the review,
  with no failing test first, to any file, not only the hunter's shard. A second `/code-review`
  started while one runs goes to the foreground, so three cannot run in parallel. Source:
  https://code.claude.com/docs/en/code-review-local, sections "Tune effort and arguments" and
  "Run in the foreground".
- All hunters work in the session's own worktree. Disjoint shards keep their edits apart; never
  give them `isolation: "worktree"`, because their fixes must see each other next round.
- A `Workflow` script can run the rounds only when I ask for a workflow.
