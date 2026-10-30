# Claude Code

## Build and launch recipe

- `/run-skill-generator` records how to build and launch the project as a project skill in
  `.claude/skills/run-<name>/`. `/run`, `/verify` and other agents in the repo follow it.
- `/verify` can also record its own recipe in `.claude/skills/verify/SKILL.md`.
- Launch steps live in that recipe, and `/run` finds it by itself. A feature file holds only how
  to reach, drive and check the feature after the launch.
- If no recipe exists, say so in the report and name `/run-skill-generator`. Do not write launch
  steps into a feature file to fill the gap.

Source: https://code.claude.com/docs/en/skills, section "Run and verify your app".
