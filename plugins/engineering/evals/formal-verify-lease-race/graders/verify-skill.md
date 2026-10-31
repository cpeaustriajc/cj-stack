---
type: llm
---

The run wrote a project skill file (a `SKILL.md` with frontmatter, anywhere in the fixture repo: the
eval sandbox can block writes under `.claude/`) that gives one command to run the check, names the
covered code (`runner/lease.py` and its functions), and records a commit as the sync point. The
reply or the transcript shows that this command ran on the current code and reported the
two-holder bug as a failure or as a recorded finding. A skill that only describes the bug in prose,
with no runnable check, fails.
