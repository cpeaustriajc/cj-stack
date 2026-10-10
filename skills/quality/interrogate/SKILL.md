---
name: interrogate
description: Review a diff with fresh Claude reviewers that each see a different slice of it - the whole change, the code without its description, the spec against the code - then verify, filter and rank their findings into act on, consider, noted and dismissed, never auto-applying anything. Use when I say "interrogate", "second opinion", "cross-check this", or before opening a PR on a risky change (auth, money, data migrations, concurrency). Not for a quick single-pass PR review.
---

# Interrogate

The session that wrote a change believes its own story about it. Reviewers that never saw that
story, and that each get a different slice of the evidence, catch what the author explains
away. The value comes from the filtering at the end, not from piling up comments.

## 1. Pick the diff

The diff is, in order: what I named (PR number, branch, commit range), else the current branch
against its base, else staged and unstaged changes. Write a bundle file with the diff, the full
text of each changed file with its line numbers (`cat -n`, so reviewers cite the file's real
lines, not the bundle's), the spec or issue if one exists, and a one-paragraph description of
what the change is meant to do. Reviewers get only their slice of this bundle and don't explore.

## 2. Run the reviewers

Read-only subagents with fresh context, none of which has seen this conversation, run in
parallel. Diversity comes from what each one sees, never from personas:

- **Full**: the whole bundle, on Opus.
- **Blind**: the diff and the changed files with no description or spec, on Sonnet. It judges
  what the code does, not what it was meant to do, so it catches what the description explains
  away.
- **Spec**: only when a spec or issue exists. It gets the spec and the diff with no description,
  so it checks the code against what was asked, not what the author says was done.

Every reviewer gets the same prompt:

> Review this change for real defects only: wrong behaviour, regressions, broken edge cases,
> security holes, data loss, divergence from the spec. No style, naming or "consider adding"
> notes. For each finding give: file:line, a one-line defect, a concrete failure scenario
> (input or state → wrong result), and your confidence (high, medium or low). If you find
> nothing real, say "no findings".

## 3. Judge: filter, don't aggregate

Merge duplicates and note which reviewers raised each finding. Then verify each one against the
code yourself, since a reviewer can be confidently wrong. Sort them into:

- **Act on**: verified, real and in scope. Five at most; more means you aren't filtering
  hard enough.
- **Consider**: plausible but unverified, or real but a judgment call.
- **Noted**: true, out of scope or minor. One line each.
- **Dismissed**: wrong or irrelevant. Keep each one visible with a one-line reason so I can
  override.

Rank by verified severity. Agreement between reviewers counts for little: they share a model's
blind spots.

## 4. Report, then stop

Show the four groups, each finding with its reviewers, file:line and failure scenario. Ask with the
ask tool which to fix. Apply nothing until I pick. Save the bundle and the raw reviews in the
scratchpad and say where they are, so the review can be re-run.
