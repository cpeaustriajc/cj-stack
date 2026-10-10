import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'
import type { Engine } from 'claude-code/testing'

const LINEAR = 'mcp__linear-server__'
const LINEAR_CONNECTOR = 'mcp__c52a7905-a861-4431-9619-0e85c0e83d6a__'

type Answer = string | 'dismiss' | 'first'

function world($t: Engine, on: On, answer: Answer, reply: Record<string, unknown> = { result: 'ok' }, surfaces: readonly string[] = ['terminal']) {
  const asked: string[] = []
  const ran: string[] = []
  const toasts: string[] = []

  on('ui.toast', ($, e) => {
    toasts.push(e.text)
    return { value: undefined } as never
  })
  on('session.surfaces', () => ({ value: surfaces }) as never)
  on('ui.render', { component: 'AskUserQuestion' }, () => ({ type: 'engine', ref: 0 }) as never)

  on('tool.call', async ($, e) => {
    if (e.tool === 'AskUserQuestion') {
      const question = (e as { questions: { question: string }[] }).questions[0].question
      asked.push(await shown($t, (e as { questions: { question: string }[] }).questions))
      if (answer === 'dismiss') return { deny: 'dismissed' }
      const first = (e as { questions: { options: { label: string }[] }[] }).questions[0].options[0].label
      const chosen = answer === 'first' ? first : answer
      return { result: { questions: (e as { questions: unknown[] }).questions, answers: { [question]: chosen } } } as never
    }
    ran.push(e.tool)
    return reply as never
  })

  return { asked, ran, toasts }
}

let mounts = 0

async function shown($: Engine, questions: { question: string }[]) {
  if (questions[0].question.includes('\n')) return questions[0].question
  const drawn = await $.ui.mount({
    plugin: 'work-pane', surface: 'terminal', component: 'AskUserQuestion', requestId: `ask${++mounts}`,
    props: { tool: 'AskUserQuestion', questions } as never,
  })
  const rows = ((await drawn.findAll({ type: 'Text' })) as { text: string }[]).map(t => t.text.trim() ? t.text : '')
  const head = questions[0].question.replace(/ — apply this change\?( \(\d+\))?$/, '')
  return [head, ...(rows.length ? ['', ...rows] : []), '', 'Apply this change?'].join('\n')
}

const comment = { tool: `${LINEAR}save_comment`, issueId: 'MP-77', body: 'Notice: AC 3 cannot ship as written.' }

test('an allowed Linear write runs', async ($, on) => {
  const w = world($, on, 'Post comment')
  const out = await $.tool.call(comment as never)
  expect(out.deny).toBe(undefined)
  expect(w.ran).toEqual([comment.tool])
})

test('a denied Linear write never runs and Claude reads why', async ($, on) => {
  const w = world($, on, 'Leave it')
  const out = await $.tool.call(comment as never)
  expect(w.ran).toEqual([])
  expect(out.deny).toMatch(/denied/)
  expect(out.deny).not.toMatch(/Their note/)
})

test('a typed answer denies, and the reason reaches Claude', async ($, on) => {
  const w = world($, on, 'wrong issue, use MP-78')
  const out = await $.tool.call(comment as never)
  expect(w.ran).toEqual([])
  expect(out.deny).toMatch(/wrong issue, use MP-78/)
})

test('an empty answer denies', async ($, on) => {
  const w = world($, on, '')
  const out = await $.tool.call(comment as never)
  expect(w.ran).toEqual([])
  expect(typeof out.deny).toBe('string')
})

test('a dismissed dialog denies instead of letting the write through', async ($, on) => {
  const w = world($, on, 'dismiss')
  const out = await $.tool.call(comment as never)
  expect(w.ran).toEqual([])
  expect(typeof out.deny).toBe('string')
})

test('Linear reads pass without asking', async ($, on) => {
  const w = world($, on, 'Deny')
  for (const read of ['list_issues', 'get_issue', 'list_comments', 'get_document']) {
    await $.tool.call({ tool: `${LINEAR}${read}`, id: 'MP-77' } as never)
  }
  expect(w.asked).toEqual([])
  expect(w.ran.length).toBe(4)
})

test('the claude.ai Linear connector is gated too', async ($, on) => {
  const w = world($, on, 'Deny')
  await $.tool.call({ ...comment, tool: `${LINEAR_CONNECTOR}save_issue` } as never)
  expect(w.asked.length).toBe(1)
  expect(w.ran).toEqual([])
})

test('a write on a future linear-server tool is gated', async ($, on) => {
  const w = world($, on, 'Deny')
  await $.tool.call({ tool: `${LINEAR}update_cycle`, id: 'c1' } as never)
  expect(w.asked.length).toBe(1)
})

test('look-alike writes on other servers pass without asking', async ($, on) => {
  const w = world($, on, 'Deny')
  for (const tool of [
    'mcp__3c832f4a-5c79-4742-b337-41dd7b8b3f36__create_label',
    'mcp__3c832f4a-5c79-4742-b337-41dd7b8b3f36__update_draft',
    'mcp__4a38aacc-854f-424a-8068-72256412473c__create_file',
    'mcp__notion-aov__notion-update-page',
  ]) {
    await $.tool.call({ tool } as never)
  }
  expect(w.asked).toEqual([])
  expect(w.ran.length).toBe(4)
})

test('a subagent write is gated', async ($, on) => {
  const w = world($, on, 'Deny')
  await $.tool.call({ ...comment, agentId: 'a1' } as never)
  expect(w.asked.length).toBe(1)
  expect(w.ran).toEqual([])
})

test('the question names the action, the issue and the text', async ($, on) => {
  const w = world($, on, 'Allow')
  await $.tool.call(comment as never)
  expect(w.asked[0]).toMatch(/^Comment on issue/)
  expect(w.asked[0]).toMatch(/MP-77/)
  expect(w.asked[0]).toMatch(/AC 3 cannot ship/)
})

const newIssue = { tool: `${LINEAR}save_issue`, team: 'SD Marketplace', title: 'Fix cart total', description: '## Context' }

test('a new issue names the template it uses', async ($, on) => {
  const w = world($, on, 'Allow')
  await $.tool.call({ ...newIssue, template: 'Chore' } as never)
  expect(w.asked[0]).toMatch(/template Chore/)
})

test('a new issue without a template says so', async ($, on) => {
  const w = world($, on, 'Allow')
  await $.tool.call(newIssue as never)
  expect(w.asked[0]).toMatch(/no template/)
})

test('an issue update never mentions a template', async ($, on) => {
  const w = world($, on, 'Allow')
  await $.tool.call({ tool: `${LINEAR}save_issue`, id: 'MP-123', state: 'In Progress' } as never)
  expect(w.asked[0]).not.toMatch(/template/)
})

test('a comment never mentions a template', async ($, on) => {
  const w = world($, on, 'Allow')
  await $.tool.call(comment as never)
  expect(w.asked[0]).not.toMatch(/template/)
})

const pr = 'cpeaustriajc/marketplace-strangedomains#415'

async function question($: Parameters<Parameters<typeof test>[1]>[0], on: On, call: Record<string, unknown>) {
  const w = world($, on, 'first')
  await $.tool.call(call as never)
  return w.asked[0]
}

test('a review request names the reviewer and the PR', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}update_diff`, urlOrId: pr, addedReviewRequests: [{ user: 'Codex' }] })
  expect(q).toMatch(/Request review from Codex on PR cpeaustriajc\/marketplace-strangedomains#415/)
})

test('a PR status change says what the status becomes', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}update_diff`, urlOrId: pr, statusAction: 'markReadyForReview' })
  expect(q).toMatch(/Mark PR .*#415 ready for review/)
})

test('a PR edit lists the fields it changes', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}update_diff`, urlOrId: pr, title: 'New title', addedIssueLinks: [{ issue: 'MP-123', type: 'closes' }] })
  expect(q).toMatch(/Title → New title/)
  expect(q).toMatch(/Link MP-123 \(closes\)/)
})

test('a merge names the PR and the method', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}merge_diff`, urlOrId: pr, mergeMethod: 'SQUASH' })
  expect(q).toMatch(/Merge PR .*#415 \(squash\)/)
})

test('a review decision is spelled out', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}submit_diff_review`, urlOrId: pr, decision: 'approved' })
  expect(q).toMatch(/Approve PR .*#415/)
})

test('an issue update lists each field it changes', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}save_issue`, id: 'MP-123', state: 'In Progress', assignee: 'me' })
  expect(q).toMatch(/Update issue MP-123/)
  expect(q).toMatch(/Status → In Progress/)
  expect(q).toMatch(/Assignee → me/)
})

test('a new issue names its team and title', async ($, on) => {
  const q = await question($, on, newIssue)
  expect(q).toMatch(/Create issue "Fix cart total" in SD Marketplace/)
})

test('a comment names its issue', async ($, on) => {
  expect(await question($, on, comment)).toMatch(/Comment on issue MP-77/)
})

const reply = { tool: `${LINEAR}save_comment`, parentId: '9cfdbd28-6d4e-4d7a-af39-daa8dd6f279b', body: 'Done.' }

test('a reply says it is a reply, with no raw comment id', async ($, on) => {
  const q = await question($, on, reply)
  expect(q.split('\n')[0]).toBe('Reply to a comment')
  expect(q).not.toMatch(/9cfdbd28-6d4e/)
})

test('a reply that names its issue says where it lands', async ($, on) => {
  const q = await question($, on, { ...reply, issueId: 'MP-77' })
  expect(q.split('\n')[0]).toBe('Reply to a comment on issue MP-77')
})

test('comment buttons are plain verbs, and they still allow', async ($, on) => {
  const seen: string[] = []
  on('tool.call', { tool: 'AskUserQuestion' }, ($, e, next) => {
    seen.push((e as { questions: { options: { label: string }[] }[] }).questions[0].options[0].label)
    return next(e)
  })
  const w = world($, on, 'first')
  await $.tool.call(reply as never)
  await $.tool.call(comment as never)
  await $.tool.call({ tool: `${LINEAR}save_comment`, id: '9cfdbd28-6d4e-4d7a-af39-daa8dd6f279b', body: 'x' } as never)
  expect(seen).toEqual(['Post reply', 'Post comment', 'Save edit'])
  expect(w.ran.length).toBe(3)
})

test('an edited comment names it by a short id', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}save_comment`, id: '9cfdbd28-6d4e-4d7a-af39-daa8dd6f279b', body: 'x' })
  expect(q.split('\n')[0]).toBe('Edit comment 9cfdbd28…')
})

const thanks = 'Thanks Rhea, you were right, and your run found a real gap. If someone signs out and then registers a new account in the same browser, SD Market still remembers the old cart.\n\nI opened MP-130 for it.'

test('a comment body shows in full, wrapped, without a Body label', async ($, on) => {
  const q = await question($, on, { ...reply, body: thanks })
  expect(q).not.toMatch(/Body/)
  const rows = q.split('\n').slice(2, -2)
  expect(rows.every(r => r.startsWith('  ') && r.length <= 76)).toBe(true)
  expect(rows.join(' ')).toMatch(/remembers the old cart\./)
  expect(rows.at(-1)).toBe('  I opened MP-130 for it.')
})

test('an unknown write still names the tool and every field', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}update_cycle`, id: 'c1', name: 'Cycle 9' })
  expect(q).toMatch(/update_cycle/)
  expect(q).toMatch(/c1/)
  expect(q).toMatch(/Cycle 9/)
})

test('a long text is cut short and says how much is hidden', async ($, on) => {
  const q = await question($, on, { ...comment, body: 'word '.repeat(600) })
  expect(q.length).toBeLessThan(1200)
  expect(q).toMatch(/… \d+ more characters/)
})

test('a new status update names the project and its health', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}save_status_update`, type: 'project', project: 'SD Checkout', health: 'atRisk', body: 'Blocked on SD.' })
  expect(q).toMatch(/Post a project status update on SD Checkout, health at risk/)
  expect(q).toMatch(/Blocked on SD/)
})

test('an edit of a posted status update says it edits one', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}save_status_update`, type: 'initiative', id: 'su1', health: 'onTrack' })
  expect(q).toMatch(/Edit the posted initiative status update su1, health on track/)
})

test('a status update delete says it deletes one', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}delete_status_update`, type: 'project', id: 'su1' })
  expect(q).toMatch(/Delete the project status update su1/)
})

test('a comment on a status update reads as one', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}save_comment`, statusUpdateId: 'su1', body: 'Also: MP-123 merged.' })
  expect(q).toMatch(/Comment on status update su1/)
})

const review = { tool: `${LINEAR}update_diff`, urlOrId: pr, addedReviewRequests: [{ user: 'Codex' }] }

test('the action leads the question and the fields sit below it', async ($, on) => {
  const q = await question($, on, { ...review, title: 'New title' })
  const lines = q.split('\n')
  expect(lines[0]).toMatch(/^Request review from Codex on PR/)
  expect(q).toMatch(/\n {2}Title → New title/)
  expect(lines[lines.length - 1]).toBe('Apply this change?')
})

const teamId = '86f90bfc-243d-4126-81f2-b512e92b02ea'
const label = { tool: `${LINEAR}create_issue_label`, name: 'Design System', teamId, color: '#BB87FC', description: 'Shared visual language.' }

test('a new label names itself and its team in the headline', async ($, on) => {
  const q = await question($, on, label)
  expect(q.split('\n')[0]).toBe('Create issue label "Design System" in team 86f90bfc…')
})

test('a label edit reads as a sentence', async ($, on) => {
  expect(await question($, on, { tool: `${LINEAR}save_issue_label`, id: 'l1', name: 'DS' })).toMatch(/^Edit issue label l1/)
})

test('a label retire reads as a sentence', async ($, on) => {
  expect(await question($, on, { tool: `${LINEAR}retire_project_label`, id: 'l2' })).toMatch(/^Retire project label l2/)
})

test('a label restore reads as a sentence', async ($, on) => {
  expect(await question($, on, { tool: `${LINEAR}restore_initiative_label`, id: 'l3' })).toMatch(/^Restore initiative label l3/)
})

test('a workspace label says it has no team', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}create_issue_label`, name: 'Bug' })
  expect(q.split('\n')[0]).toBe('Create issue label "Bug" for the whole workspace')
})

test('a new thing\'s fields read as labelled rows, never arrows, with no repeat of the tool name', async ($, on) => {
  const q = await question($, on, label)
  expect(q).toMatch(/\n {2}Color: #BB87FC\n/)
  expect(q).toMatch(/\n {2}Description: Shared visual language\.\n/)
  expect(q).not.toMatch(/→|via |create_issue_label|teamId|"Shared/)
})

test('an id field drops its Id suffix and a UUID is shortened', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}save_issue`, id: 'MP-1', projectId: teamId })
  expect(q).toMatch(/\n {2}Project → 86f90bfc…\n/)
})

test('an unknown write reads as words and still names its tool once', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}update_cycle`, id: 'c1', name: 'Cycle 9' })
  expect(q.split('\n')[0]).toBe('Update cycle (update_cycle)')
  expect(q.match(/update_cycle/g)).toHaveLength(1)
})

test('a write that worked shows a toast naming the action', async ($, on) => {
  const w = world($, on, 'first', { result: { success: true }, text: '{"success":true,"metadataUpdated":true}' })
  await $.tool.call(review as never)
  expect(w.toasts).toEqual([expect.stringMatching(/✔ .*Request review from Codex on PR .*#415/)])
})

test('a write the tool reports as an error shows a failure toast with its reason', async ($, on) => {
  const w = world($, on, 'first', { result: 'x', text: 'Merge blocked: checks pending', isError: true })
  await $.tool.call({ tool: `${LINEAR}merge_diff`, urlOrId: pr } as never)
  expect(w.toasts).toEqual([expect.stringMatching(/✘ .*Merge PR .*#415 failed: Merge blocked: checks pending/)])
})

test('a success:false reply counts as a failure', async ($, on) => {
  const w = world($, on, 'first', { result: { success: false }, text: '{"success":false,"error":"not found"}' })
  await $.tool.call(review as never)
  expect(w.toasts[0]).toMatch(/✘ .*failed/)
})

test('a denied write shows no toast', async ($, on) => {
  const w = world($, on, 'Deny')
  await $.tool.call(review as never)
  expect(w.toasts).toEqual([])
})

test('a deny tells Claude which action was refused', async ($, on) => {
  world($, on, 'no need for now')
  const out = await $.tool.call(review as never)
  expect(out.deny).toMatch(/Request review from Codex on PR .*#415/)
  expect(out.deny).toMatch(/no need for now/)
})

const cancelProject = { tool: `${LINEAR}save_project`, id: 'P-MP-7', state: 'Canceled' }

test('a project cancel reads as one sentence with the change below it', async ($, on) => {
  const q = await question($, on, cancelProject)
  const lines = q.split('\n')
  expect(lines[0]).toBe('Cancel project P-MP-7')
  expect(q).toMatch(/\n {2}Status → Canceled\n/)
  expect(q).not.toMatch(/save_project|Id:/)
})

test('a cancel or delete carries the warning line; a plain edit does not', async ($, on) => {
  const w = world($, on, 'Leave it')
  await $.tool.call(cancelProject as never)
  await $.tool.call({ tool: `${LINEAR}delete_comment`, id: 'c1' } as never)
  await $.tool.call({ tool: `${LINEAR}save_project`, id: 'P-MP-7', state: 'Started' } as never)
  expect(w.asked[0]).toMatch(/⚠ Everyone on the team sees this\./)
  expect(w.asked[1]).toMatch(/⚠/)
  expect(w.asked[2]).not.toMatch(/⚠/)
})

test('an issue moved to Canceled or Done says so in its headline', async ($, on) => {
  const w = world($, on, 'Leave it')
  await $.tool.call({ tool: `${LINEAR}save_issue`, id: 'MP-9', state: 'Canceled' } as never)
  await $.tool.call({ tool: `${LINEAR}save_issue`, id: 'MP-9', state: 'Done' } as never)
  expect(w.asked[0].split('\n')[0]).toBe('Cancel issue MP-9')
  expect(w.asked[1].split('\n')[0]).toBe('Complete issue MP-9')
})

test('a new project, milestone, initiative or document names itself', async ($, on) => {
  const w = world($, on, 'Leave it')
  await $.tool.call({ tool: `${LINEAR}save_project`, name: 'SD Checkout', team: 'SD' } as never)
  await $.tool.call({ tool: `${LINEAR}save_milestone`, name: 'Beta', project: 'SD Checkout' } as never)
  await $.tool.call({ tool: `${LINEAR}save_initiative`, name: 'V1' } as never)
  await $.tool.call({ tool: `${LINEAR}save_document`, title: 'Decision: Cart', project: 'SD Checkout' } as never)
  expect(w.asked.map(q => q.split('\n')[0])).toEqual([
    'Create project "SD Checkout"',
    'Create milestone "Beta"',
    'Create initiative "V1"',
    'Create document "Decision: Cart"',
  ])
})

test('the allow button is named after the action and the other button is Leave it', async ($, on) => {
  const seen: string[][] = []
  on('tool.call', { tool: 'AskUserQuestion' }, ($, e, next) => {
    seen.push((e as { questions: { options: { label: string }[] }[] }).questions[0].options.map(o => o.label))
    return next(e)
  })
  world($, on, 'Cancel project P-MP-7')
  const out = await $.tool.call(cancelProject as never)
  expect(seen[0]).toEqual(['Cancel project P-MP-7', 'Leave it'])
  expect(out.deny).toBe(undefined)
})

test('a long headline gives a short button, and that button still allows', async ($, on) => {
  const seen: string[][] = []
  on('tool.call', { tool: 'AskUserQuestion' }, ($, e, next) => {
    seen.push((e as { questions: { options: { label: string }[] }[] }).questions[0].options.map(o => o.label))
    return next(e)
  })
  const call = { ...newIssue, title: 'Show the cart total next to every saved domain', template: 'Task' }
  const w = world($, on, 'first')
  await $.tool.call(call as never)
  expect(seen[0][0].length).toBeLessThanOrEqual(40)
  expect(w.ran).toEqual([call.tool])
})

test('an old "Allow" answer no longer allows', async ($, on) => {
  const w = world($, on, 'Allow')
  await $.tool.call(cancelProject as never)
  expect(w.ran).toEqual([])
})

const newProject = {
  tool: `${LINEAR}save_project`, name: 'Production Launch Readiness', addTeams: ['SD Marketplace'], lead: 'me',
  state: 'Planned', addInitiatives: ['I-1'], description: '## Why\n\nProduction runs behind a private sign-in.\n\n- SD side\n- never checked',
}

test('a list of names reads as words, not code', async ($, on) => {
  const q = await question($, on, newProject)
  expect(q).toMatch(/\n {2}Teams: SD Marketplace\n/)
  expect(q).toMatch(/\n {2}Initiatives: I-1\n/)
  expect(q).not.toMatch(/\[|"SD/)
})

test('a new thing drops the Add in its field names; a change keeps it', async ($, on) => {
  const w = world($, on, 'Leave it')
  await $.tool.call(newProject as never)
  await $.tool.call({ tool: `${LINEAR}save_project`, id: 'P-1', addTeams: ['SD'] } as never)
  expect(w.asked[0]).not.toMatch(/Add teams/)
  expect(w.asked[1]).toMatch(/\n {2}Add teams → SD\n/)
})

test('a markdown description sits under its label, a row per paragraph, without its marks', async ($, on) => {
  const q = await question($, on, newProject)
  const lines = q.split('\n')
  const at = lines.indexOf('  Description:')
  expect(lines.slice(at + 1, at + 5)).toEqual(['    Why', '    Production runs behind a private sign-in.', '    SD side', '    never checked'])
  expect(q).not.toMatch(/##/)
})

test('a list of objects still shows its contents', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}update_cycle`, id: 'c1', links: [{ url: 'https://x.dev' }] })
  expect(q).toMatch(/x\.dev/)
})

const DOC = 'c089f90f-4944-4052-9616-e8fdc66839f3'
const patched = (patch: unknown[]) => ({ tool: `${LINEAR}save_document`, id: DOC, patch })

test('a patch reads as before and after lines, not JSON', async ($, on) => {
  const q = await question($, on, patched([{ op: 'replace', old_string: '**Status:** Proposed', new_string: '**Status:** Accepted' }]))
  expect(q.split('\n')[0]).toBe('Update document c089f90f…')
  expect(q).toMatch(/\n {2}− \*\*Status:\*\* Proposed\n {2}\+ \*\*Status:\*\* Accepted\n/)
  expect(q).not.toMatch(/Patch|"op"|\[\{/)
})

test('a replace with an empty new string reads as a deletion', async ($, on) => {
  const q = await question($, on, patched([{ op: 'replace', old_string: 'Draft note', new_string: '' }]))
  expect(q).toMatch(/\n {2}− Draft note\n/)
  expect(q).not.toMatch(/\n {2}\+ /)
})

test('replace_all says it hits every match', async ($, on) => {
  const q = await question($, on, patched([{ op: 'replace', old_string: 'MP-7', new_string: 'MP-8', replace_all: true }]))
  expect(q).toMatch(/every match/i)
})

test('inserts, prepends, appends and ranges name where the text goes', async ($, on) => {
  const q = await question($, on, patched([
    { op: 'insert_before', anchor: '## Risks', text: 'Before risks' },
    { op: 'insert_after', anchor: '## Goal', text: 'After goal' },
    { op: 'prepend', text: 'At start' },
    { op: 'append', text: 'At end' },
    { op: 'replace_range', from: '## Old', to: '## Next', new_string: 'New section' },
  ]))
  expect(q).toMatch(/Before "## Risks":\n {2}\+ Before risks/)
  expect(q).toMatch(/After "## Goal":\n {2}\+ After goal/)
  expect(q).toMatch(/At the start:\n {2}\+ At start/)
  expect(q).toMatch(/At the end:\n {2}\+ At end/)
  expect(q).toMatch(/From "## Old" up to "## Next":\n {2}\+ New section/)
})

test('a long patch shows the first edits and counts the rest', async ($, on) => {
  const ops = Array.from({ length: 7 }, (_, i) => ({ op: 'append', text: `line ${i}` }))
  const q = await question($, on, patched(ops))
  expect(q).toMatch(/line 4/)
  expect(q).not.toMatch(/line 5/)
  expect(q).toMatch(/…and 2 more edits/)
})

const long = 'Strange Domains wrote this working reference on 2026-09-09, and it is kept for history only. Several parts no longer hold: an order now carries one line per domain, the buyer pays on the checkout page, and the callback names the order.'

test('a long patch text wraps onto indented rows instead of being cut', async ($, on) => {
  const q = await question($, on, patched([{ op: 'prepend', text: long }]))
  const rows = q.split('\n').filter(l => l.startsWith('  + ') || l.startsWith('    '))
  expect(rows.length).toBeGreaterThan(1)
  expect(rows.every(r => r.length <= 76)).toBe(true)
  expect(rows.slice(1).every(r => r.startsWith('    ') && r[4] !== ' ')).toBe(true)
  expect(rows.map(r => r.slice(4)).join(' ')).toBe(long)
})

test('a paragraph break starts a new row and blank lines are dropped', async ($, on) => {
  const q = await question($, on, patched([{ op: 'append', text: 'first\n\nsecond' }]))
  expect(q).toMatch(/\n {2}\+ first\n {4}second\n/)
})

test('one unbroken word longer than a row is split, not left overflowing', async ($, on) => {
  const q = await question($, on, patched([{ op: 'append', text: 'x'.repeat(200) }]))
  const rows = q.split('\n').filter(l => /^ {2}\+ |^ {4}x/.test(l))
  expect(rows.every(r => r.length <= 76)).toBe(true)
})

test('a very long text stops after twelve rows and says how much is hidden', async ($, on) => {
  const text = Array.from({ length: 60 }, (_, i) => `word${i} filler text here`).join(' ')
  const q = await question($, on, patched([{ op: 'append', text }]))
  const rows = q.split('\n').filter(l => l.startsWith('  + ') || /^ {4}\S/.test(l))
  expect(rows.length).toBe(12)
  expect(q).toMatch(/\n {4}… \d+ more characters\n/)
})

test('a long old text wraps under its minus the same way', async ($, on) => {
  const q = await question($, on, patched([{ op: 'replace', old_string: long, new_string: 'short' }]))
  expect(q).toMatch(/\n {2}− Strange Domains/)
  expect(q).toMatch(/\n {4}\S/)
  expect(q).toMatch(/\n {2}\+ short\n/)
})

test('an unknown patch op still shows its contents', async ($, on) => {
  const q = await question($, on, patched([{ op: 'swap', a: 'left' }]))
  expect(q).toMatch(/left/)
})

test('a patch on an issue description reads the same way', async ($, on) => {
  const q = await question($, on, { tool: `${LINEAR}save_issue`, id: 'MP-9', patch: [{ op: 'replace', old_string: 'a', new_string: 'b' }] })
  expect(q).toMatch(/\n {2}− a\n {2}\+ b\n/)
})

test('a Linear write passes to the host without asking when no surface can draw a dialog', async ($, on) => {
  const w = world($, on, 'first', { result: 'ok' }, [])
  const out = await $.tool.call(comment as never)
  expect(w.asked).toEqual([])
  expect(w.ran).toEqual([comment.tool])
  expect(out.deny).toBe(undefined)
})

test('a Linear write still asks when a terminal surface can draw the dialog', async ($, on) => {
  const w = world($, on, 'first', { result: 'ok' }, ['terminal'])
  await $.tool.call(comment as never)
  expect(w.asked.length).toBe(1)
})

test('a Linear write is still denied when the person closes the dialog on a terminal surface', async ($, on) => {
  const w = world($, on, 'dismiss', { result: 'ok' }, ['terminal'])
  const out = await $.tool.call(comment as never)
  expect(w.ran).toEqual([])
  expect(out.deny).toMatch(/not approved \(dialog closed or no one to ask\)/)
})

test('a non-Linear tool is untouched when no surface can draw a dialog', async ($, on) => {
  const w = world($, on, 'first', { result: 'ok' }, [])
  const out = await $.tool.call({ tool: 'Read' } as never)
  expect(w.asked).toEqual([])
  expect(w.ran).toEqual(['Read'])
  expect(out.deny).toBe(undefined)
})
