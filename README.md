# cj-stack

CJ's skills and mods for Claude Code.

- [Install](#install)
- [Skills](#skills): skills shipped in six plugins: Design, Engineering, Planning, Knowledge, Writing and Principles
- [Mods](#mods): hooks that change how a session behaves, one plugin each
- [Models](models/README.md): which model does what, and why cross-vendor review stays
- [Scope](SCOPE.md): what cj-stack is, and the ideas it rejects with the reason for each
- [painting-craft: before and after](#painting-craft-before-and-after)

## Install

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install planning@cj-stack
/plugin install engineering@cj-stack
/plugin install design@cj-stack
/plugin install knowledge@cj-stack
/plugin install writing@cj-stack
/plugin install principles@cj-stack
/plugin install linear-gate@cj-stack
```

Install only the plugins you need. Add any mod the same way: `/plugin install <name>@cj-stack`.

| Plugin | What it is for | Skills |
|---|---|---|
| `design` | Sign off UI work and motion — check it against the design, add missing microinteractions, paint scenes in code, make launch videos. | ui-polish, painting-craft, microinteraction, launch-video |
| `engineering` | Prove the work in the real app — playbooks, design-first builds, unattended loops, bug hunts, code history, review and PRs. | playbooks, break-it, feature-files, interrogate, commit, create-pr, architect, implement, drive, bug-hunt, blast-radius, self-verify, no-comments, cleanup, how, why, teach |
| `planning` | Turn an idea into tickets — find and test ideas, write the spec, cut thin slices and triage them in any tracker. | vision, shape, tickets, grill, scout, triage |
| `knowledge` | Keep what the team learns — a decision log, research pages, lessons from past sessions, and a recap of recent work. | project-knowledge, hone, recall |
| `writing` | Write so people can read — docs in plain ASD-STE100, AI tells cut, and plain re-pitches and catch-ups in chat. | technical-writing, unslop, bro, ketchup |
| `principles` | Apply engineering principles by name — prove it works, subtract before you add, attack the premise, and 17 more. | principles, and the 20 `principle-*` skills it indexes |

If you installed `cj-stack@cj-stack` or `cj-lab@cj-stack` before, those plugins no longer exist.
To remove them and install the plugins above, follow [Migrate from the cj-stack and cj-lab plugins](MIGRATING.md).

- While editing a mod, add the local clone instead (`/plugin marketplace add ~/Projects/cj-stack`):
  a directory marketplace hot-reloads.
- Other agents (Codex and anything that reads `~/.agents/skills`): `scripts/link-skills.sh`.

## Skills

Most skills are model-invoked: Claude picks them from their description. A skill marked
"typed" runs only when you type its slash command. All 20 `principle-*` skills are typed.

| Skill | Plugin | What it is for |
|---|---|---|
| [vision](plugins/planning/skills/vision/README.md) | planning | grilling me on a vague product idea, breadth first and starting with whether it is worth building, then writing it as the top of the plan: destination, features that become projects, not yet specified, out of scope, risk-first order |
| [shape](plugins/planning/skills/shape/README.md) | planning | one project in any tracker (Linear, Jira, GitHub, others): a spec with numbered requirements, milestones, project descriptions and updates; owns the tracker adapters and the plan-tree check |
| [tickets](plugins/planning/skills/tickets/README.md) | planning | cutting a confirmed spec into thin, demoable work items that each cite the requirements they meet |
| [grill](plugins/planning/skills/grill/README.md) | planning | sizing an idea or change, then interviewing me in short rounds of questions, each with a recommended answer, until a plan or idea has no open decisions |
| [project-knowledge](plugins/knowledge/skills/project-knowledge/README.md) | knowledge | a decision log and research pages in the team's wiki, Notion, Linear, Obsidian or Confluence |
| [hone](plugins/knowledge/skills/hone/README.md) | knowledge | mining past transcripts for my repeated corrections and the failures nobody corrected, or one skill's with `/hone <skill>`, and proposing where each lesson should live or what to prune: code, lint, hook, test, skill or instruction file |
| [playbooks](plugins/engineering/skills/playbooks/README.md) | engineering | bug, refactor, performance, feature, prototype and design playbooks that each carry their own proof (a reproduced bug, pinned behaviour, a baseline, two compared sketches) |
| [break-it](plugins/engineering/skills/break-it/README.md) | engineering | driving the app as careless, impatient or confused users and worst-case data, then reporting ranked bugs with video and repro steps |
| [ui-polish](plugins/design/skills/ui-polish/README.md) | design | reviewing a UI and its motion against the design and a list of common mistakes, as a Before/After/Why table |
| [feature-files](plugins/engineering/skills/feature-files/README.md) | engineering | one short file per feature saying how to reach, drive and check it, so E2E checks read only what they need |
| [interrogate](plugins/engineering/skills/interrogate/README.md) | engineering | reviewing a diff with fresh Claude reviewers that each see a different slice of it, then filtering into act on, consider, noted and dismissed |
| [commit](plugins/engineering/skills/commit/README.md) | engineering | typed `/commit`: small commits in the repo's style, then push (the desktop Commit and push button) |
| [create-pr](plugins/engineering/skills/create-pr/README.md) | engineering | `/create-pr [draft]` or "open the PR": commit, check, push and open a PR linking the issue and evidence (the desktop Create PR button) |
| [painting-craft](plugins/design/skills/painting-craft/README.md) | design | drawing and painting in code to a gallery standard, with a screenshot review loop |
| [technical-writing](plugins/writing/skills/technical-writing/README.md) | writing | typed `/technical-writing`: a doc, README, spec, PR body or commit message written or reviewed by the repo's own rules first, then ASD-STE100 sentences |
| [unslop](plugins/writing/skills/unslop/README.md) | writing | typed `/unslop` with text: the same text back without the common tells of AI-written prose |
| [scout](plugins/planning/skills/scout/README.md) | planning | finding an idea worth building, or checking a niche, when apps are cheap to copy |
| [triage](plugins/planning/skills/triage/README.md) | planning | setting one state on an issue ("what needs my attention", "can an agent take this") and writing an agent brief |
| [recall](plugins/knowledge/skills/recall/README.md) | knowledge | "where was I": a brief of recent work from transcripts, git and PRs |
| [architect](plugins/engineering/skills/architect/README.md) | engineering | typed `/architect`: sketch types, signatures and module structure before code, then stay in the loop while the build fills in |
| [implement](plugins/engineering/skills/implement/README.md) | engineering | typed `/implement` with a ticket: build one ready ticket without supervision, with the feature playbook and a review |
| [drive](plugins/engineering/skills/drive/README.md) | engineering | "loop until it passes" or "run it overnight": decide the stop condition, then drive the work until it holds |
| [bug-hunt](plugins/engineering/skills/bug-hunt/README.md) | engineering | hunting bugs across a codebase in rounds, each fixed test-first, until a round comes back clean |
| [blast-radius](plugins/engineering/skills/blast-radius/README.md) | engineering | typed `/blast-radius`: find what a change could break outside its diff, and prove the fact that makes it safe |
| [self-verify](plugins/engineering/skills/self-verify/README.md) | engineering | setting up and auditing a repo's verify skill, so agents prove "done" with a verdict per PR |
| [no-comments](plugins/engineering/skills/no-comments/README.md) | engineering | typed `/no-comments` with a folder: remove stale comments and suppressions as separate commits with the same test results |
| [cleanup](plugins/engineering/skills/cleanup/README.md) | engineering | removing what a session left behind (dev servers, stale branches, the session) once it is safe; not code tidying |
| [how](plugins/engineering/skills/how/README.md) | engineering | typed `/how`: how a part of the code works, and where a new piece should live |
| [why](plugins/engineering/skills/why/README.md) | engineering | why code is like this, where a number came from, or if a guard can go, from git, PRs and docs with labelled evidence |
| [teach](plugins/engineering/skills/teach/README.md) | engineering | typed `/teach`: one plain explanation of a body of work, from `how` and `why` |
| [microinteraction](plugins/design/skills/microinteraction/README.md) | design | typed `/microinteraction` with a UI area: find the places that should animate and play each proposal before you pick |
| [launch-video](plugins/design/skills/launch-video/README.md) | design | a trailer, promo, short, voiceover, thumbnails or captions for a launch |
| [bro](plugins/writing/skills/bro/README.md) | writing | typed `/bro`: re-pitch the last message in plain words, with the missing context first and one picture |
| [ketchup](plugins/writing/skills/ketchup/README.md) | writing | typed `/ketchup`: what changed in this chat since your last message, with the calls you need to make |
| [principles](plugins/principles/skills/principles/README.md) | principles | naming an engineering principle, or a design, test, debug or measurement decision: picks the rule that applies from the 20 `principle-*` skills |

Shipped skills stay tool-neutral:
tool specifics go in a skill's adapters, and a project's own facts stay in that project.

## Mods

| Mod | What it does | Install |
|---|---|---|
| [linear-gate](mods/linear-gate/README.md) | blocks Linear writes off shift; on shift, asks only before a delete or cancel | by default |
| [session-modes](mods/session-modes/README.md) | `/mode readonly`, `research`, `prototype`, `build` or `off`, enforced for the session | optional |
| [hone-nudge](mods/hone-nudge/README.md) | suggests `/hone <skill>` when you corrected Claude during a cj-stack skill run | optional |
| [memory-lint](mods/memory-lint/README.md) | denies an auto-memory write holding task state or anything short-lived (dates, branches, plan or /tmp paths), PR or commit references, file:line pointers or code, or an oversized entry; pruning always passes | optional |
| [work-folder](mods/work-folder/README.md) | denies a new agent working file (plan, evidence, prototype, scratch, report, probe test) outside `.claude/work/`, with a per-repo allow list, and removes `.claude/work/` entries not changed for a day | optional |
| [test-guard](mods/test-guard/README.md) | denies an Edit or Write that changes or removes a line a test file has at `HEAD`; additions pass, `/test-guard allow <path>` lets one file change | optional |

## painting-craft: before and after

The same two prompts, each run once in a fresh session: the original skill on the left, the current
painting-craft on the right. Nothing was touched up by hand.

**"Paint a 1600x1000 SVG of a knight asleep against an oak tree at dusk, in a Romantic oil-painting look."**

![Knight at dusk, full picture: before and after](docs/images/knight-full.jpg)

At 2× zoom, where the viewer looks. The knight is a 3D figure lit by the low sun, with separate
plates, mail in rows and a visor, instead of a mannequin of tubes:

![Knight at dusk, 2x crop: before and after](docs/images/knight-zoom.jpg)

**"Draw a night city street as a 1600x1000 SVG: a car passes behind a row of trees on the near verge.
Flat vector style, but it must not look cheap."**

![Night street, full picture: before and after](docs/images/street-full.jpg)

At 2× zoom, a crown is clumps hung on a branch skeleton, in three values with broken edges, instead
of a pile of round blobs:

![Night street, 2x crop of a tree: before and after](docs/images/street-zoom.jpg)

What changed: build recipes for the parts that fail up close (`references/recipes.md`), studies of
each hero element against fetched public-domain references before composing (`scripts/refs.py`,
`scripts/compare.py`), the bundled 3D figure renderer, a paint pass that unifies painted styles
(`scripts/paintpass.py`), and delivery at twice the display size.
