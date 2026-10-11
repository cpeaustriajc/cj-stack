# Phases

Every project gets a fixed set of phases, in order, and no others. Leave each phase's description
empty: the same text on every project is noise, and the table below is the definition. Don't split
phases into frontend and backend.

## Product project

| Phase | Holds | Exit check | Decides |
| --- | --- | --- | --- |
| Demo | The spec in Draft, plus throwaway mockup or prototype items. No build items. | An approval item for the approver ("<approver> approves the <spec> after the demo") is done, and the spec is marked Confirmed. | Approver |
| Implementation | Items split from the Confirmed spec, the next slice only. | The verifier marked every item done. | Verifier |
| Launch | The production release, a release note, verification on production. | The product owner accepts the release against the spec's statements. | Product owner |
| Post Launch | Bugs and small follow-ups to what shipped. | Two cycles after Launch the project completes. | Engineering |

- **Demo is time-boxed to one cycle.** A demo still unconfirmed after that goes back to the
  product owner as a question, not a second demo. Demo work is throwaway, never the start of
  production code.
- **A change of direction** during Demo edits the spec and closes the mockup items. After Demo it
  moves the project back to Demo: the spec returns to Draft, unstarted build items go back to the
  backlog, and only the slice in progress is lost.
- **Post Launch is not a parking lot.** Anything that is not a fix to what shipped is a new spec.

## Internal tool

Three phases. There is no Demo, because no approver gates a tool only the team uses, and no spec:
the project What and the items' Done When are enough.

| Phase | Holds | Exit check | Decides |
| --- | --- | --- | --- |
| Implementation | Build items, plus a mockup on the first item when the tool has a screen. | The verifier marked every item done (Chores: engineering, after code review). | Verifier |
| Launch | The tool live where the team uses it, and a note on how to use it. | The main user confirms they can do the job named in Success. | Main user |
| Post Launch | Bugs and small follow-ups to what shipped. | Two cycles after Launch the project completes. New asks start a new project. | Engineering |

A mockup is approved on its item, before the build starts, by whoever owns visual calls; visual
sign-off is not a phase.
