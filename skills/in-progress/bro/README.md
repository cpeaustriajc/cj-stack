# bro

A typed `/bro` command for a reply you did not understand. Claude says it again with the missing context first, in plain words and with one picture.

> In progress: not shipped in any plugin.

## When to use it

Use it when a reply skips a step, uses a term you do not know, or assumes a state you did not see. A shorter reply does not help then, so `/bro` adds what was missing.

- For a catch-up after you step away, use `ketchup`.
- For how a subsystem works, use `how`.
- For a rewrite of your own text, use `unslop`.

## Example

Claude replies "Fixed. Root cause was chain lapses: `passToNext` stamps `ready_at` while the copy is in transit." You type `/bro`.

1. Claude finds what the reply took for granted, such as the 7-day pickup window.
2. Claude reads `GLOSSARY.md` for the project's own terms.
3. Claude writes the reply again, context first, and adds one diagram.

You get full sentences that say what a hold is, why it lapsed, and what the fix changed. Then you get a diagram and the question again. If you type `/bro` again, Claude explains it from a new angle, at the same length.

## Install

The opt-in `cj-lab` plugin ships it:

```
/plugin install cj-lab@cj-stack
```

It starts only when you type `/bro`. Claude does not pick it on its own. To re-pitch other text, type `/bro <the text>`.

## What it does

- Reads `GLOSSARY.md` (or the one `GLOSSARY-MAP.md` points to), then `CLAUDE.md` or `AGENTS.md`, then the code, for the project's terms.
- Writes in ASD-STE100 Simplified Technical English: short full sentences, active voice, common words.
- Shows one diagram in the desktop app. A click on a box asks about that part. In a terminal, it prints a mermaid flowchart.
- Keeps the question of the first reply and adds no new findings.
- Writes no file, runs no build and starts no agent.

## Limits

- It does not do new work or answer a new question. It says the same message again.
- It does not make a reply shorter. Ask for a summary when you want that.

## More

- [SKILL.md](SKILL.md): the method.
- [references/claude-code.md](references/claude-code.md): the read-only tools and the diagram.
- [evals](../evals/bro-repitch/): the re-pitch case and the case with the last reply in the history.
- [LICENSE-wait-what](LICENSE-wait-what): follows Matt Pocock's `wait-what`, under the MIT licence.
- [LICENSE](LICENSE): adapted from pstack by Lauren Tan, under the MIT licence.
