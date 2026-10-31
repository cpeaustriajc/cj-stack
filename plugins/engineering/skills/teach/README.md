# teach

A typed `/teach` command that explains a part of your codebase in plain words. It joins how the code works and why it has its shape into one answer.

## When to use it

Use it when you want to understand a subsystem or a change, not only find it. The answer starts short and goes deeper when you ask.

- For a full walkthrough with file and function names, use `how`.
- For the evidence behind one choice, use `why`.

## Example

You type: `/teach how does an order get from checkout to the warehouse`

1. Claude reads the code, then runs the `how` and `why` methods side by side.
2. Claude writes one or two sentences that answer the question.
3. Claude shows a short series of diagrams. Each diagram repeats the last one and adds one part.
4. Claude offers to go deeper on a part.

A claim from `why` keeps its evidence label, such as "Inferred" or "appears to".

## Install

The `engineering` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install engineering@dotfiles
```

The skill then loads as `/engineering:teach`.

## What it does

- Reads the code, the git history and the pull requests of the subject.
- Uses only agents with read tools. A run changes no file.
- Writes the answer by the `unslop` rules: plain sentences, no filler, no framing labels.
- Shows the diagram series as a stepper in the desktop app. In a terminal, it prints one mermaid block per step.

## Limits

- It searches the tracker or the docs only when you ask why, or the subject is a past decision.
- It does not change code or propose a new design.
- It gives no quiz and does not ask you to repeat the answer.

## More

- [SKILL.md](SKILL.md): the method.
- [references/claude-code.md](references/claude-code.md): spawns, the diagram series and the text fallback.
- [LICENSE](LICENSE): adapted from pstack by Lauren Tan, under the MIT licence.
