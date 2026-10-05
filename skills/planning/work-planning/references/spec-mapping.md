# Shaping a spec

## Where each part of a spec lands

| Spec section | Destination |
| --- | --- |
| Product goal, business value, customer value | The goal (usually already there) |
| Epic, objective | Project Why and What |
| Feature 1, Feature 2 | Spec sections, one outcome sentence each |
| User story N | A build item, once the spec is Confirmed |
| Acceptance criteria | The spec, verbatim; quoted into items |
| Acceptance considerations: UI behaviour, ordering | Item acceptance criteria |
| Acceptance considerations: performance | Project How |
| Dependencies on another system | Project How; on other work, a "blocked by" relation |
| Assumptions | Project Not in scope, or a decision |
| Risks | Project Risks, only those that change the build |
| Example values | A verifier's example under the item, generalised |
| Anything naming infrastructure, a vendor API, an endpoint or a sub-second budget | The engineering document, or a decision when it applies to every project; never carried into items |

## A spec filed as a ticket

1. Create the spec document in the project, with the author's text verbatim and status Draft.
2. Convert the ticket: move it back to the backlog, or keep it as the first build slice once the
   spec is Confirmed. Never cancel it.
3. Put the project in Demo (`phases.md`), and add the approval item.
4. Split no build items until the spec is Confirmed.

## Translating an old epic, brief or plan

Treat an old source as evidence of the problem someone wanted solved, not as a technical spec. Its
architecture, named services, data flows, estimates and implementation criteria are hypotheses
unless current code, tests, contracts or a newer decision confirm them. Current decisions and
current code outrank a stale plan.

- Keep the source's key or link as provenance, recover the intent, and draft from the present state.
- When sources conflict on a product choice, ask the product owner. Don't ask them to settle a
  technical question the code or a current contract already answers.
- Account for every source item as one of: translated into a project; merged with another;
  split into several projects; kept as goal or reference context; or held for a product decision.
- Merge several old items when they describe one outcome today, and list every contributing key
  on the merged draft.
