# linear-gate

A mod (a plugin that adds a hook to Claude Code) that blocks Linear writes outside your shift. On shift, your permission mode decides, and the mod asks you only before a delete, retire or cancel.

## Why

A Linear write is visible to your whole team, and Linear can post it to Slack. After your shift, one write can notify your team at night.

On shift, a dialog for every write costs you many clicks. Auto mode can decide most writes. linear-gate keeps a dialog only for writes that remove or cancel work, and shows a plain description with a diff.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install linear-gate@cj-stack
```

To see that it is on, run `claude plugin list` and look for `linear-gate`. The install steps in the root README include this mod.

## Example

1. At 20:35, after your 18:00 shift end, Claude calls the Linear tool `save_issue`.
2. The mod denies the call. No dialog opens.
3. Claude reads the reason and puts the draft in the chat.

Claude reads:

```
linear-gate: off shift (09:00-18:00); a Linear write notifies the team's Slack. Do not retry: draft it in the chat for the next shift.
```

At 10:00, the same call goes to your permission mode. A call that moves ACME-77 to Canceled opens the dialog "Cancel issue ACME-77 — apply this change?". You pick "Cancel issue ACME-77" or "Leave it", or you type a note.

## What it does

| Event | Decision |
|---|---|
| Claude or a subagent calls a Linear write tool off shift | Deny it, also in a headless session. |
| Claude calls a Linear write tool on shift | Leave it to your permission mode. |
| Claude calls a delete, retire or cancel on shift | Ask you in a dialog. |
| Claude calls a Linear read tool | Let it pass. |
| You allow the write | Run it, then show a toast with the result. |
| You pick "Leave it" or type a note | Deny the call. Claude reads the reason. |
| You close the dialog | Deny the call. |
| No surface (an interface) is attached to the session on shift | Ask nothing. The host decides. |

The dialog names the action, such as "Create issue" or "Merge PR". It lists the changed fields. For a document edit, it shows removed text in red and added text in green.

A delete, a retire or a cancel adds the warning "⚠ Everyone on the team sees this."

The mod treats a tool as a write if its name is in the list in `hooks/register.tsx`. A tool on the `linear-server` server is also a write if its name starts with a write verb such as `save_`, `delete_` or `update_`.

## Settings

| Option | Default | Meaning |
|---|---|---|
| `shiftStart` | `09:00` | The local time your shift starts, 24-hour. |
| `shiftEnd` | `18:00` | The local time your shift ends. A start after the end crosses midnight. |
| `timeZone` | empty | An IANA zone such as `Asia/Manila`. Empty uses the zone of your machine. |
| `onShift` | `drastic` | `host`: your permission mode decides every write. `drastic`: ask before a delete, retire or cancel. `ask`: ask before every write. |

An hour that is not `HH:MM` makes both hours fall back to 09:00 and 18:00. Run `claude plugin configure linear-gate@cj-stack` to set them on your machine.

To turn the mod off, run `claude plugin disable linear-gate@cj-stack`.

## Limits

- A write tool from another server passes if its name is not in the list.
- A write tool with a new name on `linear-server` is gated only if it starts with a write verb.
- A long text or a long list of edits is cut in the dialog, with a count of what is hidden.
- If the document title lookup fails, the dialog shows the document id.
- The toast shows a failure only if the tool reports one.

## More

- [hooks/register.tsx](hooks/register.tsx): the hook source.
- [hooks/register.test.ts](hooks/register.test.ts): the tests for the questions and the decisions.
- [hooks/dialog.test.ts](hooks/dialog.test.ts): the tests for the dialog colors.
- [hooks/headless.test.ts](hooks/headless.test.ts): the tests for sessions with no surface.
- [hooks/shift.test.ts](hooks/shift.test.ts): the tests for the shift hours and the `onShift` option.
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json): the manifest.
