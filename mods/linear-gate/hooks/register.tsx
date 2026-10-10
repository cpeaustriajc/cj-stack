import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

const asks = atom({ plugin: 'linear-gate', key: 'asks' } as const, {} as Record<string, string>)

const LINEAR_WRITES = new Set([
  'save_issue', 'save_comment', 'save_document', 'save_project', 'save_milestone',
  'save_initiative', 'save_initiative_label', 'save_issue_label', 'save_project_label',
  'save_release', 'save_release_note', 'save_status_update', 'save_diff_comment',
  'create_attachment', 'create_attachment_from_upload', 'create_issue_label',
  'create_initiative_label', 'delete_attachment', 'delete_comment', 'delete_diff_comment',
  'delete_status_update', 'merge_diff', 'update_diff', 'submit_diff_review',
  'resolve_diff_thread', 'retire_issue_label', 'retire_initiative_label',
  'retire_project_label', 'restore_issue_label', 'restore_initiative_label',
  'restore_project_label', 'share_issue', 'unshare_issue', 'mark_notification',
])
const LINEAR_SERVER_WRITE = /^(save|delete|create|update|merge|submit|resolve|retire|restore|share|unshare|mark)_/
const LEAVE = 'Leave it'
const HEADER = 'Linear'
const CONFIRM = 'Apply this change?'
const LOOKUP_MS = 3000
const BUTTON_MAX = 40
// The engine refuses a dialog with more rows than this around it and draws its own,
// which would show only the staged question and hide the body.
const ROWS_MAX = 12
const NARROW = 60

function linearWrite(tool: string): string | undefined {
  const m = /^mcp__(.+?)__(.+)$/.exec(tool)
  if (!m) return undefined
  const [, server, name] = m
  if (LINEAR_WRITES.has(name)) return name
  if (server === 'linear-server' && LINEAR_SERVER_WRITE.test(name)) return name
  return undefined
}

const EVENT_KEYS = new Set(['tool', 'tool_use_id', 'agentId'])
const TEXT_KEYS = ['body', 'description', 'content']
const PR_STATUS: Record<string, string> = {
  markReadyForReview: 'ready for review', convertToDraft: 'back to draft', close: 'closed', reopen: 'reopened',
}
const REVIEW: Record<string, string> = { approved: 'Approve', changesRequested: 'Request changes on', commented: 'Leave a review comment on' }

const HEALTH: Record<string, string> = { onTrack: 'on track', atRisk: 'at risk', offTrack: 'off track' }
const clip = (s: string, max: number) => (s.length > max ? `${s.slice(0, max)}...` : s)
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
const short = (v: string) => (UUID.test(v) ? `${v.slice(0, 8)}…` : v)
const flat = (t: string) => t.replace(/^\s*(#+|[-*>]|\d+\.)\s+/gm, '').replace(/[*_`]/g, '').replace(/\s+/g, ' ').trim()
const isNames = (v: unknown): v is string[] => Array.isArray(v) && v.every(x => typeof x === 'string')
const shown = (v: unknown) =>
  clip(typeof v === 'string' ? short(flat(v)) : isNames(v) ? v.map(short).join(', ') : JSON.stringify(v), 80)
const words = (k: string) => k.replace(/Id$/, '').replace(/([A-Z])/g, ' $1').replace(/_/g, ' ').toLowerCase().trim()
const FIELD: Record<string, string> = { state: 'Status' }
const heading = (k: string) => FIELD[k] ?? words(k).replace(/^./, c => c.toUpperCase())
const STATE_VERB: Record<string, string> = { canceled: 'Cancel', cancelled: 'Cancel', done: 'Complete', completed: 'Complete' }
const people = (v: unknown) =>
  (Array.isArray(v) ? v : []).map(r => String(r.user ?? r.externalUserId ?? r.githubTeamId)).join(', ')

function whatItDoes(name: string, a: Record<string, unknown>): [string[], string[]] {
  const s = (k: string) => (typeof a[k] === 'string' ? (a[k] as string) : undefined)
  const pr = `PR ${s('urlOrId')}`
  switch (name) {
    case 'save_issue': {
      if (s('id')) return [[`${STATE_VERB[s('state')?.toLowerCase() ?? ''] ?? 'Update'} issue ${short(s('id')!)}`], ['id']]
      const template = s('template') ? `with template ${s('template')}` : 'with no template'
      return [[`Create issue "${s('title')}" in ${s('team')} ${template}`], ['title', 'team', 'template']]
    }
    case 'save_comment': {
      const parent = ['issueId', 'projectId', 'documentId', 'initiativeId', 'milestoneId', 'statusUpdateId'].find(k => s(k))
      const noun = parent?.replace(/Id$/, '').replace(/([A-Z])/g, ' $1').toLowerCase()
      const where = parent ? ` on ${noun} ${short(s(parent)!)}` : ''
      if (s('id')) return [[`Edit comment ${short(s('id')!)}`], ['id', ...(parent ? [parent] : [])]]
      if (s('parentId')) return [[`Reply to a comment${where}`], ['parentId', ...(parent ? [parent] : [])]]
      return parent ? [[`Comment${where}`], [parent]] : [[], []]
    }
    case 'save_status_update': {
      const health = s('health') ? `, health ${HEALTH[s('health')!] ?? s('health')}` : ''
      const lines = s('id')
        ? [`Edit the posted ${s('type')} status update ${s('id')}${health}`]
        : [`Post a ${s('type')} status update on ${s('project') ?? s('initiative')}${health}`]
      return [lines, ['type', 'id', 'health', 'project', 'initiative']]
    }
    case 'save_project': case 'save_milestone': case 'save_initiative': case 'save_document': {
      const noun = name.split('_')[1]
      if (s('id')) return [[`${STATE_VERB[s('state')?.toLowerCase() ?? ''] ?? 'Update'} ${noun} ${short(s('id')!)}`], ['id']]
      const key = s('name') ? 'name' : 'title'
      return [[`Create ${noun} "${s(key)}"`], [key]]
    }
    case 'delete_status_update':
      return [[`Delete the ${s('type')} status update ${s('id')}`], ['type', 'id']]
    case 'update_diff': {
      const lines: string[] = []
      if (a.addedReviewRequests) lines.push(`Request review from ${people(a.addedReviewRequests)} on ${pr}`)
      if (a.removedReviewRequests) lines.push(`Withdraw the review request to ${people(a.removedReviewRequests)} on ${pr}`)
      for (const l of (Array.isArray(a.addedIssueLinks) ? a.addedIssueLinks : []) as { issue: string; type: string }[])
        lines.push(`Link ${l.issue} (${l.type}) to ${pr}`)
      if (a.removedIssueLinks) lines.push(`Unlink ${(a.removedIssueLinks as string[]).join(', ')} from ${pr}`)
      if (s('statusAction')) lines.push(`Mark ${pr} ${PR_STATUS[s('statusAction')!] ?? s('statusAction')}`)
      if (!lines.length) lines.push(`Edit ${pr}`)
      return [lines, ['urlOrId', 'addedReviewRequests', 'removedReviewRequests', 'addedIssueLinks', 'removedIssueLinks', 'statusAction']]
    }
    case 'merge_diff':
      return [[`Merge ${pr}${s('mergeMethod') ? ` (${s('mergeMethod')!.toLowerCase()})` : ''}`], ['urlOrId', 'mergeMethod']]
    case 'submit_diff_review':
      return [[`${REVIEW[s('decision') ?? ''] ?? 'Review'} ${pr}`], ['urlOrId', 'decision']]
    case 'save_diff_comment': {
      const verb = a.draft ? 'Save a draft comment on' : s('commentId') ? 'Edit a comment on' : s('parentId') ? 'Reply on' : 'Comment on'
      return [[`${verb} ${pr}`], ['urlOrId', 'draft', 'commentId', 'parentId', 'draftId', 'anchor', 'anchorContent']]
    }
    case 'create_issue_label': case 'create_initiative_label':
    case 'save_issue_label': case 'save_initiative_label': case 'save_project_label': {
      const noun = `${name.split('_')[1]} label`
      if (name.startsWith('save_') && s('id')) return [[`Edit ${noun} ${s('id')}`], ['id']]
      const where = s('teamId') ? `in team ${short(s('teamId')!)}` : 'for the whole workspace'
      return [[`Create ${noun} "${s('name')}" ${where}`], ['name', 'teamId']]
    }
    case 'retire_issue_label': case 'retire_initiative_label': case 'retire_project_label':
    case 'restore_issue_label': case 'restore_initiative_label': case 'restore_project_label': {
      const [verb, kind] = name.split('_')
      return [[`${heading(verb)} ${kind} label ${s('id') ?? s('name')}`], ['id', 'name']]
    }
    case 'resolve_diff_thread':
      return [[`${a.resolved === false ? 'Reopen' : 'Resolve'} PR thread ${s('threadId')}`], ['threadId', 'resolved']]
    default:
      return [[], []]
  }
}

const SHOWN_EDITS = 5
const row = (t: string) => clip(t.replace(/\n/g, ' ⏎ ').replace(/[ \t]+/g, ' ').trim(), 160)
const quote = (t: string) => `"${clip(row(t), 40)}"`
const WRAP = 72
const WRAP_ROWS = 11

function wrapped(mark: string, text: string): string[] {
  return block(`  ${mark} `, '    ', text, l => l)
}

const unmark = (l: string) => l.replace(/^\s*(#+|[-*>]|\d+\.)\s+/, '').replace(/[*_`]/g, '')

function block(first: string, rest: string, text: string, tidy: (line: string) => string): string[] {
  const rows = text.split('\n').map(l => tidy(l).replace(/\s+/g, ' ').trim()).filter(Boolean).flatMap(line => {
    const out: string[] = []
    let cur = ''
    for (let word of line.split(' ')) {
      while (word.length > WRAP) {
        if (cur) out.push(cur), (cur = '')
        out.push(word.slice(0, WRAP)), (word = word.slice(WRAP))
      }
      if (cur && cur.length + 1 + word.length > WRAP) out.push(cur), (cur = '')
      cur = cur ? `${cur} ${word}` : word
    }
    return cur ? [...out, cur] : out
  })
  const kept = rows.slice(0, WRAP_ROWS).map((r, i) => (i ? `${rest}${r}` : `${first}${r}`))
  const hidden = rows.slice(WRAP_ROWS).join(' ').length
  return hidden ? [...kept, `${rest}… ${hidden} more characters`] : kept
}

function patchLines(patch: unknown[]): string[] {
  const lines = patch.slice(0, SHOWN_EDITS).flatMap((raw, i) => {
    const op = (raw ?? {}) as Record<string, string>
    const added = (t: string | undefined) => (t ? wrapped('+', t) : [])
    const body = (() => {
      switch (op.op) {
        case 'replace':
          return [...(op.replace_all ? ['Every match:'] : []), ...wrapped('−', op.old_string), ...added(op.new_string)]
        case 'insert_before': return [`Before ${quote(op.anchor)}:`, ...added(op.text)]
        case 'insert_after': return [`After ${quote(op.anchor)}:`, ...added(op.text)]
        case 'prepend': return ['At the start:', ...added(op.text)]
        case 'append': return ['At the end:', ...added(op.text)]
        case 'replace_range':
          return [`From ${quote(op.from)} up to ${quote(op.to)}:`, ...added(op.new_string)]
        default: return [`  ${shown(raw)}`]
      }
    })()
    return [...(i ? [''] : []), ...body.map(l => (l.startsWith('  ') ? l : `  ${l}`))]
  })
  const rest = patch.length - SHOWN_EDITS
  return rest > 0 ? [...lines, '', `  …and ${rest} more edit${rest === 1 ? '' : 's'}`] : lines
}

function actionOf(name: string, args: Record<string, unknown>): string[] {
  const [lines] = whatItDoes(name, args)
  return lines.length ? lines : [`${heading(name)} (${name})`]
}

function isChange(name: string, args: Record<string, unknown>): boolean {
  return /^(update|merge|submit|resolve)_/.test(name) || (/^save_/.test(name) && typeof args.id === 'string')
}

function isDrastic(name: string, args: Record<string, unknown>): boolean {
  return /^(delete|retire)_/.test(name) || STATE_VERB[String(args.state).toLowerCase()] === 'Cancel'
}

function describeWrite(name: string, args: Record<string, unknown>): string {
  const [, covered] = whatItDoes(name, args)
  const change = isChange(name, args)
  const sep = change ? ' → ' : ': '
  const label = (k: string) => (change ? heading(k) : heading(k.replace(/^add([A-Z])/, (_, c: string) => c.toLowerCase())))
  const textKey = TEXT_KEYS.find(k => typeof args[k] === 'string')
  const patch = Array.isArray(args.patch) ? args.patch : undefined
  const fields = Object.keys(args)
    .filter(k => !EVENT_KEYS.has(k) && !covered.includes(k) && k !== textKey && !(patch && k === 'patch'))
    .map(k => `  ${label(k)}${sep}${shown(args[k])}`)
  if (textKey) {
    const text = args[textKey] as string
    if (name === 'save_comment') fields.push(...(fields.length ? [''] : []), ...block('  ', '  ', text, unmark))
    else {
      const head = `  ${label(textKey)}${change ? ' →' : ':'}`
      const rows = block('    ', '    ', text, unmark)
      const inline = rows.length === 1 && head.length + rows[0].length - 3 <= 76
      fields.push(...(inline ? [`${head} ${rows[0].trim()}`] : [...(fields.length ? [''] : []), head, ...rows]))
    }
  }
  if (patch) fields.push(...(fields.length ? [''] : []), ...patchLines(patch))
  const warning = isDrastic(name, args) ? ['', '⚠ Everyone on the team sees this.'] : []
  return [...actionOf(name, args), ...(fields.length ? ['', ...fields] : []), ...warning, '', CONFIRM].join('\n')
}

function allowLabel(name: string, args: Record<string, unknown>): string {
  if (name === 'save_comment') return args.id ? 'Save edit' : args.parentId ? 'Post reply' : 'Post comment'
  const line = actionOf(name, args)[0]
  if (line.length <= BUTTON_MAX) return line
  const cut = line.includes('"') ? -1 : line.search(/ (in|with|on|for) /)
  const head = cut > 0 && cut <= BUTTON_MAX ? line.slice(0, cut) : line
  return head.length <= BUTTON_MAX ? head : `${head.slice(0, BUTTON_MAX - 1)}…`
}

function failure(out: { text?: string; isError?: boolean }): string | undefined {
  const text = out.text ?? ''
  if (out.isError) return clip(text || 'the tool reported an error', 100)
  if (/"success"\s*:\s*false/.test(text)) return clip(text, 100)
  return undefined
}

function bodyOf(description: string): string[] {
  return description.split('\n').slice(2, -2)
}

function drawnRows(description: string): number {
  return bodyOf(description).reduce((n, line) => n + Math.max(1, Math.ceil(line.length / NARROW)), 0)
}

// The dialog's question must reach the engine unchanged: a free-text answer is keyed by
// the question the dialog drew, and $.ui.ask drops one keyed by anything else.
async function stage($: Parameters<typeof read>[0], description: string): Promise<string> {
  const base = `${description.split('\n')[0]} — ${CONFIRM.toLowerCase()}`
  let question = base
  await update($, asks, pending => {
    question = base
    for (let n = 2; question in pending; n++) question = `${base} (${n})`
    return { ...pending, [question]: description }
  })
  return question
}

async function documentTitle($: Parameters<typeof read>[0], server: string, id: string): Promise<string | undefined> {
  try {
    const timeout = $.clock.sleep(LOOKUP_MS).then(() => undefined, () => new Promise<never>(() => {}))
    const out = await Promise.race([$.mcp.call(server, 'get_document', { id }), timeout])
    if (!out || out.isError) return undefined
    for (const block of out.content) {
      if (block.type !== 'text') continue
      const title = (JSON.parse((block as { text: string }).text) as { title?: unknown }).title
      if (typeof title === 'string' && title) return title
    }
  } catch {
    return undefined
  }
  return undefined
}


function diffColor(line: string, current: string | undefined): string | undefined {
  if (line.startsWith('  − ')) return 'red'
  if (line.startsWith('  + ')) return 'green'
  if (line.startsWith('    ') && line.trim()) return current
  if (line.startsWith('⚠')) return 'yellow'
  return undefined
}

export const register: Register = on => {
  on('tool.call', async ($, e, next) => {
    let args = e as unknown as Record<string, unknown>

    const name = linearWrite(e.tool)
    if (!name) return next(e)
    if ((await $.session.surfaces()).length === 0) return next(e)

    const server = /^mcp__(.+?)__/.exec(e.tool)![1]
    const title =
      name === 'save_document' && typeof args.id === 'string' ? await documentTitle($, server, args.id) : undefined
    if (title) args = { ...args, id: `"${title}"` }
    const allow = allowLabel(name, args)
    const description = describeWrite(name, args)
    const question = drawnRows(description) <= ROWS_MAX ? await stage($, description) : description
    let answer: string
    try {
      answer = await $.ui.ask(question, { options: [allow, LEAVE], header: HEADER })
    } catch {
      return { deny: `${$.plugin.name}: the Linear write was not approved (dialog closed or no one to ask).` }
    } finally {
      await update($, asks, ({ [question]: _, ...rest }) => rest)
    }
    const action = actionOf(name, args).join('; ')
    if (answer !== allow) {
      const reason = answer && answer !== LEAVE ? ` Their note: ${answer}` : ''
      return { deny: `${$.plugin.name}: the user denied this Linear write (${action}).${reason}` }
    }
    const out = await next(e)
    if (out.deny) return out
    const failed = failure(out)
    await $.ui.toast(failed ? `✘ ${action} failed: ${failed}` : `✔ ${action}`)
    return out
  })

  on('ui.render', { component: 'AskUserQuestion' }, async ($, e, next) => {
    const questions = e.props.questions as { question?: unknown; header?: unknown }[]
    const q = questions.length === 1 ? questions[0] : undefined
    const description = q?.header === HEADER && typeof q.question === 'string' ? (await read($, asks))[q.question] : undefined
    if (!description) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    const dialog = await next(e)
    let color: string | undefined
    const rows = bodyOf(description).map(line => {
      color = diffColor(line, color)
      return <Text color={color}>{line || ' '}</Text>
    })
    return (
      <Box flexDirection="column">
        {rows}
        {dialog}
      </Box>
    )
  })
}
