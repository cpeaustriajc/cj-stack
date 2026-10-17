---
name: interrogate
description: >
  This skill should be used when the user says "interrogate", "second opinion" or "cross-check
  this", or before opening a PR on a risky change (auth, money, data migrations, concurrency). It
  reviews a diff with fresh reviewers that each see a different slice of it, then verifies,
  filters and ranks their findings into act on, consider, noted and dismissed, never auto-applying
  anything. Not for a quick single-pass review.
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
parallel. Diversity comes from what each one sees, never from personas. Tool mechanics:
`references/claude-code.md`.

- **Full**: the whole bundle, on the session's own model.
- **Blind**: the diff and the changed files with no description or spec, one model tier below
  the session's (the same model when none is below). It judges
  what the code does, not what it was meant to do, so it catches what the description explains
  away.
- **Spec**: only when a spec or issue exists. It gets the spec and the diff with no description,
  so it checks the code against what was asked, not what the author says was done.

Every reviewer gets the same prompt:

> Review this change for real defects only: wrong behaviour, regressions, broken edge cases,
> security holes, data loss, divergence from the spec. No style, naming or "consider adding"
> notes. For each finding give: file:line, a one-line defect, a concrete failure scenario
> (input or state → wrong result), your confidence (high, medium or low), and the highest proof
> level that is true:
>
> - stated: claimed, with no location.
> - pointed at the line: file:line given.
> - walked through: the call path traced by hand, with the inputs that trigger it. Give the path.
> - run: a command, test or repro executed. Give the command and its output.
>
> If you find nothing real, say "no findings".

## 3. Judge: filter, don't aggregate

Merge duplicates and note which reviewers raised each finding. Then verify each one against the
code yourself, since a reviewer can be confidently wrong. Your check sets the final proof level:
raise it when you trace the path or run a repro yourself, lower it when the reviewer's path or
output does not hold. Sort them into:

- **Act on**: real, in scope, and walked through or run. Example: a null deref at cart.ts:42
  whose call path was traced but not run is walked through, so it can go here.
- **Consider**: plausible, or real but a judgment call. A real finding that is only stated or
  pointed at the line goes here, with a note on what would raise it, such as "run refund with
  an amount equal to the charge".
- **Noted**: true, out of scope or minor. One short row each.
- **Dismissed**: wrong or irrelevant. Keep each one visible with a one-line reason so I can
  override.

Rank by verified severity. Agreement between reviewers counts for little: they share a model's
blind spots.

## 4. Report, then stop

Show the four groups as tables, one row per finding with its reviewers, file:line, proof level
and failure scenario. Every row has a proof level, in Noted and Dismissed too. Ask with the ask tool which to fix. Apply nothing until I pick. Save the
bundle and the raw reviews in the ignored work folder (`.claude/work/<topic>/` in Claude Code)
and say where they are, so the review can be re-run.

## 5. Quality pass, only when I ask

When I ask for it ("check quality too", "simplify it"), run it after the report, and after the
fixes I picked if I picked any. A fresh reviewer that did not write the code reads the diff for
reuse, quality and efficiency, never for defects. Its changes stay uncommitted so I can read and
revert them. Tool mechanics, such as a built-in that already does this pass:
`references/claude-code.md`.
