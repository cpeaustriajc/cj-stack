# Weekly audit

Read this before you run or set up the weekly audit. The evidence rules in `SKILL.md` apply to it.

Run the verify skill on the default branch once a week, by a scheduled routine or a desktop
scheduled task. Mechanics: `references/claude-code.md`. Do these steps in this order:

1. **Source wave.** Read `references/claude-code.md` first. Start one read-only reader on the
   smallest model tier for each feature file, all at the same time. Each reader compares its
   feature file with the code on the **Code** line. It returns each drift
   as the code's `file:line` and the feature-file line that the code contradicts, or "no drift".
   A reader never drives the app and never edits.
2. **Churn sweep.** List the paths that the commits since the last audit changed. One more
   reader of the same kind finds the user-facing surfaces in them (routes, commands, screens) that no feature
   file lists. Drop each finding that has no source path.
3. **Live pass.** Drive every feature once in the live app, also when the source wave found no
   drift. A reader's drift is a lead: fix a feature file only after the live pass confirms it.

The audit:

- Ends in exactly one result:
  - **clean**: no PR.
  - **changed**: one PR that fixes only feature files and the verify skill.
  - **blocked**: names the blocker.
- Never edits product code.
- Sorts each mismatch into doc drift, harness gap or product regression. Doc drift and harness
  gaps go into the PR. A product regression goes to the tracker, not into the map.
- Treats an unlisted surface as doc drift: the PR adds its feature file, proved in the live pass.
