# Global Guidance
- Write to me in ASD-STE100: chats, technical documents, and rules for models.
- Refer to a section of a document by its title; a section number changes when the document
  changes.
## Check facts at the source
- Before you state or use something that can change, or that can be newer than your training
  data (a package version, an API, what is installed, configured, tracked or decided), check
  the source now. Otherwise call it a guess, or ask me.
- A CI run that fails in seconds with no steps did not run the code: read its annotations
  before you change any code.
## Asking questions
- Every question to me carries a concrete example: a specific person, input or situation, and
  what each answer would make happen in it.
- Do what your own tools can do. Ask me only for a sign-in, a secret, or a call of taste or
  business; after my go, do every step I named without a new ask.
- My answer, picked or typed, is final. Never ask the same question again in new words.
- A choice or an explanation of a layout, UI state, flow or account state comes with a rendered
  picture. ASCII art and a text table of options are not pictures.
- A draft I must read or approve goes in the chat, not in a file.
## Scope
- Change only what was asked; report other problems you see instead of fixing them.
- A fix that grows far past the size it was asked as, such as a one-line fix past about 100
  lines, is a new decision: stop and confirm.
- My own working files (plans, notes, research, prototypes, probes) go in
  `.claude/work/<topic>/`, never in tracked folders; add `.claude/work/` to `.gitignore` if it
  is missing.
## Facts about my setup
- Before stating what's installed, configured, tracked, deprecated or decided (an MCP, a deploy,
  a tracked folder, a package type), check the source now: the code, upstream main, git log and
  PRs, the tracker, the vendor's docs, the live system. Otherwise call it a guess, or ask me.
- CI fails in seconds with no steps: read the annotations; a billing block needs no code fix.
## Instruction files
- Memory and instruction files hold rules, preferences and pointers to sources, never a
  decision, finding or status: those go stale without anyone noticing. Fix or delete a wrong
  line; never add a newer one beside it.
- Every line must pass one test: would Claude make a mistake without it? Otherwise cut it.
- Put knowledge where it loads only when needed: a rule scoped to the files it is about, a
  procedure in a skill. An import still loads in full.
- A rule that a check can enforce becomes the check; the file keeps a pointer.
- A custom agent loads only the instructions its job needs (`omitClaudeMd: true` when it needs
  none of the project's).
- Source: https://code.claude.com/docs/en/memory and /best-practices.
## Testing
- Prove a feature by driving the real app the way a user does; prefer these tests as the only
  tests.
- A test run I rely on leaves the exact command and its evidence where another person can run
  it again and check it; say where.
- Unit-test a part only when it must be tested alone, and only test first: a case for every way
  it can fail, before the code.
- A project's own test policy wins over this section.
## Before and after
- Every PR and issue for a change that a user, QA or a caller can observe carries a before and
  an after of the same state, made with the same steps on the base branch and on the change.
  Use the form that shows the change best: a cropped screenshot, a recording for a flow or a
  timing, or command output, a response or a measurement when there is nothing to see.
- Evidence shows only the change, at a pace a person can follow.
## Workflow
- Commit each finished slice as soon as its check passes, without asking, unless the project
  needs a sign-off first. This overrides the default "commit only when asked".
- When a build keeps failing review, start it again fresh with what is left of the spec; do not
  patch it.
## Error Handling
The project's own error handling sets the style; where it has none, ask before the first
handler. No style loosens these:
- Every error, also one that no caller waits for, reaches a handler that acts on it or goes up
  to the caller. A log alone is not handling.
- An error that goes up keeps the error that caused it.
- Retry only an error known to be temporary, with growing random delays and a limit.
- A log goes where the platform collects it and survives the crash it describes.
- A guard without a test that fails when it is removed is a guess.
## Code review
- Give the reviewer what the change is for, not only the change. Failure: reviewers that saw only
  the change missed a bug that broke its purpose.
- Who counts as a user comes from the project, never from the review request. Failure: a request
  that widened "user" turned almost every finding into an input no user gives.
- Ask for every finding, then filter by user impact. Failure: a model told to hold back reports
  less, not better (the vendor's prompting guide).
- Review loops between the author and a reviewer who knows the purpose, not the work or its
  history. Failure: a reviewer read the later fix commits, so its review proved nothing.
- Prove a finding on the user's path where you can, not only by reading. Failure: bugs that show
  only at run time were missed in every review that only read the code.
- Report a bug kind once, with its instances. Failure: later rounds found mostly old kinds.
- Stop when a pass finds nothing a user would hit; if findings keep coming, question the design.
  Failure: real findings dried up while variants grew, until a cap stopped the loop.
- Rank findings and reviewers by impact, not count: one bug a user hits outranks many that no
  user hits.
- Reviewers with different blind spots find more than one reviewer run twice. Failure: two
  dissimilar reviewers found more real bugs than two similar ones.
## Long commands
- A command that can run longer than a few seconds shows progress while it runs and keeps its
  full log. On start, say what runs, about how long it takes and where the log is.
## Delegation
The session I talk to plans, writes specs, starts threads and reviews their work; a thread does
the building. Failure: a ticket built in the main session instead of a thread.
- A thread shares my checkout unless another thread edits the same repo. Small fixes for one
  repo go to one thread.
- Push and open a thread's PR without asking me.
- The build tickets of one project ship as one PR stack in blocked-by order, each branching off
  the previous one; other items branch off main. A restack costs more than the build.
- New work goes to a fresh thread, not an idle one: an idle thread rereads its whole history.
- Before parallel attempts at one task, say how the winner is picked.
- Subagents read, research and review; they write no code and ask no question. They run on a
  cheaper model than mine (a skill may name an exception); raise effort when one misreads or
  loops.
- A subagent result without its evidence gets one more try; a second miss is a gap, never a
  pass.
## Claude config is shared through chezmoi
- `~/.claude` is shared through chezmoi with a Windows machine. After you change a shared
  file, `chezmoi re-add` it and commit in the dotfiles repo; push only when I ask. For
  `settings.json`, run the source's `.settings-capture.sh` instead; keys in
  `.settings-deny.json` stay on this machine.
- Share a new config file with `chezmoi add`; never machine state (transcripts, `projects/`,
  `plugins/`, `.claude.json`, caches, backups).
- Shared files work on macOS and under Git Bash on Windows; paths start with `~`.
- `chezmoi diff` before `chezmoi apply`: Claude Code rewrites `settings.json` itself, and an
  apply reverts that without a warning.
