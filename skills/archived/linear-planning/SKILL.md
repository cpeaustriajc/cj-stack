---
name: linear-planning
description: Shaping work in Linear — where a spec, feature, story, acceptance criterion, dependency or risk lands (initiative, project, spec document, phase milestone, issue), and who owns each level. Use before creating or restructuring any Linear project, milestone or issue, when a PO spec arrives as one large ticket, and when the CEO redirects a project.
---

# Linear planning — containers, work types, ownership

Project-specific facts live in the project, not here: who holds the PO, CEO and
QA roles, where older specs live, and any ownership record. Look for
`.agents/references/linear.md` (or the project's AGENTS.md / CLAUDE.md Linear section) and read it first. If a project has none, ask; on a
solo project the lead developer holds the PO role.

Linear has one work item: the **Issue**. There is no Story, Feature or Epic type.
Jira Story = Linear Issue. Jira Epic = Linear Project. Jira Epic description or
Confluence PRD = the project's spec Document. Never file a spec as an issue and
never title a project "Epic 1".

The CEO redirects direction through the PO, often after seeing a demo. Structure
therefore follows confirmation: a spec stays one Document until the CEO confirms
it, and issues are split from it one slice at a time. A redirect edits the
Document and costs nothing else.

## Who owns which level

| Level | Object | Owner | Holds |
| --- | --- | --- | --- |
| Vision | Initiative | PO | Product goal, business and customer value. Projects link to it; do not repeat per project. |
| Feature | Project | PO writes intent, engineering writes the template | Why, What, How, Not in scope, Success, Risks. One project per tool or feature. |
| Internal tool | Project from the `Internal Tool` template | Engineering writes it, checked with the main user | A project whose users are the team (QA, PO, engineering), not buyers. Why, What, How, Not in scope, Success. No Product spec and no Demo (see Internal tool projects). |
| Spec | Project Document titled `<Project> — Product spec` | PO writes, engineering formats | Intent, flows and acceptance criteria as statements, verbatim, no checkboxes, no dates. Status line at the top: Draft or Confirmed (date, by whom). Version history keeps every direction the CEO rejected. |
| Cross-team change | Project Document `Proposal: <Title>` | Engineering, accepted by the other team | A change another team must accept. Draft, Agreed, Shipped. Once Agreed, its interface moves into an API contract. |
| Interface | Project Document `<Project> — API contract` | Builder and consumer | What one side builds and the other consumes: endpoint, parameters, response, fields, errors, limits. |
| Mechanism | Project Document `<Project> — Technical design` | Engineering | Work inside one codebase: architecture, data rules, open technical questions. The PO does not need to read it. |
| Decision | Project Document titled `Decision: <Topic>`, from the `Decision` template | Engineering or PO, whoever decided | One decision, filed in the project it belongs to; a team-wide one is a Team Document. No number and no index: its first line (`Status · Kind · Decided by · Date`) is what a search for "Decided by" finds. |
| Phase | Milestone | Engineering | One of the fixed phases below: four for `Product Outcome`, three for `Internal Tool`. No description: the name says it all, and the exit check lives here. |
| Story | Issue | Engineering, PO approves AC | Plain task title, `Task` template body. Done When quotes the spec statements it satisfies plus finer conditions QA needs. |
| Done | Issue status | QA | QA marks Done. Only a defect against the quoted statements reopens. New asks are new issues. A `No QA` issue (`Chore` template) is closed by engineering after Code Review. |
| Accepted | Launch exit check | PO | PO checks the released feature against the spec's statements. This is the acceptance step; the progress bar is not. |
| Older specs, audit answers | Project Resource (wherever the project reference says they live) | PO | Existing specs stay where the PO's comment threads are. New specs are Documents. |
| Team-wide decisions | `Decision: <Topic>` Team Documents | Whoever decided | Decisions every project relies on, one document each. Link the specific decision; never keep a list of them. |

## Rules

- **Acceptance criteria are statements, not tasks.** They describe what the user
  sees and does. They never name a data source, vendor, endpoint, model or timing
  budget. Mechanism goes in the project How (one line) and the engineering
  Document (the detail). If a PO statement names a mechanism,
  the issue quotes the outcome half and links the team-wide decision behind it.
- **Initiative and project descriptions use a neutral tense.** Present simple,
  describing what the product does and why ("Users save items to a shortlist"),
  never future ("will let users"), past ("was moved", "we added") or in-progress
  ("is being built"). Change over time belongs in status updates.
- **Milestones carry no target date** unless the CEO asks, and then only Launch.
  Dates on every phase turn the project into a waterfall.
- **The spec is intent, not build instructions.** Agents build from issues only.
  A Draft spec never has issues split from it.
- **Convert, never cancel.** A PO spec filed as an issue moves into the spec
  Document; the issue goes back to Backlog or becomes the first Implementation
  slice. Cancelling removes it from Definition of Ready and reads as a verdict.
- **Feasibility gate.** No issue enters Ready To Pull Out until engineering confirms
  it names only systems the team owns or has a signed contract for. Probe the
  upstream endpoint first; the answer usually dissolves the dependency line.
- **Labels, not issues, split frontend from backend** unless the halves ship
  separately. Sub-issues hold tasks under a story that exceeds one cycle.
- **Bugs after Done** are new issues labelled Bug, related to the original. Do not
  reopen.
- **Templates.** Project template `Product Outcome` for every project a buyer will
  see, and `Internal Tool` for one only the team uses: a test harness, a mock of
  another team's system, a QA panel, a devtool. If buyers ever see the result, it
  is `Product Outcome`, even when the team uses it first. Issue
  templates `Task`, `Bug` and `Chore`. Do not use the `Epic` project template; the word pulls
  Jira habits back.
- **Every issue body is the `Task` template** (below), including issues under a
  milestone. Engineering work with no change a user can see uses `Chore`: the same
  four headings plus its No QA Check, and the `No QA` label. A refactor is a `Chore`
  only when automated tests prove behaviour is unchanged and it touches none of
  sign-in, cart, checkout, routes or `data-testid`s. No story line, no Functional
  Testing Requirements, no test-category sections: those are the retired Jira format.

## Project Documents

A project has the Product spec plus **one** engineering Document at a time,
split by reader:

- **Product spec** — for the PO. What the user sees and does. It never names an
  endpoint, field, vendor or data source, because the PO reads it to confirm
  intent and mechanism detail buries that.
- **One engineering Document**, whichever fits the work:
  - **Proposal** — a change another team must accept. Once Agreed, its
    interface moves into an API contract, which replaces it.
  - **API contract** — an interface one side builds and another consumes, so
    both can build in parallel.
  - **Technical design** — work that stays inside one codebase.

Decisions do not count toward that limit. File each one in the project it
belongs to, titled `Decision: <Topic>` with the topic as a plain statement
("Decision: Make Offer hidden") and no number. There is no decisions index to
maintain: the Documents tab groups decisions by project, and a title search for
"Decision:" or a search for "Decided by" lists them all. Superseding changes only
the old decision's Status line to `Superseded by <link>`.

Do not call any of them "tech spec" or "PRD": "spec" means the product side
only. Small projects with no interface to agree skip the engineering Document;
the project How carries the mechanism.

The templates live in Linear, as team templates. Start each Document from its
Linear template: `<Project> — Product spec`, `Proposal: <Title>`,
`<Project> — API contract`, `<Project> — Technical design` and
`Decision`. The project body starts from the `Product Outcome` or `Internal Tool`
project template, whose How links the API contract or Technical design. Read the
current template text in Linear before writing; do not copy it into files.

## Task template

Use this shape even where the team's Linear `Task` template still shows bold
headings or no checkboxes.

```markdown
## Context

<Why this exists now, the evidence, and the links that stop someone rediscovering it.>

## Outcome

<The concrete state that is true when this is done. One sentence.>

## Done When

- [ ] <One observable check. Behaviour someone can see, not test steps.>

## Out of Scope

- <Only the boundaries that prevent a likely misunderstanding. Omit the section if none.>
```

Length limits:

- Context: 2–4 sentences plus links. Probe data and architecture go in the PR or
  the project's engineering Document, not here; link it.
- Outcome: one sentence.
- Done When: 3–5 `- [ ]` checkboxes, one check each, never plain bullets. An
  Implementation issue quotes the spec statements it satisfies here. No click-by-click steps, no
  "record only" measurements, no "deliberately absent" lists.
- Out of Scope: 0–3 plain `- ` bullets.
- Whole body: under ~1,500 characters. Longer means the issue is two issues.
- **Drop the "As a … I want … so that" line** unless the PO wants it for readability.
  Keep her AC. The persona sentence is where mechanism and timing tend to sneak in.

## Phase milestones

Every `Product Outcome` project gets these four milestones, in this order, and no
others (`Internal Tool` projects: see the next section). Leave
the milestone description empty; the same text repeated on every project is noise.

| Milestone | Holds | Exit check | Decides |
| --- | --- | --- | --- |
| Demo | The spec Document in Draft, plus throwaway mockup or prototype issues. No build issues. | An approval issue assigned to the PO ("CEO approves the <spec> after the PO's demo") is Done, and the PO marks the spec Confirmed. | CEO through PO |
| Implementation | Issues split from the Confirmed spec, the next slice only. | QA marked every issue Done. | QA |
| Launch | Production release, release note, QA on production. | PO accepts the release against the spec's statements. | PO |
| Post Launch | Bugs and small follow-ups to what shipped. | Two cycles after Launch the project completes. New ideas start a new spec. | Engineering |

- **Demo is time-boxed to one cycle.** A demo still unconfirmed after that goes
  back to the PO as a question, not a second demo. Demo work is throwaway, never
  the start of production code.
- **A CEO redirect** during Demo edits the spec Document and closes the mockup
  issues. After Demo it moves the project back to Demo: the spec returns to
  Draft, unstarted Implementation issues go to Backlog, and only the slice in
  progress is lost.
- **Post Launch is not a parking lot.** Anything that is not a fix to what
  shipped is a new spec.

## Internal tool projects

An `Internal Tool` project gets three milestones, in this order, and no others.
There is no Demo: no CEO decision gates a tool only the team uses. There is no
Product spec either: the project What and the issues' Done When are enough.

| Milestone | Holds | Exit check | Decides |
| --- | --- | --- | --- |
| Implementation | Build issues, plus a mockup on the first issue when the tool has a screen. | QA marked every issue Done (`Chore` issues: engineering after Code Review). | QA |
| Launch | The tool live where the team uses it, and a release note on how to use it. | The main user confirms in a comment that they can do the job named in Success. | Main user |
| Post Launch | Bugs and small follow-ups to what shipped. | Two cycles after Launch the project completes. New asks start a new project. | Engineering |

- **Visual sign-off is not a milestone.** A mockup is approved on its issue,
  before the build starts, by whoever owns visual calls on the team.
- **A tool that stands in for another team's system** says in its How whose
  behaviour it copies and where it deliberately differs, and links the
  `Decision` that allowed each difference.
- **Shared state is stated.** The How says whether one person's use affects
  anyone else's, because testers share these tools.

## Mapping a PO spec

| Spec section | Destination |
| --- | --- |
| Product goal, business value, customer value | Initiative (already there) |
| Epic / objective | Project Why and What |
| Feature 1, Feature 2 | Spec Document sections, one outcome sentence each |
| User story N | Implementation issue, once the spec is Confirmed |
| Acceptance criteria | Spec Document (PO's), quoted into issues |
| Acceptance considerations: UI behaviour, ordering | Issue AC |
| Acceptance considerations: performance | Project How |
| Dependencies on upstream | Project How; on other work, issue relation "blocked by" |
| Assumptions | Project Not in scope, or a team-wide decision |
| Risks | Project Risks line, only those that change the build |
| Example values from the spec | QA example under the issue, generalised |
| Anything naming infra, vendor API, endpoint, sub-second | The engineering Document (API contract or Technical design), or a team-wide decision when it applies to every project; not carried into issues |

## Ownership record

If the project reference records who owns final decisions on stories, anchor
structure disputes on it, in refinement, not in issue comment threads.
