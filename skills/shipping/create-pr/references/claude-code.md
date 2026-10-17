# Claude Code adapter

- The comment reader is one `Agent` call with `model: "haiku"`. Paste the output of
  `git diff <base>...HEAD` and the comment rule into its prompt, so it needs no tools and sees
  nothing of this session.
- Neither built-in replaces it. `/simplify` checks reuse, simplification, efficiency and
  altitude, not comments. `/code-review` flags a comment only through its CLAUDE.md conventions
  angle, only when a CLAUDE.md states a comment rule, and it has a usage cap.
