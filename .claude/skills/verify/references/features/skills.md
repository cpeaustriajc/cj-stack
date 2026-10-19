# Skills

What exists: the shipped skills in `skills/<bucket>/`, the in-progress ones, and this repo's own
`.claude/skills/`. A skill is Markdown plus optional scripts; there is no app to drive.

- **Code:** `skills/**` except `skills/**/.claude-plugin/**`; `.claude/skills/**`
- **Tests:** `.claude/skills/run-cj-stack/smoke.sh tests` (descriptions, script tests, READMEs)
- **Check:** `claude plugin validate .` exits 0; each changed `SKILL.md` names only files that exist
  (`grep -o 'references/[a-z-]*\.md'` on it, then `ls` each).
