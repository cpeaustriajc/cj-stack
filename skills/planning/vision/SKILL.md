---
name: vision
description: >
  Grill me on a vague product idea, starting with whether it is worth building and worth my time,
  until it is sharp; then write it as the top level of the plan in the team's tracker: the destination, the features that become projects, what is not yet
  specified and what is out of scope, ordered so the riskiest unknown is built first. Then hand
  each feature to `shape`, one at a time. Use when I bring a product idea or a vision, say "grill
  me on this idea", "plan the product", "set up the initiative" or "what are the features", or ask
  for a product plan from features down to tickets; when something I built for myself might be
  worth selling; and for a product-level status update or audit.
---

# Vision

The top of three levels: `vision` for the product, `shape` for each project, `tickets` for each
slice. Read the five top-down rules in `../shape/SKILL.md` first; they hold here too. The tracker
adapters live there as well: find the tracker as its section 1 says, and use the adapter's
**Product** row and its status-update row for a product update.

## 1. Grill me

A product idea is the vaguest thing in the plan, so this skill does the grilling itself. An idea
handed over from `scout` arrives with its evidence; start the ledger from it. Run the
interview from `../triage/SKILL.md`, from **Grilling** to **Ending**: the ledger, the rounds, the
recommended answers, the lookups. Skip its sizing: a product idea is always grilled. What changes
at this level:

- **Breadth first.** Round 1 fans out across the whole idea, one question per branch, before going
  deep on any: who it is for, their problem today, whether it is worth building (below), the
  destination, how we will know it worked, the first version's cut, and the riskiest unknown. Deep questions wait until every branch has a
  first answer.
- **The tree is the product.** Every settled branch becomes a line in section 2: a feature, a
  Success measure, an Out of scope item or the Sequence. Show the Features list growing in the
  ledger each round, numbered F1…Fn.
- **Vague is allowed to stay vague.** When I can't answer sharply and no lookup or prototype
  would settle it, don't press: put it under Not yet specified, say so in the ledger, and move on.
  Pressing a vague answer into a feature invents one.
- **Make it concrete to sharpen it.** Ask through one specific person in one specific moment ("Ana
  runs a small shop and her domain lapses on Friday night. What does she do first?"). Offer a
  rough sketch, a mock landing page headline or a one-screen flow, as an option when words are
  not landing.
- **Is it worth building, and worth my time?** Settle this before the features, because every
  later answer depends on it. Look up what you can before asking:
  - **Real**: who has the problem today, how often, and what they do about it now. A workaround
    people already pay for or put up with is evidence; "it would be nice" is not.
  - **Not already solved**: the existing products, tools or a spreadsheet that do this. Look them
    up; say what this would do that they don't, or recommend using one instead.
  - **What it costs**: my time to the first usable version, in weeks, and what it costs to keep
    running and maintain after. Estimates are mine to give; label yours as guesses.
  - **Reach and copies**: how I reach the people who pay, and what a copy built with an agent in
    a weekend could not take: distribution I own, data that accrues per customer, a workflow it
    sits in, trust or compliance. If a copy with an audience would win, say so.
  - **What it displaces**: what else that time would go to. Ask me which matters more.
  - **What it returns**: money, time saved, learning, or joy. Any of these can be enough, but say
    which one this is.

  **Personal software**, built for me alone, changes the questions. Ask in round 1 who it is for
  if it isn't plain. For me:
  - **Real**: how often I hit the problem and the minutes it costs each time. Five minutes a day
    is about 30 hours a year: the budget the build has to beat, when time saved is the point.
  - **Not already solved**: a tool that is 80% there with some setup, a script or a spreadsheet.
    An option to price against building, not a reason to stop.
  - **What it costs**: evenings and weekends, plus upkeep when an API or the OS changes.
  - **What it returns**: time saved, learning or joy. When it is learning or joy the time math
    doesn't apply, but the build gets a timebox ("two weekends"), and its end is a keep-going or
    stop decision, not a drift.

  Then recommend one verdict, with the reason in a line: **build**, **shrink** (a smaller first
  version is worth it and the whole is not yet), **test first** (one cheap check, a landing page,
  five conversations or a prototype, decides it), or **don't build**. Don't build and test first
  are good outcomes; say them plainly when the evidence points there, and stop the interview on
  don't build.
- **The riskiest unknown gets a test, not an opinion.** If it can be settled by a lookup, a
  prototype or talking to a user, name that as the first item of the first project rather than
  deciding it in the interview.

The interview ends when the frontier is empty: every branch is settled, out of scope, or under
Not yet specified. Then post the ledger as the draft product and ask whether it is right before
writing anything.

## 2. Write the product

The product's description, in the tracker object the adapter names for the Product level:

```markdown
Status: Draft | Confirmed (<date>, <approver>)

## Destination

<Who it is for, the problem it solves for them, and what the product is once it exists. Neutral
present tense: "Buyers find and buy a domain in one visit".>

## Worth it

<Verdict (build, shrink or test first) and why: the problem's evidence, what exists already, the
cost to a first version and to keep running, what it displaces, and what it returns.>

## Success

<One or two observations or measures that say it worked.>

## Features

F1. <Outcome in one line.> → <project, or "not yet shaped">
F2. ...

## Sequence

<The order the features are shaped and built, and what each waits on. Start with the thinnest
version of the whole product that works end to end and answers the riskiest unknown.>

## Not yet specified

- <What is surely coming but cannot yet be stated as a feature. Coarser than a feature; no
  project until it sharpens.>

## Out of scope

- <What this product deliberately is not.>
```

- **Features are outcomes**, one line each, never a list of screens or components. Number them
  once; a dropped feature is struck through, so projects that cite it still resolve.
- **Fog or feature?** A feature you can state sharply now gets an F number, even if it waits. One
  you cannot yet phrase sharply goes under Not yet specified, and one later answer may turn it into
  several features or none.
- **An unknown that a prototype can settle** becomes a prototype item in the first project's Demo
  phase, not a question for me.
- **Out of scope is never empty** on a Confirmed product.
- **Worth it is never blank** on a Confirmed product. A test first verdict makes that test the
  first item of the first project, and the product stays Draft until its result is in.

## 3. Hand down, in stages

1. Once the product is Confirmed, create one project per feature in the Sequence's first step,
   linked to the product, holding only the feature's line. Later features stay in the Features
   list until their turn.
2. Hand the first project to `shape`. The next feature is shaped when the project before it
   reaches Launch, or sooner if I say so.
3. **Check Worth it again at each Launch**, before shaping the next feature, against what the
   launch showed and the time it really took; for personal software, whether I used it this week. Say in one line whether the verdict still holds; if
   not, recommend shrinking or stopping rather than carrying on by momentum.
4. A change to a feature after its project exists returns that project's spec to Draft; say so in
   one line and tell me what it touches.

## 4. From personal to sellable

When I think something I built for myself could sell, grill it again as a product for others,
with the same five worth-it questions. Two things differ from a fresh idea:

- **I am user one, which is evidence and bias at once.** That I use it weekly proves it works for
  one person. That I love it proves nothing about anyone else. Ask for evidence from others:
  people who have asked for it or a copy, the ones I could show it to this week, and how I would
  reach more of them.
- **Selling has a cost the personal version never paid.** Price it in weeks before the verdict:
  accounts for more than one person, billing, onboarding that works without me, support, privacy
  and security, reliability, and the time all of it takes from building.

The usual verdict is **test first**: put it in front of five people who have the problem, or
offer it before building the selling parts, and decide on what they do, not what they say. On
build, write a new Draft product for others, its features including the selling parts, with
product phases from here on; the personal product stays as it is until the new one replaces it.

## 5. Product updates and audits

- **A product update** is one line per project, with the project's own health and its phase,
  then the product's health as my judgement, proposed if the facts don't settle it. Read each
  project's latest update; never retype a project's progress by hand.
- **An audit** checks Worth it against the latest launch and the five rules: every feature has a project or is
  deferred, every project serves a feature, nothing is built under a Draft level, and Not yet
  specified holds nothing that has since sharpened.

## 6. Writing to the tracker and checking the tree

Writing follows section 7 of `../shape/SKILL.md`: state each write before making it, show the
first one, read it back. Then read the tree back into the outline in
`../shape/references/tree-outline.md` and run `python3 ../shape/scripts/check_tree.py
<outline.json>` from this skill's folder. Fix every line it prints before handing back.
