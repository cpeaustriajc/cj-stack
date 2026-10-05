# cj-stack

## Buckets

- `skills/planning/`, `skills/knowledge/`: shipped in the `cj-stack` plugin.
- `skills/craft/`: shipped in the opt-in `cj-paint` plugin.
- `skills/in-progress/`: not shipped. A skill starts here.
- `skills/archived/`: shipped only in the opt-in `cj-jira` plugin, or not at all. Never delete a skill; archive it.

## Moving a skill

A skill changes bucket in one commit that also updates:

1. its path in the `skills` array of the right plugin in `.claude-plugin/marketplace.json`
2. its row in the README Skills table
3. the plugin's `version` (minor for an added or moved skill, patch for an edit)

Then run `claude plugin validate .`.

## Copies

This repo is the only source. Never hand-copy a skill into `~/.claude/skills` or a project's
`.agents/skills`: a copy drifts, and a skill installed both ways is listed twice in every session.
