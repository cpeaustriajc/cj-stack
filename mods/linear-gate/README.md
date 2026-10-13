# linear-gate

A mod (a plugin that adds a hook to Claude Code) that holds every Linear write until you allow it. Claude can read Linear freely, but it cannot change anything without your answer.

## Why

A Linear write is visible to your whole team. A comment, a status change or a deleted document cannot be taken back quietly.

The usual permission prompt shows a tool name and raw arguments. linear-gate shows a plain description of the change instead, and a diff for a document edit.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install linear-gate@cj-stack
```

To see that it is on, run `claude plugin list` and look for `linear-gate`. The install steps in the root README include this mod.

## Example

1. Claude calls the Linear tool `save_comment` on issue MP-77.
2. The mod holds the call and opens a dialog.
3. You pick "Post comment", or you pick "Leave it", or you type a note.

The dialog asks "Comment on issue MP-77 — apply this change?" and shows the comment text. If you allow the write, you see the toast "✔ Comment on issue MP-77". If you pick "Leave it", Claude reads:

```
linear-gate: the user denied this Linear write (Comment on issue MP-77).
```

If you type a note, Claude reads it too, after "Their note:".

## What it does

| Event | Decision |
|---|---|
| Claude calls a Linear write tool | Ask you in a dialog. |
| Claude calls a Linear read tool | Let it pass. |
| A subagent calls a Linear write tool | Ask you, as for Claude. |
| You allow the write | Run it, then show a toast with the result. |
| You pick "Leave it" or type a note | Deny the call. Claude reads the reason. |
| You close the dialog | Deny the call. |
| No surface (an interface) is attached to the session | Ask nothing. The host decides. |

The dialog names the action, such as "Create issue" or "Merge PR". It lists the changed fields. For a document edit, it shows removed text in red and added text in green.

A delete, a retire or a cancel adds the warning "⚠ Everyone on the team sees this."

The mod treats a tool as a write if its name is in the list in `hooks/register.tsx`. A tool on the `linear-server` server is also a write if its name starts with a write verb such as `save_`, `delete_` or `update_`.

## Settings

No settings.

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
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json): the manifest.
