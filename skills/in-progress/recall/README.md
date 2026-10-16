# recall

A skill that writes a short brief of where your work stands: recent threads, their state and one next step.

> In progress: not shipped in any plugin.

## When to use it

Use it at the start of a session that resumes work, or when you lose track of what is in flight. It reads past transcripts and the live git and pull request state.

- For corrections to learn from, use `hone`.
- For a recorded decision, use `project-knowledge`.

## Example

You say: "Where was I on the checkout work?"

1. Claude searches this project's transcripts from the last 7 days for the topic.
2. Claude checks each thread against the branches, worktrees and pull requests.
3. Claude writes the brief in the chat.

You get up to 5 bullets of context, each thread tagged such as `[open PR #12]`, the recurring problems and one next step.

## Install

The opt-in `cj-lab` plugin ships it:

```
/plugin install cj-lab@cj-stack
```

## What it does

- Reads the transcripts of the current project with one search.
- Reads up to 5 matching sessions itself. For more, it starts Haiku subagents, one per group of about 5 sessions.
- Starts one Sonnet subagent only if two transcripts disagree about one thread.
- Runs `git` and the pull request list. The live state wins over a transcript.
- Writes nothing to disk. The brief stays in the chat.

## Limits

- It covers one project and 7 days unless you name more.
- It does not resume a session. Open the cited session id for that.
- A thread that left no branch, pull request or transcript text is not found.

## More

- [SKILL.md](SKILL.md): the method.
- [references/claude-code.md](references/claude-code.md): where Claude Code keeps transcripts.
- [evals/triggers.json](evals/triggers.json): the trigger cases.
