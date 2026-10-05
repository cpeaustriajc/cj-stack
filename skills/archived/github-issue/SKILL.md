---
name: github-issue
description: Creating or updating the GitHub Issues that hold implementation detail (engineering context) for this project's Jira tickets — field names, probe data, architecture, latency budgets. Use whenever technical detail needs a home, a Jira draft contains implementation content, or issues/milestones/sub-issues are being organized on the repo.
---

# Engineering context — GitHub Issues

Implementation detail never goes into a Jira description (see the
`jira-ticket` skill's "Where content lives" rule). Its home is a GitHub Issue
on `cpeaustriajc/marketplace-strangedomains`.

## What belongs here

File paths, code symbols, API fields and probed coverage numbers, upstream
operator traps, latency budgets and caching plans, architecture decisions,
routing constraints, quality gates. Anything the PO or QA does not need
— they read Jira only; the engineer reads both.

## Structure

- **One issue per Jira ticket** (epic and each story), not one big issue.
- **Title carries the Jira key**: `"MP-79 engineering context: <topic>"`.
  The naming is the whole cross-reference — do NOT link the issue from the
  Jira ticket, and do not paste Jira content into the issue beyond a one-line
  pointer to the key.
- **Milestone = sprint**: assign every issue to the current sprint milestone
  (e.g. "Sprint 2"); ask CJ which milestone if unclear.
- **Sub-issue hierarchy mirrors Jira**: story issues are sub-issues of their
  epic's issue. Attach via
  `gh api -X POST repos/<repo>/issues/<epic#>/sub_issues -F sub_issue_id=<id>`
  where `<id>` is the child's numeric `.id` (not its number).
- Shared material (signals tables, scorer guard rails) lives once in the
  epic's issue; story issues reference it ("see the MP-nn issue on this
  milestone") instead of duplicating it.

## Content rules

- State probe dates and hosts next to every measured number; never present
  spec claims as observed behaviour (`.agents/references/strangeproxy-reference.md`
  is the discrepancy source of truth).
- Name traps plainly: what breaks, the failing input, the guard.
- Keep quality gates (pnpm checks, E2E evidence, testid stability, release note) as a
  checklist the PR can be judged against.

## Workflow

1. Draft tickets locally first (the client's temporary artifact directory outside the repository);
   keep technical material under an "Engineering context" heading in the
   draft while iterating.
2. Once CJ approves, create the issue(s) with `gh issue create` +
   `--milestone`, attach sub-issues, then DELETE the engineering section from
   the local draft — the draft must end up Jira-transcribable as-is.
3. When authorized to update an issue after implementation contradicts it,
   update the body rather than piling on comments. If the integration is
   unavailable, return the proposed text; do not claim it was published.
