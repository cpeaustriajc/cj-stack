# Claude Code adapter

- Hunters are `Agent` calls with `model: "opus"` and `effort: "high"`, unless I name another
  model. Send all three `Agent` calls in one message.
- Do not use `/code-review` as the hunter. It has a usage cap and stops mid-hunt.
- All hunters work in the session's own worktree. Disjoint shards keep their edits apart; never
  give them `isolation: "worktree"`, because their fixes must see each other next round.
- A `Workflow` script can run the rounds only when I ask for a workflow.
