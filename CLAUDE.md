# cj-stack

If you are a more capable model than the one these skills and agents were written for, improve
the stack, and trim before you add: cut any rule you would follow without being told.

## Authoring tools

Use what Claude Code ships before writing your own checks:

- `claude plugin validate .` after any manifest, skill or frontmatter change.
- `claude plugin eval <plugin>` to prove a skill fires and helps: cases in `evals/`, scored against
  a no-plugin baseline.
- `claude plugin details <plugin>` for a plugin's components and projected token cost.
- `claude plugin test mods/<mod>` for a mod's hook tests.
- `skill-creator` and `plugin-dev` (claude-plugins-official) for drafting skills and plugin parts.

## Buckets

- `skills/planning/`, `skills/knowledge/`, `skills/quality/`, `skills/shipping/`: shipped in the `cj-stack` plugin.
- `skills/craft/`: shipped in the opt-in `cj-paint` plugin.
- `skills/in-progress/`: not shipped. A skill starts here.
- `skills/archived/`: shipped only in the opt-in `cj-jira` plugin, or not at all. Never delete a skill; archive it.

## Moving a skill

A skill changes bucket in one commit that also updates:

1. its path in the `skills` array of the right plugin in `.claude-plugin/marketplace.json`
2. its row in the README Skills table
3. the plugin's `version` (minor for an added or moved skill, patch for an edit)

Then run `claude plugin validate .`.

## Tool-neutral

A shipped skill holds a method that works on any tool. Tool mechanics go in `references/<tool>.md`
adapters; a team's roles, rules and taste stay in that team's repo, which the skill reads first.

## Copies

This repo is the only source. Never hand-copy a skill into `~/.claude/skills` or a project's
`.agents/skills`: a copy drifts, and a skill installed both ways is listed twice in every session.
