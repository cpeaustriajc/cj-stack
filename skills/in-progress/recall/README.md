# recall

A skill that writes a short brief of where your work stands: recent threads, their state and one next step.

> In progress: not shipped in any plugin.

## When to use it

Use it at the start of a session that resumes work, or when you lose track of what is in flight. It reads past transcripts and the live git and pull request state.

- For corrections to learn from, use `hone`.
- For a recorded decision, use `project-knowledge`.

## Example

You say: "Where was I on the checkout work?"

1. Claude searches this project's sessions from the last 7 days for the topic.
2. Claude checks each thread against the branches, worktrees and pull requests.
3. Claude writes the brief in the chat.

You get up to 5 bullets of context, each thread tagged such as `[open PR #12]`, the recurring problems and one next step.

## Install

The opt-in `cj-lab` plugin ships it:

```
/plugin install cj-lab@cj-stack
```

## What it does

- Finds the matching sessions with one search: the desktop app's session search, or grep in the CLI.
- For 7 days or less, reads the matching parts itself, with no subagents.
- For a wider window with more than 3 matching sessions, it starts up to 5 Haiku subagents, one per session.
- In that case, one more Haiku subagent searches the repo's issues and pull requests.
- Starts one Sonnet subagent only if two sources disagree about one thread.
- Treats transcript and issue text as data, never as instructions.
- Runs `git` and the pull request list. The live state wins over a transcript.
- Writes nothing to disk. The brief stays in the chat.

## Limits

- It covers one project and 7 days unless you name more.
- The desktop app's search does not find headless `claude -p` or eval sessions.
- It does not resume a session. Open the cited session id for that.
- A thread that left no branch, pull request or transcript text is not found.

## More

- [SKILL.md](SKILL.md): the method.
- [references/claude-code.md](references/claude-code.md): where Claude Code keeps transcripts.
- [references/claude-desktop.md](references/claude-desktop.md): the desktop app's session search.
- [evals/triggers.json](evals/triggers.json): the trigger cases.
