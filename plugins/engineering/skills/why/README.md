# why

A skill that answers "why is this code like this?" from git history, pull request reviews and the team's records. It labels each claim by its evidence.

## When to use it

Use it before you change or delete code that nobody explains: a magic number, a guard, a retry or a flag. It stops a plausible reason that nobody wrote down from becoming the answer.

- For a decision the team recorded, use `project-knowledge`.
- For recent work in flight, use `recall`.

## Example

You say: "Can I delete this null check in `parseOrder`? It looks pointless."

1. Claude reads the decision log, then runs `git blame` and `git log -S` on the line.
2. Claude reads the commit and pull request that added the check, and searches for the incident behind it.
3. If a tracker or docs tool is connected, Claude starts one investigator per source in parallel.

You get the claims labelled Direct, Supported, Inferred, Speculative or Unknown, the sources searched, and four lines: Preserve, Change, Avoid, Risk.

## Install

The `engineering` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install engineering@cj-stack
```

The skill then loads as `/engineering:why`.

## What it does

- Reads the decision log first, through the `project-knowledge` adapters.
- Runs read-only `git` and `gh` commands on the target lines.
- Searches for the outage or issue behind defensive code.
- Checks your own guess as one candidate, not as the answer.
- Starts one Haiku investigator for git and one Sonnet investigator per other source, only when two or more sources are available.
- Writes the answer in the chat. It writes no files.

## Limits

- It reads only sources it can reach. A source with no access is listed as a gap.
- It does not explain how code runs. Ask that directly.
- Chat tools, error trackers and analytics are not searched.

## More

- [SKILL.md](SKILL.md): the method and the evidence tiers.
- [references/git.md](references/git.md): the git and `gh` commands.
- [references/investigator.md](references/investigator.md): the brief each investigator gets.
- [references/claude-code.md](references/claude-code.md): models and spawn mechanics.
- [evals/triggers.json](evals/triggers.json): the trigger cases.
