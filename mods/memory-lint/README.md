# memory-lint

A mod (a plugin that adds a hook to Claude Code) that denies a memory write holding task state, a one-off reference or repo detail. Memory then keeps only what is worth relearning.

## Why

Auto memory (notes Claude saves between sessions) fills with entries that go stale: "currently migrating auth", "fixed in PR 412", "see src/api.ts:42". Later sessions read them as facts.

memory-lint checks each memory write. If the note holds one of these, the mod denies the write and tells Claude what memory is for.

## Install

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install memory-lint@dotfiles
```

To see that it is on, run `claude plugin list` and look for `memory-lint`. The mod is optional: `dotfiles` does not install it.

## Example

1. Claude writes `Currently migrating auth to OAuth; next step is the callback route.` to a file in `~/.claude/projects/<project>/memory/`.
2. The note holds task state, so the mod denies the write.

Claude reads this deny reason:

```
memory-lint: memory not saved. It holds task state (in progress, next step, this session, today). Memory keeps durable facts that would otherwise be relearned: the user's corrections and preferences, and non-obvious quirks of this project or environment that will still hold in a month. If this is one, restate it without the flagged parts. If it is task state, a finding, or readable from the repo, do not save it. A rule the team shares goes in AGENTS.md or a checked-in rule; a decision goes in the team's decision log.
```

## What it does

The mod checks the Write and Edit tools on Markdown files in the memory directory. It denies a write that matches one of these checks:

| Check | Example |
|---|---|
| Task state | `currently`, `next step`, `today`, `just fixed` |
| One-off reference | `PR #412`, a commit hash, a `claude/` branch |
| Repo detail | `src/api/client.ts:42`, a code block |
| Short-lived fact | `next week`, `still pending`, a `/tmp` path, a plan path |
| Dated status | `since 2026-09-04`, `as of 2026` |
| Size | a topic file or a `MEMORY.md` line over a set length |

The size limits are in `hooks/register.ts`. A Write is checked whole, without its frontmatter. An Edit is checked only on the lines it adds, so removing or shortening memory always passes.

The default memory directory is `~/.claude/projects/<project>/memory`. A file outside the memory directory passes.

## Settings

| Option | Default | Meaning |
|---|---|---|
| `memoryDir` | empty | Your `autoMemoryDirectory` setting, if you moved memory out of the default directory. |

With the default, the mod checks only the default directory. Run `claude plugin configure memory-lint@dotfiles` to show the options and which are unset.

To turn the mod off, run `claude plugin disable memory-lint@dotfiles`.

## Limits

- It checks word patterns. A harmless note can match, and a stale note in other words can pass.
- It checks the Write and Edit tools only. A shell command that writes a memory file passes.
- If the check itself throws an error, the write passes.

## More

- [hooks/register.ts](hooks/register.ts): the hook source and the checks.
- [hooks/register.test.ts](hooks/register.test.ts): the tests.
- [marketplace.json](../../.claude-plugin/marketplace.json): the manifest, in this mod's entry.
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json): the option and its default (`userConfig`).
