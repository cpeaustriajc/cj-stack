# Claude Code

- `/doctor prompt-audit` audits CLAUDE.md, AGENTS.md, rules, skills, commands and
  agents for dated instructions, contradictions and missing files. It reports and edits nothing.
  Pass a path to audit one skill or folder.
- Headless (`claude -p "/doctor prompt-audit" --add-dir ~/.claude`) it needs the flag to read the
  global rules and agents, and the flag goes after the prompt, since it takes several paths.
- It reports installed plugin skills without proposing edits; audit the skill's source path instead.
- `claude-md-improver` (claude-md-management plugin) checks CLAUDE.md against the current code:
  stale commands and paths are prune candidates; its additions still pass step 2.
- Size limit: keep each always-loaded file (CLAUDE.md, a rule without `paths:`) under 200 lines;
  past that, Claude follows it less reliably.
- `/revise-claude-md` drafts one session's learnings; they are single-run corrections until they
  recur.

## Lens pass

- `python3 -I scripts/corrections.py --turns --out <file>` with the same `--project` and `--since`
  as the correction run. It refuses `--skill`: for `/hone <skill>`, run it without and keep only
  the findings about that skill. The file is about 6 times the size of the corrections file.
- Add `--chunk-lines 1500` to both runs: the script writes `<out>.NN.md` chunks, cut only between
  sessions. Tell each miner to read its chunk in 500-line parts: a miner on a cheap model given a bigger
  chunk stops early and reports a partial read as whole.
- Start the lens subagents and the correction miners in one message, so they run in parallel:
  one `Agent` per chunk on the cheapest model the session can pick, told to only read. Move
  up one model when an eval shows a miner misreads a lens.
- The skill list for the missed-trigger lens is the skills listing in this session's context plus
  the frontmatter of each `.claude/skills/*/SKILL.md` in the project.

## Missed trigger proof

Use what Claude Code ships; hone adds only the transcript evidence that a request was missed.
- `/skill-doctor` warns about skills never invoked in 7 days: a lead for the lens, not proof,
  since it has no list of requests that should have fired.
- skill-creator's description loop (`scripts/run_loop.py --eval-set <triggers.json>`) rewrites
  the description against should- and should-not-trigger requests. Add the missed request to
  the skill's `evals/triggers.json` as `"should_trigger": true` and run it; apply its
  `best_description` by hand.
- Prove it with `claude plugin eval <plugin> --case <case>`: a case in the plugin's `evals/` (a
  `prompt.md` with the missed request and a `tool_used` grader on `Skill` whose `input_match`
  names the skill) fails before the edit and passes after. It does not read `triggers.json`.
