# scout

A skill that helps you find what is still worth building. It looks for real demand, then filters each candidate for what a clone cannot take.

## When to use it

Claude loads this skill when you say "find me an idea", "what should I build", "is there a SaaS in this" or "scout this niche". It also loads when you ask what is still worth building while apps are cheap to copy.

It guards against four failures:

- An idea the model labs will ship next.
- A problem nobody pays to solve.
- A product with no way to reach a buyer.
- A tool a buyer builds alone in a weekend.

Do not use it to grill an idea you already have: use `vision`.

## Example

You say: "Scout this niche: bookkeeping for small dental clinics."

1. Claude asks what you have that others lack, what you want from the idea, and how much time you have.
2. Claude runs one or two research methods, such as reading incumbent reviews or a community's threads.
3. Claude scores each candidate against eight filters and the red flags.

You get a table with a verdict per candidate: pursue, test first or drop. Claude recommends one, or none.

## Install

The `planning` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install planning@cj-stack
```

The skill then loads as `/planning:scout`.

## What it does

- Claude asks its starting questions in one round, before any method.
- Claude picks methods that match your edge and looks things up instead of asking you.
- Claude writes each candidate as one line: who, the painful job, what they pay now, and the method that found it.
- You pick one. Claude hands it to `vision` with the evidence, so the worth-it round starts from facts.

The skill names no files to write.

## Limits

- It does not grill an idea you already have. `vision` does that.
- It can find nothing. Claude reports that as a good result.
- An unknown that decides a filter becomes a lookup or a test. Claude does not guess it.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the questions, the seven methods, the filters and the red flags.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
