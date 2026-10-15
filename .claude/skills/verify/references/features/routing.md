# Routing

What exists: `skills/evals/<case>/` checks that each request loads its own skill.

- **Code:** `skills/evals/**`; the frontmatter of any `SKILL.md` (name or description)
- **Tests:** `.claude/skills/run-cj-stack/smoke.sh routing` (about $2 and a few minutes; `RUNS=1`
  halves it). Run it only when this feature is selected.
- **Check:** the eval report shows every case passing.
