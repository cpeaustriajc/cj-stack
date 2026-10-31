# cj-stack

CJ's skills and mods for Claude Code.

- [Install](#install)
- [Skills](#skills): maintained skills, shipped in five plugins: Design, Engineering, Planning, Knowledge and Writing
- [Mods](#mods): hooks that change how a session behaves, one plugin each
- [Lab](#lab): in-progress skills in the `lab` plugin; they can change at any time
- [Models](models/README.md): which model does what, and why cross-vendor review stays
- [Scope](SCOPE.md): what cj-stack is, and the ideas it rejects with the reason for each
- [painting-craft: before and after](#painting-craft-before-and-after)

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install planning@cj-stack
/plugin install engineering@cj-stack
/plugin install design@cj-stack
/plugin install knowledge@cj-stack
/plugin install writing@cj-stack
/plugin install lab@cj-stack
/plugin install linear-gate@cj-stack
```

Install only the plugins you need. Add any mod the same way: `/plugin install <name>@cj-stack`.

| Plugin | What it is for | Skills |
|---|---|---|
| `design` | Sign off UI work — check spacing, type, colour and motion against the design, and paint scenes in code. | ui-polish, painting-craft |
| `engineering` | Prove the work in the real app — playbooks for bugs and features, careless-user QA, diff review and PRs. | playbooks, break-it, feature-files, interrogate, commit, create-pr |
| `planning` | Turn an idea into tickets — test if it is worth building, write the spec, cut thin slices in any tracker. | vision, shape, tickets, grill |
| `knowledge` | Keep what the team learns — a decision log, research pages, and lessons from your past sessions. | project-knowledge, hone |
| `writing` | Write docs people can read — repo rules first, plain ASD-STE100 sentences, and AI tells cut from any draft. | technical-writing, unslop |
| `lab` | Try in-progress skills early — they change without notice and have no eval proof yet. | all skills in [Lab](#lab) |

If you installed `cj-stack@cj-stack` or `cj-lab@cj-stack` before, those plugins no longer exist.
To remove them and install the plugins above, follow [Migrate from the cj-stack and cj-lab plugins](MIGRATING.md).

- While editing a mod, add the local clone instead (`/plugin marketplace add ~/Projects/cj-stack`):
  a directory marketplace hot-reloads.
- Other agents (Codex and anything that reads `~/.agents/skills`): `scripts/link-skills.sh`.

## Skills

All skills are model-invoked (Claude picks them from their description), except `commit`,
`technical-writing` and `unslop`, which run only when typed.

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

## Lab

In-progress skills live in `lab/`, and the `lab` plugin ships all of them. They can change at
any time and have no eval proof yet. Install them with `/plugin install lab@cj-stack`.

A skill loads as `/lab:<skill>`, for example `/lab:why`. Lab skills: [architect](lab/architect/README.md), [blast-radius](lab/blast-radius/README.md), [bro](lab/bro/README.md), [bug-hunt](lab/bug-hunt/README.md), [cleanup](lab/cleanup/README.md), [drive](lab/drive/README.md), [how](lab/how/README.md), [implement](lab/implement/README.md), [ketchup](lab/ketchup/README.md), [launch-video](lab/launch-video/README.md), [microinteraction](lab/microinteraction/README.md), [no-comments](lab/no-comments/README.md), [principle-attack-the-premise](lab/principle-attack-the-premise/README.md), [principle-boundary-discipline](lab/principle-boundary-discipline/README.md), [principle-build-the-lever](lab/principle-build-the-lever/README.md), [principle-exhaust-the-design-space](lab/principle-exhaust-the-design-space/README.md), [principle-experience-first](lab/principle-experience-first/README.md), [principle-explain-the-number](lab/principle-explain-the-number/README.md), [principle-fix-root-causes](lab/principle-fix-root-causes/README.md), [principle-foundational-thinking](lab/principle-foundational-thinking/README.md), [principle-laziness-protocol](lab/principle-laziness-protocol/README.md), [principle-make-operations-idempotent](lab/principle-make-operations-idempotent/README.md), [principle-minimize-reader-load](lab/principle-minimize-reader-load/README.md), [principle-model-the-domain](lab/principle-model-the-domain/README.md), [principle-outcome-oriented-execution](lab/principle-outcome-oriented-execution/README.md), [principle-prove-it-works](lab/principle-prove-it-works/README.md), [principle-redesign-from-first-principles](lab/principle-redesign-from-first-principles/README.md), [principle-separate-before-serializing-shared-state](lab/principle-separate-before-serializing-shared-state/README.md), [principle-sequence-verifiable-units](lab/principle-sequence-verifiable-units/README.md), [principle-subtract-before-you-add](lab/principle-subtract-before-you-add/README.md), [principle-test-behavior-not-implementation](lab/principle-test-behavior-not-implementation/README.md), [principle-type-system-discipline](lab/principle-type-system-discipline/README.md), [principles](lab/principles/README.md), [recall](lab/recall/README.md), [scout](lab/scout/README.md), [self-verify](lab/self-verify/README.md), [teach](lab/teach/README.md), [triage](lab/triage/README.md), [why](lab/why/README.md).

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
