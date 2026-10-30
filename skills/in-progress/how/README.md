# how

A typed `/how` command that explains how a part of your codebase works. It names the files and functions, so you can follow it without opening them.

> In progress: only in the opt-in `cj-lab` plugin.

## When to use it

Use it before you change a subsystem you do not know, or when you ask where new code should live. It gives you a working picture of the flow at the level of a senior engineer who joins the team.

- For why code has its shape, use `why`.
- For recent work in flight, use `recall`.

## Example

You type: `/how how does a goal get saved`

1. Claude sees a wide question and starts two to four read-only explorers, one per part of the flow.
2. One explainer reads their findings, checks the code where they disagree, and writes the answer.
3. Claude shows How It Works as a stepper. You click through it stage by stage, and a click on a stage asks a follow-up about it.

You get the sections Overview, Key Concepts, How It Works, Where Things Live and Gotchas. A section with nothing to say is left out.

## Install

The opt-in `cj-lab` plugin ships it:

```
/plugin install cj-lab@cj-stack
```

It starts only when you type `/how`. Claude does not pick it on its own.

## What it does

- Takes a narrow question in one pass: one explainer reads and explains.
- Starts Haiku explorers for a wide question, then one Sonnet explainer that joins their findings.
- Uses only agents with read tools. A run changes no file.
- Shows the stepper in the desktop app. In a terminal, it prints the stages as a list and a mermaid flowchart.

## Limits

- It reads code, not history. It does not say why a choice was made.
- It does not change code or propose a new design.
- A part it cannot trace is listed as an open question, not guessed.

## More

- [SKILL.md](SKILL.md): the method.
- [references/explorer-prompt.md](references/explorer-prompt.md): the brief each explorer gets.
- [references/explainer-prompt.md](references/explainer-prompt.md): the brief and the output sections.
- [references/claude-code.md](references/claude-code.md): models, spawn calls and the stepper.
- [LICENSE](LICENSE): adapted from pstack by Lauren Tan, under the MIT licence.
