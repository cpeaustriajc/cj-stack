# Claude Code adapter

Mechanics for Claude Code. Read the current docs when a detail matters, since these change.

## Project verify skill runs before commit

- Put the skill at `.claude/skills/verify/SKILL.md` in the target project.
- Claude Code v2.1.286 or later runs a skill named `verify` before each commit.
  Docs: https://code.claude.com/docs/en/skills
- The commit step skips changes to docs or tests only.
- Plugin skills do not count. The bundled `/verify` and `/simplify` do not count.
- Do not set `disable-model-invocation: true`. Claude then does not get the instruction.
- The skill also needs `includeGitInstructions` not set to off.

## Recording a recipe

- `/run-skill-generator` records launch recipes to `.claude/skills/run-<name>/`.
- The bundled `/verify` records to `.claude/skills/verify/SKILL.md`. Edit that file to match the template.

## Weekly audit

- Use a scheduled cloud routine (`schedule` skill).
- Or use a desktop scheduled task.

## PR verdict

- In CI, use `anthropics/claude-code-action` on `pull_request`.
- Locally, start a fresh `Agent` subagent. Give it the diff and the verify skill only.

## Stronger gates

Weakest to strongest:

1. A `/goal` condition that names the verify command.
2. A Stop hook that runs the verify command and blocks on failure.
3. A fresh verifier subagent with no access to the author's session.

## Patch-id

`git patch-id` gives a stable id for a diff. Store the id with the verdict.
A later push that changes the patch-id voids the verdict.
