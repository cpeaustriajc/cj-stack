# interrogate

A skill that reviews a diff with fresh reviewers that never saw your session. Each reviewer sees a different slice of the change.

## When to use it

Use it before you open a PR on a risky change, such as auth, money, data migrations or concurrency. The session that wrote a change believes its own story. Reviewers without that story catch what the author explains away.

Say "interrogate", "second opinion" or "cross-check this".

- For a quick single-pass review, run the built-in `/code-review` command.
- To test a flow as a careless user, use `break-it`.
- To review a UI against a design, use `ui-polish`.
- To question a plan before you build, use `grill`.

## Example

You say: "Cross-check this payments refactor with fresh reviewers before I push."

1. Claude picks the diff: the one you named, else the current branch, else your staged changes.
2. Claude runs two or three read-only reviewers in parallel and checks each finding against the code.
3. Claude asks which findings you want fixed.

You get four groups: Act on, Consider, Noted and Dismissed. Each finding lists its reviewers, `file:line`, a proof level and a failure scenario.

## Install

The `engineering` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install engineering@cj-stack
```

To turn the plugin off, run `claude plugin disable engineering@cj-stack`. This also turns off every other skill in `engineering`.

Requirement: Claude must be able to start subagents.

## What it does

- Claude writes a bundle file with the diff, the full changed files with line numbers, the spec if one exists, and a short description.
- The Full reviewer sees the whole bundle. The Blind reviewer sees no description or spec and runs on a model one tier below the session. The Spec reviewer runs only if a spec or issue exists.
- Claude verifies each finding itself. A reviewer can be confidently wrong.
- Each finding has a proof level: stated, pointed at the line, walked through or run. Act on takes only walked through or run. A real finding with less proof goes to Consider, with a note on what would raise it.
- Dismissed findings stay visible with a one-line reason, so you can override them.
- Claude saves the bundle and the raw reviews in the ignored work folder (`.claude/work/<topic>/` in Claude Code) and tells you where they are.
- If you ask for a quality pass, a fresh reviewer reads the diff for reuse, quality and efficiency after your fixes. In Claude Code, this pass is the built-in `/simplify` skill.

## Limits

- It applies nothing until you pick which findings to fix.
- Reviewers look for real defects only. They give no style or naming notes.
- Two reviewers that agree prove little, because they share a model's blind spots.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method and the reviewer prompt.
- [references/claude-code.md](references/claude-code.md): how the reviewers and the quality pass run in Claude Code.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
