# unslop

A typed `/unslop` command that rewrites your text without the common tells of AI-written prose. The rewrite keeps the meaning and the tone you want.

## When to use it

Use it on a draft before other people read it: a README, a PR body, a ticket or a message. AI drafts often carry words like "delve" and "pivotal", em dashes, groups of three and filler phrases.

- For comments in code, use `no-comments`.
- For a README in this repo, also follow `.claude/rules/wiki.md`.

## Example

You type: `/unslop Additionally, this pivotal update serves as a testament to our team's dedication — showcasing speed, reliability, and scale.`

1. Claude scans the text for each pattern in the list.
2. Claude rewrites the text without them and keeps each claim.

You get plain text back, for example: "This update makes the app faster and more reliable at scale."

## Install

The `writing` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install writing@cj-stack
```

To turn the plugin off, run `claude plugin disable writing@cj-stack`. This also turns off every other skill in `writing`.

## What it does

- Reads the text you give it. It does not read your code or your files.
- Checks the text against a numbered list of patterns: content, language, style, chatbot phrases, filler, jargon and plain speech.
- Gives back the rewritten text with the same meaning.
- Keeps the pattern numbers stable, so other skills can cite a pattern by its number.

## Limits

- It does not check facts. A wrong claim stays wrong.
- It does not invent sources. If your text gives no source for a claim like "experts believe", the claim is deleted.
- It writes no file, unless you ask Claude to save the result.

## More

- [SKILL.md](SKILL.md): the method and the full pattern list.
- [LICENSE](LICENSE): adapted from pstack by Lauren Tan, under the MIT licence.
