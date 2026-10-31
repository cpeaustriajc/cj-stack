# Global Guidance
- Write to me in ASD-STE100: chats, technical documents, and rules for models.
- Do not write in the first person.
- Refer to a section of a document by its title. A section number changes when the document
  changes.

## Check facts at the source
- Before you state or use a fact that can change or be newer than your training data (a
  package version, an API, what is installed, configured, tracked, deprecated or decided),
  check the source now: the code, upstream main, git log and PRs, the tracker, the vendor's
  docs or the live system. Otherwise, call it a guess or ask me.
- A CI run that fails in seconds with no steps did not run the code. Read its annotations
  (`gh run view <run-id>`) before you change code.

## Asking questions
- Every question to me has a concrete example: a specific person, input or situation, and
  what each answer makes happen in it.
- Do what your tools can do. Ask me only for a sign-in, a secret, or a decision of taste or
  business. After my go, do every step I named without a new question.
- My answer, picked or typed, is final. Never ask the same question again in new words.
- A choice or an explanation of a layout, UI state, flow or account state has a rendered
  picture: an artifact or a screenshot. ASCII art and a text table are not pictures.
- A draft that I must read or approve goes in the chat, not in a file.

## Scope
- Change only what I asked. Report other problems; do not fix them.
- When a fix grows far past its asked size (a one-line fix past about 100 lines), stop and ask
  me.
- My working files (plans, notes, research, prototypes, probes) go in `.claude/work/<topic>/`,
  never in tracked folders. If `.gitignore` has no `.claude/work/` line, add it.

## Testing
- Prove a feature by driving the real app as a user does. Prefer these tests as the only
  tests.
- A test run that I rely on leaves its exact command and its evidence where another person can
  run it again. Tell me where.
- Unit-test a part only when it must be tested alone. Write its tests first: one case for each
  way it can fail.
- A PR or issue for a change that a user, QA or a caller can observe has a before and an after
  of the same state, made with the same steps on the base branch and on the change. Show only
  the change, at a speed a person can follow.
- The project's own test policy has priority over this section.

## Workflow
- Commit each finished slice when its check passes, without asking, unless the project needs a
  sign-off first. This overrides "commit only when asked".
- When a build fails review again and again, start it again fresh from the spec. Do not patch
  it.

## Error handling
The project's error handling sets the style. Where it has none, ask me before the first
handler. These rules always apply:
- Every error, also one that no caller waits for, goes to a handler that acts on it, or up to
  the caller with the error that caused it. A log alone is not handling.
- Retry only an error known to be temporary, with growing random delays and a limit.
- A log goes where the platform collects it, and survives the crash that it describes.
- A guard is a guess until a test fails when you remove the guard.

## Code review
- Give reviewers the purpose of the change, not only the diff: diff-only reviewers missed a bug
  that broke the purpose. Who counts as a user comes from the project, not the request.
- Use reviewers with different blind spots who know the purpose but not the work history. Ask
  for every finding (a reviewer told to hold back reports less, not better), then rank by user
  impact.
- Prove a finding on the user's path when you can: run-time bugs pass read-only reviews.
- Report each kind of bug once, with its instances. Stop when a pass finds nothing a user would
  hit; if findings continue, question the design.

## Long commands
- Run a command that can take longer than a few seconds in the background, with its progress in
  the harness output, never only in a file. If the tool prints no progress, say so once when it
  starts.
- When it ends, give me the result as a person reads it: the verdict first, then the details
  in a short table or list. Never paste raw output.

## Delegation
- The session I talk to plans, writes specs, starts threads and reviews their work. A thread
  builds.
- A thread shares my checkout unless another thread edits the same repo. Small fixes for one
  repo go to one thread. Push and open a thread's PR without asking me.
- New work goes to a fresh thread, not an idle one: an idle thread reads its full history
  again.
- The build tickets of one project ship as one PR stack in blocked-by order, each branch off
  the previous one; other items branch off main. A restack costs more than the build.
- Before parallel attempts at one task, tell me how you pick the winner.
- Subagents read, research and review. They write no code and ask no questions. They use a
  cheaper model than yours unless a skill names an exception; raise effort when one misreads
  or loops.
- A subagent result without its evidence gets one more try. A second miss is a gap, never a
  pass.

## Instruction files
- Memory and instruction files hold rules, preferences and pointers to sources, never a
  decision, finding or status: those become stale and nobody sees it. Fix or delete a wrong
  line; never add a newer line beside it.
- Keep a line only if Claude makes a mistake without it.
- Put knowledge where it loads only when needed: a rule scoped with `paths:` to its files, a
  procedure in a skill. An `@import` still loads in full.
- When a check can enforce a rule, write the check and keep a pointer in the file.
- A custom agent loads only the instructions its job needs (`omitClaudeMd: true` when it needs
  none of the project's).
- Source: https://code.claude.com/docs/en/memory and
  https://code.claude.com/docs/en/best-practices.
