# technical-writing

A writing standard for the docs, READMEs, specs, PR descriptions and commit messages that Claude writes or reviews. Your text gets a clear structure and short, plain sentences.

## When to use it

Use it for text that engineers read: docs, READMEs, specs, PR bodies and commit messages. Type `/technical-writing` with the text or the file.

- For product UI copy, use the product's copy guidelines. This skill does not apply.
- To remove AI tells from any text on demand, type `/unslop`. This skill applies `unslop` itself.

## Example

You type: `/technical-writing rewrite the "Proto budget" paragraph in README.md`. The paragraph has passive verbs and filler.

1. Claude reads the repo's writing rules, such as `CLAUDE.md` and `.claude/rules/`.
2. Claude rewrites the paragraph: real file names, active verbs, one thought per sentence.

You get a shorter paragraph that says the same facts, with the condition before each instruction.

## Install

The `writing` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install writing@dotfiles
```

To turn the plugin off, run `claude plugin disable writing@dotfiles`. This also turns off every other skill in `writing`.

## What it does

- Reads the repo's own writing rules first. Where they differ from the skill, the repo's rules win.
- Picks one Diátaxis mode for a whole document: tutorial, how-to, reference or explanation.
- Writes sentences to ASD-STE100: an instruction has at most 20 words, any other sentence at most 25.
- Applies the `unslop` pattern list to the text it writes.
- Keeps a PR body short, with the evidence that the project's PR rule asks for, and links long logs.

## Limits

- It does not check facts. A wrong claim stays wrong.
- It does not write product UI strings.
- It does not edit `unslop`. It proposes a new pattern in the reply instead.

## More

- [SKILL.md](SKILL.md): the method and the sentence rules.
- [references/diataxis.md](references/diataxis.md): the rules for each of the four modes.
- [references/worked-example.md](references/worked-example.md): one rewrite, before and after.
- [Evals](../../evals/): the `technical-writing-readme-rewrite` and `technical-writing-not-ui-copy` cases.
- [LICENSE](LICENSE): adapted from pstack by Lauren Tan, under the MIT licence.

### Sources and evidence

- Source: pstack's `technical-writing` by Lauren Tan, from `cursor/plugins` at commit `4dd1d05`, under the MIT licence.
- Changes: repo rules first, ASD-STE100 sentence limits, and pstack's own repo rules removed.
- Status: tested on one case. In `technical-writing-readme-rewrite`, typed as `/technical-writing`, 2 of 2 runs pass with the plugin and 0 of 2 pass without it.
- Without the plugin, Claude does not read `CONTRIBUTING.md` and keeps "ratchet" and the semicolon. A PR description case passed 2 of 2 in both arms, so it was dropped.
- Eval command: `claude plugin eval plugins/writing --case 'technical-writing-*' --scaffold`.
- Native check: Claude Code has no writing standard. Output styles set the chat tone for a whole session and are not picked by task.
- Prior art: Matt Pocock's `writing-for-agents` covers docs that agents read. His `writing-*` skills shape articles. Neither covers engineering docs for people.
