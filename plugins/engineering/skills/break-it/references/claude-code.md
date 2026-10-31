# Claude Code

## Launch

- Launch with `/run`. It follows the project's recorded recipe when one exists (a
  `.claude/skills/run-<name>/` skill from `/run-skill-generator`), and otherwise guesses the
  launch from the project type and the README, `package.json` or `Makefile`.
- The guess is unreliable when the app needs a database, an env file or a multi-step build. A
  launch that fails is a setup problem, not an app bug.
- `/run` and `/verify` show a change working on the happy path. The careless users start only
  when the app is up.

Source: https://code.claude.com/docs/en/skills, section "Run and verify your app".
