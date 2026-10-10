---
name: create-pr
description: Commit what's left, push the branch and open a pull request with a short body that links the issue and the evidence. Pass "draft" to open it as a draft. Typed only - the terminal version of the desktop app's Create PR button. Not for reviewing a PR or writing review comments.
disable-model-invocation: true
argument-hint: "[draft] [base-branch]"
---

Open a pull request for the work in this session. Arguments: `$ARGUMENTS`. The word `draft`
means open it as a draft. Any other word is the base branch.

## Steps

1. **Branch.** If you're on the default branch, create one named `claude/<short-topic>`
   (`claude/` is required by a hook). Otherwise stay on the current branch.
2. **Commit.** Keep the existing commits as they are; never squash or rewrite them. If
   changes are still uncommitted, commit them in small logical slices, with messages in the
   repo's style taken from `git log`. Never commit `.env`, credentials or files in
   `.gitignore`. Add no AI attribution, co-author trailers or "Generated with" lines.
3. **Check.** Run the project's fast checks (lint, typecheck, tests the repo's CLAUDE.md
   names). If one fails, stop and report it. Don't open a PR on red.
4. **Push** with `-u`.
5. **Existing PR.** If one is already open for this branch, push and report its URL. Don't
   open a duplicate, and don't change its draft or ready state.
6. **Open it** with `gh pr create`, adding `--draft` only when asked. Pass `--base` when a base
   was given or the branch was cut from one other than the default and it exists on origin
   (check with `git ls-remote --heads origin <base>`).
   - **Title**: what changed, in the repo's commit style.
   - **Body**: follow the repo's PR template if it has one. Otherwise:

     ```
     <1-3 lines: what changed and why, for a reviewer who hasn't seen the issue>

     Related: <issue link or key>
     Evidence: <before and after: E2E report, screenshots or video path/link, and the command to re-run it>
     Merge danger: <one-way or two-way door; blast radius>
     ```

     Summary visual: only when it clarifies, add the smallest one right after the line it
     supports. Prefer, in order, a `diff` block of the key change, a file or component tree,
     a call tree or pseudocode, then a Mermaid diagram when a flow changes. A typo or
     one-line fix gets none. The visual replaces prose and is never added on top of it.

     Evidence shows before and after. Visual changes get screenshots. Otherwise name the test
     that failed before and passes after.

     Merge danger says whether the change is a one-way door (a migration, sent email, a
     charge, deleted data, a public API change) or a two-way door (a revert is clean), plus
     the blast radius in a few words, such as `Merge danger: one-way door, adds
     premium_prices table; blast radius: search results and checkout totals.`

     Link the issue as related; never write `Closes`, `Fixes` or `Resolves`. Find the issue
     in the branch name, the commits or the session. If there is none, leave the line out.
     Leave the Evidence line out when no E2E run happened; don't invent one. No headings,
     checklists or test-plan sections unless the template asks for them. Keep it short.
7. **No remote.** If `gh auth status` fails, say so and stop. If there is no GitHub remote,
   look for a matching repo with `gh repo list`, then ask with the ask tool: link the match,
   create a private repo, or create a public one.

Report the PR URL on its own line, plus one line on anything skipped, such as "no issue
found" or "no evidence linked".
