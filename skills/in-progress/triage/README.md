# triage

A skill that checks an issue or pull request before anyone builds it. It gives the item one state and writes a brief that an agent can work from.

> In progress: not shipped in any plugin.

## When to use it

Use it before an agent starts on an issue, and when you want to know what waits on you. It stops two things: building what exists already, and handing an agent work it cannot prove done.

- You say "triage #42", "what needs my attention" or "can an agent take this?".
- You say "move #42 to ready-for-agent" or "write an agent brief".
- An idea from an article becomes an issue, and you want a check before the build.

Do not use it for open design questions: use `grill`. Do not use it to cut a spec into tickets: use `tickets`.

## Example

You say: "Triage #272."

1. Claude reads the issue and searches the code and the installed tools for the same feature.
2. Claude checks the decision log and closed items for an earlier rejection.
3. Claude reads each "Done when" item and finds one that needs a merge first.
4. Claude recommends `ready-for-human` and names that item, then waits for your go.

You get one label set and one comment with the brief and the items a person must do.

## Install

The `cj-lab` plugin lists this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-lab@cj-stack
```

To turn it off, run `claude plugin disable cj-lab@cj-stack`. This also turns off the other `cj-lab` skills.

## What it does

- Each item gets one state: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human` or `wontfix`.
- Each item also gets one category: `bug` or `enhancement`.
- Claude uses your team's label names when your repo states them.
- With no item named, Claude lists the issues and outside pull requests that wait on you, oldest first.
- Claude reproduces a bug, or runs a pull request's checks, before it recommends a state.
- Every comment starts with a line that says AI wrote it during triage.

## Limits

- It writes no label and no comment before you say go.
- It does not run on a schedule. You start it.
- It does not answer design questions. It hands them to `grill`.
- It supports GitHub with commands. Other trackers use their own MCP server or CLI.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [references/agent-brief.md](references/agent-brief.md): the brief and the triage notes.
- [references/github.md](references/github.md): the `gh` commands.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
