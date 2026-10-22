---
name: create-pr
description: >
  This skill should be used when the user asks to open a pull request: "open a PR", "make a PR for
  this branch", "create a draft PR" or "PR this against develop". It commits, runs the fast
  checks, pushes and opens a PR that links the issue and the evidence ("draft" for a draft, or a
  base branch). The terminal version of the desktop Create PR button.
disable-model-invocation: true
argument-hint: "[draft] [base-branch]"
---

Open a pull request for the work in this session. Arguments: `$ARGUMENTS`. The word `draft`
means open it as a draft. Any other word is the base branch.

## Steps

0. **Remote.** If `gh auth status` fails, say so and stop. If there is no GitHub remote,
   look for a matching repo with `gh repo list`, then ask with the ask tool: link the match,
   create a private repo, or create a public one.
1. **Branch.** If you're on the default branch, create one named `claude/<short-topic>`
   (`claude/` is required by a hook). Otherwise stay on the current branch.
2. **Commit.** Keep the existing commits as they are; never squash or rewrite them. If
   changes are still uncommitted, commit them in small logical slices, with messages in the
   repo's style taken from `git log`. Never commit `.env`, credentials or files in
   `.gitignore`. Add no AI attribution, co-author trailers or "Generated with" lines.
3. **Comments.** A fresh read-only reader on the cheapest model, which did not write the
   code, reads the branch diff against the base for added or changed comments only. A comment
   stays only when it names a trap (something that breaks if the next reader edits blindly),
   in one line of at most two sentences and about 20 words. A comment rule in the repo's
   CLAUDE.md or AGENTS.md wins over this one. The reader lists every other comment with
   file:line and the reason. Remove or shorten each one it lists, commit that as its own
   slice, and don't argue for a listed comment: the author defends its own comments, which is
   why a separate reader checks them.
   Mechanics: `references/claude-code.md`.
4. **Check.** Run the project's fast checks (lint, typecheck, tests the repo's CLAUDE.md
   names). If one fails, stop and report it. Don't open a PR on red.
5. **Push** with `-u`.
6. **Existing PR.** If one is already open for this branch, push and report its URL. Don't
   open a duplicate, and don't change its draft or ready state.
7. **Open it** with `gh pr create`, adding `--draft` only when asked. Pass `--base` when a base
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

     Evidence shows before and after of the same state. A visual change gets a screenshot
     cropped to the change. A flow, a motion or a timing also gets a short video. Each video
     and screenshot:
     - shows where each click lands and which key was pressed, with no test code on screen.
       Use the project's helper when it has one. Playwright 1.64+:
       `screencast.show_actions(cursor="pointer", style={"title": "display: none", "point":
       "width: 28px; height: 28px; border: 3px solid red; border-radius: 50%"})` plus a key
       label of your own. Playwright draws no click mark unless `point` is styled.
     - plays at a person's pace: the hero script pauses before each action (`show_actions`
       `duration` does this), types at human speed and holds where the viewer reads.
       Failure: a 16-second clip of two whole flows that a reviewer could not follow.
     - starts after sign-in and setup and ends before cleanup, so it shows only the user's
       steps.
     - comes from a hero script: a standalone script made only for the video, run outside the
       test runner, that reuses the tests' setup helpers. Never film a test run with tracing on:
       tracing claims the page capture first, and the video shows a small corner of the page at
       about one frame a second.
     - opens each step with a chapter card (Playwright: `screencast.show_chapter(title,
       description=...)`) and reaches each page by the click a person would make, never a
       URL jump. Without both, the video jumps from page to page and the viewer gets lost.
     - closes on screen each tool it opens (a dev panel, a QA menu) before the user's next
       step, so no state changes without a visible cause.

     Before you attach a video, run `scripts/check-video.sh <file>` on the file you attach. It
     fails a file over the upload limit or a frame padded with grey, and lists each still over
     3 s: a chapter card is fine, a frozen step is not. Then read a contact sheet of its
     frames for the marks. Attach each file with `--attach ./file` and reference it in the body as
     `![alt](./file)`; gh uploads it and rewrites the path. Put a video alone in its
     paragraph. Otherwise name the test that failed before and passes after.

     Merge danger says whether the change is a one-way door (a migration, sent email, a
     charge, deleted data, a public API change) or a two-way door (a revert is clean), plus
     the blast radius in a few words, such as `Merge danger: one-way door, adds
     premium_prices table; blast radius: search results and checkout totals.`

     Link the issue as related; never write `Closes`, `Fixes` or `Resolves`, since merging
     would close the issue before the verifier marks it done. Find the issue
     in the branch name, the commits or the session. If there is none, leave the line out.
     Leave the Evidence line out when no E2E run happened; don't invent one. No headings,
     checklists or test-plan sections unless the template asks for them. Keep it short.

     Then read the title and body against **Plain prose** below, and rewrite each hit.

Report the PR URL on its own line, plus one line on anything skipped, such as "no issue
found" or "no evidence linked".

## Plain prose

A check cannot match these, so read for them. Rewrite each one in the title and body:

- **"Not only X but also Y", "not just X".** Say Y. "Not just a linter, it is a guard" becomes
  "It blocks the write."
- **Synonym cycling.** One name per thing. "the hook ... the guard ... the checker" becomes "the
  hook" each time.
- **Real names.** Use the name in the code. "the config loader" becomes `loadConfig`.
- **Abstract metaphor nouns** (surface, substrate, wedge, primitive, flywheel, north star). Name
  the thing. "the auth surface" becomes "the login and token endpoints".
- **Mannered prose** (aphorisms, code with feelings, "rides along"). "The cache quietly
  remembers" becomes "The cache keeps each result for 5 minutes."
- **Arrows and symbol-speak.** Write the sentence. "login → token → retry" becomes "After
  login, the client gets a token and retries once."
- **Dropped articles.** Keep "the" and "a" in sentences. "Fixes bug in parser" becomes "This
  fixes a bug in the parser."
- **"-ing" tails.** Split them off. "It adds a cache, ensuring fast reads" becomes "It adds a
  cache. Reads take 5 ms."
- **Feelings, not facts.** Give the measure. "This greatly improves search" becomes "Search
  takes 80 ms, not 900 ms." Test: could the sentence sit unchanged in another project's docs?
