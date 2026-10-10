---
name: commit
description: Commit the uncommitted changes in small logical slices with messages in the repo's style, then push the current branch. Pass "local" to skip the push. Typed only - the terminal version of the desktop app's Commit and push button. Not for writing PR bodies or reviewing changes.
disable-model-invocation: true
argument-hint: "[local]"
---

Commit my uncommitted changes and push the current branch. Arguments: `$ARGUMENTS`.
`local` means don't push.

1. Read `git status`, `git diff HEAD` and `git log --oneline -10`. Match the repo's message
   style.
2. Split the work into small logical commits: one per concern, not one blob. Stage by path,
   never with `git add -A` blindly. Never commit `.env`, credentials or ignored files. Add no
   AI attribution or co-author trailers.
3. If you're on the default branch, create `claude/<short-topic>` first, since a hook
   requires the prefix.
4. Push with `-u` unless `local` was passed. If the push is rejected because the remote
   moved, pull with rebase only when it applies cleanly. On any conflict, stop and tell me.
   Don't resolve it.

Report the commits as `<sha> <subject>` lines, plus the branch and whether it was pushed.
