# Claude Code adapter

- Reviewers are `Agent` calls. Send all of them in one message. The Blind reviewer sets
  `model` to the next cheaper model the session can pick.
- The ignored work folder is `.claude/work/<topic>/`.
- `/code-review` is the built-in correctness pass. For a quick single-pass review, point me to
  it instead of this skill. Never use it as one of the reviewers: it has a usage cap and can stop
  mid-review.
- The quality pass is the bundled `/simplify` skill (`Skill` tool, `skill: "simplify"`), with
  the diff target as its argument. It runs its own cleanup agents and applies the fixes. Do not
  write a separate quality reviewer.
