# hone-nudge

A mod (a plugin that adds a hook to Claude Code) that suggests `/hone <skill>` after you correct Claude during a cj-stack skill. It points you to the [hone skill](../../plugins/knowledge/skills/hone/README.md), which turns repeated corrections into lasting fixes.

## Why

You correct Claude during a skill run, and the same correction comes back next week. The skill needs a fix, but you forget to run hone.

hone-nudge reads the session transcript when a turn ends. If you corrected Claude during a cj-stack skill, it prints one log line (a line in the session output) that names the skill.

## Install

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install hone-nudge@cj-stack
```

To see that it is on, run `claude plugin list` and look for `hone-nudge`. The mod is optional: no skill plugin installs it.

## Example

1. You run `/design:ui-polish`. Claude works on the screen.
2. You reply "no, wrong easing". The message counts as a correction.
3. Claude ends its turn. The mod finds one correction during `ui-polish`.

You see this log line: "1 correction during ui-polish. Run /hone ui-polish?". Run the suggested command to start hone.

## What it does

| Event | Decision |
|---|---|
| A turn ends | Read the transcript and count corrections per skill. |
| A skill has corrections and no nudge yet | Print one log line for that skill, then record it. |
| A skill was nudged before in this session | Print nothing. |
| Another Stop hook blocks the stop | Print nothing. |
| A session starts | Delete this mod's state files older than seven days. |

A correction is one of these:

- A message that starts with a word such as "no", "stop", "wrong", "wait" or "actually".
- An interrupt of Claude, or a rejected tool call.

The mod credits a correction to the last cj-stack skill that started before it. A skill starts by the Skill tool or by a slash command. The skill names are in `hooks/register.ts`. A name with another prefix, such as `other:ui-polish`, does not count.

The mod writes `{ "v": 1, "nudged": ["ui-polish"] }` to `~/.claude/mod-state/<session id>.hone-nudge.json`. If `CLAUDE_CONFIG_DIR` is set, the file goes to `$CLAUDE_CONFIG_DIR/mod-state`.

## Settings

No settings.

To turn the mod off, run `claude plugin disable hone-nudge@cj-stack`.

## Limits

- It finds corrections by word patterns. A correction that starts with other words slips through.
- A correction made before any cj-stack skill ran gets no nudge.
- If the mod cannot find a home directory, or cannot read the transcript, it prints nothing.
- If the state file cannot be read, the hook throws "hone-nudge: state file is unreadable".
- If the state file write fails, the hook throws "hone-nudge: could not record the nudge for this session".

## More

- [hooks/register.ts](hooks/register.ts): the hook source.
- [hooks/register.test.ts](hooks/register.test.ts): the tests.
- [hone skill](../../plugins/knowledge/skills/hone/README.md): what to do after the nudge.
- [marketplace.json](../../.claude-plugin/marketplace.json): the manifest, in this mod's entry.
