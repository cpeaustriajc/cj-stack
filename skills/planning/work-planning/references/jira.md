# Jira adapter

Use Atlassian's MCP server (Rovo MCP) or the `acli` CLI. Jira's interface now calls issues "work
items" and projects "spaces"; the APIs and MCP tools still say "issue" and "project".

## Objects

| Level | Jira object |
|---|---|
| Goal | An Initiative above Epic (Premium plans, configured in Plans); otherwise a Confluence page the epics link to |
| Project | Epic. Its description holds the project template. |
| Spec, engineering document | A Confluence page linked from the epic. Jira descriptions are a poor home for a long spec with a status line and history. |
| Decision | Follows the `project-knowledge` skill if installed (Confluence adapter); otherwise a Confluence page per decision |
| Phase | Jira has no milestone inside an epic. Use the epic's workflow status if the board has phase statuses; otherwise a `phase-demo`, `phase-implementation` … label on the epic, and a Fix Version for the Launch release. Pick one and record it in the project's facts. |
| Work item | Story or Task (child of the epic); Bug for a defect |
| Sub-item | Subtask |
| Work type | Work type (Story, Task, Bug); a Chore is a Task with a `chore` label unless the space defines its own type |
| Dependency | Issue link "is blocked by" (`listJiraIssueLinkTypes` gives the exact name) |
| Cycle | Sprint |
| Status update | A comment on the epic, or the space's own status update feature |

## Templates and fields

- Read the space's work types and required fields first (`listJiraProjectIssueTypesMetadata`,
  then `getJiraIssueTypeMetaWithFields`). Many spaces have a custom **Acceptance criteria** field;
  when they do, Done When goes there and the description keeps Context, Outcome and Out of Scope.
- Rich text is stored as Atlassian Document Format. Whether Markdown checkboxes survive the MCP
  tool is unverified: call `getContentFormatGuide` before the first write, and read the item back.
  If checkboxes are lost, use a numbered list and say so.

## Tools

- Rovo MCP, Jira: `createJiraIssue`, `editJiraIssue`, `getJiraIssue`, `searchJiraIssuesUsingJql`,
  `transitionJiraIssue` (with `listJiraIssueTransitions`), `addOrEditJiraIssueComment`.
- Rovo MCP, Confluence: `createConfluenceContent`, `updateConfluenceContent`,
  `getConfluenceContent`, `searchConfluence`.
- CLI: `acli jira workitem create --project KEY --type Task --summary "<title>" --description-file body.txt --label <label>`.

## Things to know

- **Sprint language is not structure.** Translate "sprint goal" or "committed points" into the
  method's terms (a project's Success, a cycle's chosen items); don't recreate ceremonies.
- **Story points and estimates** are the team's choice; leave them blank unless the facts say the
  team estimates.
- **Workflows differ per space.** Read the transitions before moving an item, and never move one
  to Done on the verifier's behalf.
