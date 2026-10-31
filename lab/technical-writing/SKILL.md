---
name: technical-writing
description: >
  This skill should be used when the user types /technical-writing to write, rewrite or review
  a doc, README, RFC, spec, PR description or commit message. It reads the repo's own writing
  rules first, then applies ASD-STE100 sentences.
disable-model-invocation: true
argument-hint: "<the text or file to write, rewrite or review>"
---

# Technical writing

Write so a tired engineer understands on the first read.

## Read the repo's rules first

Before you write, read the repo's own writing rules: `CLAUDE.md`, `.claude/rules/`,
`CONTRIBUTING`, and a docs style guide if one exists. Where they differ from this skill, they
win. Example: a README rule in `.claude/rules/` sets the structure of a README.

Three rules sit above the layers:

- **Cut every word that does no work.** "In order to" is "to".
- **Use the short, everyday word.** "Use", not "utilize". A long word must buy its length with
  precision.
- **When a rule makes a sentence worse, fix the sentence another way.** A sentence that obeys
  every rule and sounds machine-written has failed.

Write the real symbol, file, flag or command name, not a synonym. Do not invent jargon. A named
pattern is fine when the doc defines it at first use. To propose a new offender, put it and its
replacement in your reply as a diff to rule 26 (abstract metaphor nouns) of `../unslop/SKILL.md`.
Do not edit that skill.

Mix sentence lengths. Split a sentence that carries two thoughts, and keep a long one that
carries one. Be specific: not "schema changes can cause issues" but "a column rename fails the
build".

## Pick the mode first (Diátaxis)

One document has one mode. Action and learning: **tutorial**. Action and work: **how-to**.
Understanding and work: **reference**. Understanding and learning: **explanation**. Do not mix
modes. Split and link instead. Before you write a whole document, read
`references/diataxis.md` for the rules of its mode.

## Write sentences to the reader (Google developer style)

- Talk to the reader as "you", in the present tense.
- Say who does what: "the compiler checks", not "is checked".
- Write instructions as commands. Put the condition first: "To delete the file, click Delete."
- Put the common case first and the exceptions after.
- No buzzwords, no "please", and never "simply", "easy" or "quickly" in a procedure.
- Link text says where the link goes. Never "click here".
- A heading carries the point, in sentence case. One h1 per page, no skipped levels.
- Use numbered lists for sequences and bullets for the rest. Keep items parallel.
- Code goes in code font. UI elements go in bold. Use serial commas. No "etc.".

## Make statements load one at a time (ASD-STE100)

ASD-STE100 is the sentence standard.

- Write one instruction per sentence, at most 20 words, in the imperative.
- Keep any other sentence to at most 25 words, and a paragraph to at most 6 sentences.
- Use the active voice. Keep "the" and "a": "Remove the backup file", not "Remove backup file".
- Put a warning or a condition before the step it guards.
- Give each word one meaning, and use one word for each action.
- Avoid "-ing" words where you can.

## Leave no sentence open to two readings (Global English)

- Keep "only" and "not" next to the word they change.
- Break up noun strings: "the script that checks the proto-import budget".
- Make each "it", "they" and "this" point at one thing. Repeat the noun when in doubt.
- Do not drop verbs. Keep "that" where it shows the structure.
- Use periods, not semicolons or em dashes. No slashes, no "(s)" plurals.
- Call each thing by one name everywhere.
- No idioms, Latin abbreviations or metaphors.

## Voice and specifics

- Apply `unslop` to every doc you touch: read `../unslop/SKILL.md` and follow it.
- A PR description and a commit message are writing too. Every layer except Diátaxis applies.
- A PR body is a briefing that a reviewer reads in under a minute. It also has the evidence that
  the project's PR rule asks for, for example a before and an after. Link long logs. Do not
  paste them.
- Product UI strings are not documentation. Use the product's copy guidelines.
- Write real paths. Make every count true at the commit that lands it, and give the command
  that regenerates it.

For a before and an after of one rewrite, read `references/worked-example.md`.

## Credit

Adapted from pstack's `technical-writing` by Lauren Tan (MIT; see `LICENSE`).
