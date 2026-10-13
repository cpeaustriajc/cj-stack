---
paths:
  - "skills/**/README.md"
  - "mods/*/README.md"
  - "mods/archived/*/README.md"
---

# README files for skills and mods

Each skill folder and each mod folder has a `README.md`. A person reads it, not Claude: Claude
loads `SKILL.md` and the hooks, never the README. `python3 -I scripts/check_readmes.py` checks
the structure and the sentence lengths.

## Reader

A developer who uses Claude Code but has never seen cj-stack. They give the README 30 seconds
to learn what the thing is, whether they need it, and how to turn it on.

## Write from the source

- Read the whole `SKILL.md` and its `references/`, or the mod's `hooks/`, `plugin.json` and
  tests, before you write. Every command, path, setting name and default in the README must
  exist in that source today. Never write a command you have not seen there or run.
- Do not copy the steps of `SKILL.md` into the README. Say what happens in terms the reader
  sees (files written, questions asked, actions blocked), then link to `SKILL.md` for the method.
- A value that changes often (a cap, a version, a count) stays in its source. Name the file.

## Structure

Line 1 is `# <folder name>`. Then one or two sentences: what it is and what it does for the
reader. An archived or in-progress folder adds a status line next:
`> Archived: not maintained.` or `> In progress: not shipped in any plugin.`

Then these `##` headings, in this order, with no other `##` headings:

| Skill | Mod | What the section answers |
|---|---|---|
| When to use it | Why | the problem it solves; for a skill also when not to use it, and which neighbour skill to use then |
| Example | Install | skill: you say X, Claude does Y, you get Z; mod: the install command and how to see it is on |
| Install | Example | skill: which plugin ships it and the install command; mod: you do X, the hook does Y, you see Z |
| What it does | What it does | what it reads, writes, asks, blocks or changes; a table for a mod's events and decisions |
| Limits | Settings | skill: what it does not do; mod: each `userConfig` option with its default, and how to turn the mod off |
| More | Limits | skill: links to `SKILL.md`, `references/`, `evals/`; mod: what slips through, what happens on error |
| | More | mod: links to the hook source, tests and design notes |

Keep the README under 100 lines. Use `###` headings inside a section only when it is long.

## Sentences (ASD-STE100)

- A step in a numbered list: at most 20 words, one instruction, imperative ("Run", "Open").
- Any other sentence, list item or table cell: at most 25 words. A paragraph: at most 6
  sentences, about one topic.
- Active voice, present tense, "you" for the reader. Keep the articles ("the", "a").
- Put a condition before the instruction: "If the hook denies a write, read the toast."
- Use common words. Define a cj-stack or Claude Code term at its first use, or link it.
- One word keeps one meaning in the whole README: do not change between "mod", "plugin" and
  "hook" for the same thing. No noun cluster longer than three words.
- No abbreviations such as "e.g." or "i.e.". No filler ("simply", "just", "powerful",
  "seamless"), no hedging, no marketing tone, no emoji.
- Lead each heading, bullet and paragraph with the word that carries the information.

## Check

`skills/quality/playbooks/README.md` and `mods/loop-brake/README.md` show the expected result.

Run `python3 -I scripts/check_readmes.py`. Then read the README as the reader above: can you say
in one sentence what it does, when you would use it, and how to turn it on?
