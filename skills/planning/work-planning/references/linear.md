# Linear adapter

Use the Linear MCP server. If the only Linear tools listed are `authenticate` and
`complete_authentication`, ask the person to connect Linear first.

## Objects

| Level | Linear object |
|---|---|
| Goal | Initiative |
| Project | Project |
| Spec, engineering document, decision | Project Document (a team-wide decision is a Team Document) |
| Phase | Project milestone |
| Work item | Issue. Linear has no Story, Feature or Epic type. |
| Sub-item | Sub-issue |
| Work type | Issue template (`Task`, `Bug`, `Chore` if the team has them), plus a label |
| Dependency | Issue relation "blocked by"; project dependency for project-level ones |
| Cycle | Cycle |
| Status update | Project update, with health `onTrack`, `atRisk` or `offTrack` |

Coming from Jira: a Story is an Issue, an Epic is a Project, and an Epic description or Confluence
PRD is the project's spec Document. Never file a spec as an issue, never title a project "Epic 1",
and don't use an `Epic` project template if the workspace has one: the word pulls Jira habits back.

## Templates

List the team's templates (`list_templates`) and read the one you need (`get_template`) before
writing. Pass the template's name when creating, so Linear applies its labels and fields. A form
template's questions are not answered by passing a description: fill its headings in the body
instead. Common project templates are a product one and an internal-tool one; check which exist.

Write checkboxes in Done When as `- [ ]`. Linear renders them as task lists.

## Tools

- Issues: `save_issue` (create, or update with `id`), `get_issue`, `list_issues`, `save_comment`.
- Projects: `save_project`, `get_project`, `save_milestone`, `save_status_update`.
- Documents: `save_document`, `get_document`, `list_documents`.
- Relations: `blockedBy`, `relatedTo` and `parentId` on `save_issue`. They only add; removing
  needs the matching `remove…` field.
- Prefer `patch` over a full `description` when changing part of an existing body.

## Things to know

- **Every write notifies.** Linear posts each save to the team's integrations, so batch changes to
  one issue into a single `save_issue`.
- **An issue in progress is often frozen** by team convention: put new findings in a comment or a
  new issue instead of editing the body. Check the project's facts.
- **Documents have search but no sorted views**, so a hand-kept index of documents rots. Find
  documents by title search instead.
- **Done is usually set by the verifier**, sometimes by an integration that moves issues on merge
  or review request. Don't mark an issue Done for them.
