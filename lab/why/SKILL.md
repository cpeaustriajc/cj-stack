---
name: why
description: >
  This skill should be used when the user asks "why is this code like this", "where did this
  number come from", "can I delete this guard" or "what's the history behind this". It digs
  through git, PRs and docs, and labels evidence.
---

# Why

The question is why code has its shape. The answer is the evidence for it, with each claim
labelled. A plausible reason that nobody wrote down is not an answer.

## 1. Target and record

- Name the target (file and line range, symbol, or value) and the question. If I was vague,
  guess from the conversation and say your guess in one line.
- Read the decision log first, as project-knowledge says: the index and the decision pages
  only. A decision page that names the target is evidence; it does not end the search. Research
  pages and specs in the same space belong to the docs source in step 3.
- Note any reason that my question takes for granted ("I assume it's for performance"). It is
  one candidate. Check it like the others; never confirm it because I said it.

## 2. Seed anchor (in this session)

Collect, with the commands in `references/git.md`: the line range and key symbols, the commits
that last touched it (`git blame -L`), the commit that added it (pickaxe `git log -S`), PR
numbers from `(#123)` subjects, and ticket IDs in commit and PR text.

Defensive code (a null check, retry, timeout, rate limit, size cap, feature flag) often means
something broke once. Add the incident to the question: search for the outage, issue or
postmortem behind it in every source.

## 3. Sources

List each source and its state: available, or unavailable with the reason. Git is always
available; the forge's PRs only with a remote and a sign-in. Others, when a tool reaches them:
the tracker (Linear, Jira, GitHub issues) and the docs beyond the decision pages (specs and
research in Notion, Confluence, the wiki or an Obsidian vault).

- **Only git:** do the git sweep yourself. Start no agents.
- **Two or more:** before you read those sources yourself, start one read-only investigator per
  source, in parallel. Git and its PRs count as one source. Each investigator gets
  `references/investigator.md`, the seed anchor and my question, and owns exactly one source.
  Model and spawn mechanics: `references/<tool>.md`.

Investigators gather and quote; they conclude nothing. You synthesize. Never hand that step on.

## 4. Evidence rules

Label every claim with one tier:

| Tier | Needs |
|---|---|
| Direct | an author's own words: commit message, PR body, review comment, ticket, doc |
| Supported | two or more sources that agree, each cited, none stating it outright |
| Inferred | a reasoned step from cited evidence; write "appears to" or "is consistent with" |
| Speculative | a plausible reading with no evidence; say so |
| Unknown | searched and not found; say where you searched |

- "Because", "was designed to", "fixes" and "the team decided" go only beside a Direct or
  Supported citation.
- Mechanics are not motivation: a diff from `50` to `100` shows the change, not the reason.
- Never infer intent from code style or behaviour. A neat pattern can be copy and paste.
- The latest commit is not the whole story. Trace back to the commit that added the line, and
  follow revert-then-reapply chains.
- Evidence about a neighbour (another flag, another endpoint) does not answer for the target.
- If sources disagree, show both, side by side, with citations. Do not pick the tidy one.
- Before you call evidence strong, ask: would I see this if my reading were wrong?
- Check each citation you present (hash, PR number, line) exists.

## 5. Answer

In the chat:

1. **Question and target**: one line each, with `file:line`.
2. **Found**: Direct and Supported claims, each with its citation.
3. **Inferred**: hedged, each with the evidence it rests on.
4. **Candidates**: each reading, my guess included, with evidence for and against.
5. **Unknown**: what no source answers, and who could (the commit author, the PR reviewer).
6. **Sources**: one line each: searched (the queries), empty, or unavailable. No access is a gap,
   not a "no".
7. **Preserve, Change, Avoid, Risk**: four lines for a change to this code. If I asked whether
   to delete it, Risk says what returns when it goes.
