---
name: hone
description: Mine past Claude Code transcripts for the times I corrected, interrupted or pushed back on Claude, find the lessons that recur, and propose where each one should live - code structure, a lint rule, a hook, a test, a skill or an instruction file - plus what to prune, for my approval. With a skill name, improve that one skill from the corrections made while it ran. Use when I say "hone", "hone <skill>", "hone this skill", "improve this skill from my corrections", "reflect", "what do I keep correcting", "learn from my sessions", "why does Claude keep doing X", or after a session with several corrections. Not for updating one CLAUDE.md from a single session.
---

# Hone

A correction I've made twice is a missing mechanism. This skill finds those and proposes the
cheapest durable fix for each one. It applies nothing without my approval.

## 1. Gather

Run `scripts/corrections.py` to pull, from the transcripts on this machine, every place where I
corrected Claude: the reply right after Claude asked or acted, interrupted requests, rejected tool
calls, dismissed forms, and replies that open with "no", "why", "I already said", "stop" or
"don't". Scope it with `--project <substring>` and `--since <YYYY-MM-DD>`. It prints progress and
writes one markdown file of exchanges.

`/hone <skill>` runs it with `--skill <skill>`, which keeps only corrections made while that skill
was active (a plugin prefix is fine). Read that skill's SKILL.md and references before judging.

Large output goes to subagents: split the file into chunks and have read-only subagents return
the recurring patterns, each with 2-3 short verbatim quotes and the count of sessions it appears
in. Never quote secrets, tokens or credentials.

## 2. Keep only what recurs

A lesson qualifies only if it passes both tests:
- **Recurs**: it shows up in 2+ sessions, or once with an obvious cost.
- **Would be got wrong without it**: Claude would repeat the mistake if nothing changed. A
  one-off preference or a fact that's already enforced doesn't count.

A correction from a single run is listed under Rejected, not applied.

Also check the existing instruction files, skills and hooks. If a rule already exists and was
broken anyway, the fix is a stronger layer, not a second copy of the rule.

## 3. Prune as well as add

Look for:
- instruction lines that changed nothing in the transcripts, or were broken anyway
- repeated wasted tool calls
- checks or scripts that exist but aren't wired in

Each proposal states the lines it removes as well as the ones it adds.

## 4. Route each lesson to the strongest layer that can hold it

Strongest first:
1. **Code structure**: make the wrong thing impossible to write (a type, a boundary, one shared
   helper).
2. **Lint, typecheck or CI rule**.
3. **Hook** (use the `update-config` skill), when it's a tool-use pattern such as "never X on main".
4. **Test**: an end-to-end check, when it's a behaviour that regressed.
5. **Skill**: a procedure or a domain's know-how. A lesson about one skill goes into that
   skill's own SKILL.md or references, never a general instruction file. Edit the skill that
   covers it before writing a new one.
6. **Agent definition** (`.claude/agents/*.md` or a plugin's agents).
7. **Instruction file**: CLAUDE.md, AGENTS.md or a `paths:`-scoped rule. Only rules and
   preferences belong here, each one line, never a status, a date or a finding. Keep each
   always-loaded file under 200 lines.

A proposed lint, test or hook must first be shown failing on a real past instance of the
mistake, such as the commit or transcript where it happened. If it can't be shown failing, it
doesn't go in. A lint's error message names the fix, not just the problem. Any exception or
suppression a proposal adds carries an expiry, such as a date or an issue to remove it, in the
code or config it applies to and never in an instruction file.

Trap: edit a skill in its source repo, never in the installed plugin cache copy, which is
overwritten on update.

## 5. Propose, then stop

Present three groups:
- **Accept?**: each lesson with its evidence (quote and session count), the layer, and the
  exact diff or rule text.
- **Backlog**: worth doing but needs real work, such as a lint rule or a refactor.
- **Rejected**: patterns that failed the tests, each with one line of why, so I can override.

Ask which to apply using the ask tool. Apply only those. For files kept in a dotfiles manager,
re-add them there and commit, following the instruction file's rules for that.
