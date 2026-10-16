---
name: recall
description: >
  This skill should be used when the user says "recall", "where was I", "catch me up", "what did
  we do last week", "what's in flight" or "pick up where we left off", or at the start of a
  session that resumes work. It writes a short brief of the recent work in this project from past
  transcripts and the live git and pull request state. Corrections to learn from go to hone; a
  recorded decision goes to project-knowledge.
---

# Recall

A short brief of where the work stands, cheap enough to run at the start of any session.

1. Scope: the current project, the last 7 days, and the topic if I named one.
2. Search the transcripts once with grep for the topic or for branch names, issue keys and PR
   numbers, and count the matching sessions. Where they live: `references/<tool>.md`.
   - 5 or fewer: read only the matching regions yourself. No subagents.
   - More than 5: start read-only Haiku subagents (`model: haiku`) in parallel, one per group
     of about 5 sessions. Each returns its threads with the session id, a proposed tag from
     step 4 and the evidence lines. Never Opus.
   - Two transcripts disagree about one thread: one Sonnet subagent reads only that conflict.
   - Merge the threads yourself before step 3.
3. Check each thread against the live state: `git branch`, `git log`, `git worktree list` and
   the pull request list. The live state wins over a transcript.
4. Write the brief in the chat:
   - at most 5 bullets of context;
   - each thread with one tag: `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`,
     `[verified, uncommitted]`, `[reverted #N]` or `[planned, not started]`;
   - at most 5 recurring problems;
   - one next step.
5. Cite the session id for each thread, so I can open it. Never fill a gap from memory: say
   "not found".
