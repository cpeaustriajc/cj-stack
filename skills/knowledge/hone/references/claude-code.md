# Claude Code

- `/doctor prompt-audit` (v2.1.283+) audits CLAUDE.md, AGENTS.md, rules, skills, commands and
  agents for dated instructions, contradictions and missing files. It reports and edits nothing.
  Pass a path to audit one skill or folder.
- Headless (`claude -p "/doctor prompt-audit" --add-dir ~/.claude`) it needs the flag to read the
  global rules and agents, and the flag goes after the prompt, since it takes several paths.
- It reports installed plugin skills without proposing edits; audit the skill's source path instead.
- `claude-md-improver` (claude-md-management plugin) checks CLAUDE.md against the current code:
  stale commands and paths are prune candidates; its additions still pass step 2.
- `/revise-claude-md` drafts one session's learnings; they are single-run corrections until they
  recur.
