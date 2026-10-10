---
name: interrogate
description: Review a diff with reviewers from different model vendors, then verify, filter and rank their findings into act on, consider, noted and dismissed - never auto-applying anything. Use when I say "interrogate", "second opinion", "cross-check this", "review with other models", or before opening a PR on a risky change (auth, money, data migrations, concurrency).
---

# Interrogate

One model reviewing its own vendor's code shares its blind spots. Different vendors fail
differently, so a finding two of them agree on is worth more than one only Claude raises. The
value comes from the filtering at the end, not from piling up comments.

## 1. Pick the diff

The diff is, in order: what I named (PR number, branch, commit range), else the current branch
against its base, else staged and unstaged changes. Write it to a file, together with the full
text of each changed file with its line numbers (`cat -n`, so reviewers cite the
file's real lines, not the bundle's), the spec or issue if one exists, and a one-paragraph description of
what the change is meant to do. Reviewers get only this bundle. They don't explore, so the review
works on models without tool use too.

## 2. Pick the reviewers

Use 2-3 reviewers from **different vendors**, and always one Claude subagent. Find the others
through an adapter:
- `references/opencode.md`: OpenCode CLI, for GPT, Gemini, Grok, Kimi, GLM and DeepSeek.
- `references/local.md`: a local model behind an OpenAI-compatible server (llama.cpp, Ollama,
  LM Studio).

Probe each one with a one-line prompt first. If only Claude works, say so in one line: the
review then runs Claude at two tiers, which catches less. Don't pretend it's cross-vendor.

Every reviewer gets the **same prompt**. Diversity comes from the model, not from personas:

> Review this change for real defects only: wrong behaviour, regressions, broken edge cases,
> security holes, data loss, divergence from the spec. No style, naming or "consider adding"
> notes. For each finding give: file:line, a one-line defect, a concrete failure scenario
> (input or state → wrong result), and your confidence (high, medium or low). If you find
> nothing real, say "no findings".

## 3. Judge: filter, don't aggregate

Merge duplicates and note which vendors raised each finding. Then verify each one against the
code yourself, since a reviewer can be confidently wrong. Sort them into:

- **Act on**: verified, real and in scope. Five at most; more means you aren't filtering
  hard enough.
- **Consider**: plausible but unverified, or real but a judgment call.
- **Noted**: true, out of scope or minor. One line each.
- **Dismissed**: wrong or irrelevant. Keep each one visible with a one-line reason so I can
  override.

Weight agreement: a finding raised by 2+ vendors and verified goes first.

## 4. Report, then stop

Show the four groups, each finding with its vendors, file:line and failure scenario. Ask with the
ask tool which to fix. Apply nothing until I pick. Save the bundle and the raw reviews in the
scratchpad and say where they are, so the review can be re-run.
