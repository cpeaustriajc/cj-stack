# microinteraction

A typed `/microinteraction` command that finds where a web page should animate, and where it should not. Each proposal plays inline, and you pick which ones you want.

## When to use it

Use it when a page works but feels flat, and you want small, well-timed motion in the right places. It rejects most candidates on purpose.

- To review motion that already exists, use `ui-polish`.
- To build an effect you already chose, write it yourself or ask Claude directly.

## Example

You type: `/microinteraction the goals page`

1. Claude reads the page's code and maps how often a user sees each part.
2. Claude gates each candidate on frequency, purpose, speed and function.
3. Claude shows each surviving proposal playing on a copy of the element, with its values.

You get a table of proposals, a list of rejected places with reasons, and Pick and Skip for each proposal. Nothing is built.

## Install

The `design` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install design@dotfiles
```

The skill then loads as `/design:microinteraction`.

## What it does

- Reads the area you name and its styles. It writes no file in your project.
- Names each proposal's effect with a term from the glossary, such as Scale in or Stagger.
- Gives each proposal a purpose, a frequency, and exact values: property, duration and curve.
- Plays each proposal inline in the Claude app, with Pick, Skip and a Send button.
- Prints the proposals as text in a terminal, and waits for your reply.
- Ships an example library: good and bad versions of each effect, as GIFs and frame sheets.

## Limits

- It does not build a pick. It stops when you pick.
- It judges feel from code and stand-in copies, not from your running app.
- It covers web motion only, not native apps.

## More

- [SKILL.md](SKILL.md): the method, the gate and the output format.
- [references/claude-code.md](references/claude-code.md): the inline view and the pick in Claude Code.
- [references/animation-vocabulary.md](references/animation-vocabulary.md): the glossary of effect names.
- [library/index.md](library/index.md): the example library and the command that re-makes it.
- [LICENSE](LICENSE): adapted from Emil Kowalski's skills, under the MIT licence.
