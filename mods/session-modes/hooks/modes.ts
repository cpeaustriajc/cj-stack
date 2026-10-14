export type Mode = 'off' | 'audit' | 'no-pr' | 'chat' | 'product'

export const MODES = ['audit', 'no-pr', 'chat', 'product', 'off'] as const

export function parseMode(args: string): Mode | undefined {
  const name = args.trim().toLowerCase()
  return (MODES as readonly string[]).includes(name) ? (name as Mode) : undefined
}

export const SECTION: Record<Exclude<Mode, 'off'>, string> = {
  audit: 'Audit mode: read and report only. Do not edit files, commit, push or open pull requests; list findings instead.',
  'no-pr': 'No-PR mode: do not open a pull request. Commit on the branch and say so in the reply.',
  chat: 'Chat mode: do not open a pull request or push. Put the result in the reply, not in a pull request.',
  product:
    'Product mode: plan top-down and write no code. Use vision for the product, shape for a project and tickets for its work items, and triage for any open decision. Load the skill for the level before writing to the tracker.',
}

export const LABEL: Record<Exclude<Mode, 'off'>, string> = {
  audit: 'Audit',
  'no-pr': 'No PR',
  chat: 'Chat',
  product: 'Product',
}

export const OFF_SECTION = (ended: Exclude<Mode, 'off'>): string =>
  `Session mode: off. ${LABEL[ended]} mode has ended; its rules no longer apply, even if the conversation still shows it on.`

export const MODE_NOTE = (current: Mode, ended: Exclude<Mode, 'off'> | null): string =>
  current !== 'off'
    ? `Session mode: ${LABEL[current]} is on. ${SECTION[current]}`
    : ended
      ? OFF_SECTION(ended)
      : 'Session mode: off.'

export const SUBAGENT_NOTE = (mode: Exclude<Mode, 'off'>): string =>
  `The main session is in ${LABEL[mode]} mode, and it applies to you too. ${SECTION[mode]} Tool calls that break it are denied.`

export type Active = Exclude<Mode, 'off'>

export type Scope = 'self' | 'subagents'

export type Held = { self: Active | null; subagents: Active | null }

export const AGENT_TOOL = 'mcp__session-modes__agent_mode'

export const AGENT_TOOL_DESCRIPTION =
  'Set a working mode for yourself (scope "self") or for your subagents (scope "subagents"); it applies at once, also to subagents already running, and subagents you start later get it in their task text. Modes: audit (read and report only), no-pr (no pull requests), chat (no push or PR), product (plan only, no code). "off" clears the mode you set in that scope. You can only add limits: a mode the user set with /mode stays in force, and the stricter rule always wins.'

export const AGENT_TOOL_SCHEMA = {
  type: 'object',
  properties: {
    mode: { type: 'string', enum: [...MODES] },
    scope: { type: 'string', enum: ['self', 'subagents'] },
  },
  required: ['mode', 'scope'],
}

export function parseScope(raw: unknown): Scope | undefined {
  return raw === 'self' || raw === 'subagents' ? raw : undefined
}

export const INHERITED_NOTE = (mode: Active): string =>
  `The agent that started you set ${LABEL[mode]} mode for its subagents, and it applies to you. ${SECTION[mode]} Tool calls that break it are denied.`

export const agentModeText = (wanted: Mode, scope: Scope, before: Active | null, user: Mode): string => {
  const kept = scope === 'self' && user !== 'off' ? ` The user's ${LABEL[user]} mode stays on.` : ''
  if (wanted === 'off') {
    if (!before) return `No mode was set for that scope.${kept}`
    return `Cleared the ${LABEL[before]} mode you set for ${scope === 'self' ? 'yourself' : 'your subagents'}.${kept}`
  }
  if (scope === 'self') return `You are now in ${LABEL[wanted]} mode. ${SECTION[wanted]}${kept}`
  return `Your subagents are now in ${LABEL[wanted]} mode, also those already running.`
}

export function claudeParts(held: Held | undefined): string | undefined {
  if (!held) return undefined
  const parts = [
    held.self ? `${LABEL[held.self]} for itself` : null,
    held.subagents ? `${LABEL[held.subagents]} for subagents` : null,
  ].filter((p): p is string => p !== null)
  return parts.length ? parts.join(' and ') : undefined
}

export const reword = (text: string, tail: string): string => text.replace('/mode off to leave.', tail)

// The skills that may write a plan outside the repo in product mode.
export const PLANNING = new Set(['vision', 'shape', 'tickets'])

// A prefix other than cj-stack means someone else's skill of the same name.
export function planningSkill(raw: string): boolean {
  const parts = raw.trim().replace(/^\//, '').split(':')
  return (parts.length === 1 || parts[0] === 'cj-stack') && PLANNING.has(parts[parts.length - 1])
}

const PR_CREATE = /\bgh\s+pr\s+create\b/
const PUSH = /\bgit\s+push\b/
const AUDIT_BASH = /\bgit\s+commit\b|\bgit\s+push\b|\bgh\s+pr\s+(create|merge)\b/
const WRITE_VERB =
  /^(create|save|update|delete|add|remove|set|edit|write|post|move|archive|close|reopen|assign|link|unlink|merge|upsert|patch|put|push|transition|submit|publish|batch)$/
// Tracker CLIs the shape adapters name; an MCP tool is judged by its name alone.
const TRACKER_CLI =
  /\bgh\s+(issue|project|label|milestone)\s+(create|edit|close|reopen|delete|comment|transfer|item-add|item-edit|item-archive|field-create|link)\b|\bgh\s+api\b.*(-X|--method)\s*(POST|PATCH|PUT|DELETE)\b|\bacli\s+jira\s+\S+\s+(create|edit|delete|transition|assign|comment|link)\b/
const PLAN_FILE = /\.(md|markdown)$/i
const HARMLESS_REDIRECT = /\d*>&\d+|\d*>>?\s*\/dev\/null/g
const FILE_REDIRECT = />>?\s*[^\s>&|;]/

export function redirectsToFile(command: string): boolean {
  return FILE_REDIRECT.test(command.replace(HARMLESS_REDIRECT, ''))
}

// mcp__server__create_issue or mcp__server__createIssue: any word of the tool's own name is a write verb.
export function writesOutside(tool: string, command: string): boolean {
  if (tool === 'Bash') return TRACKER_CLI.test(command)
  const name = /^mcp__.+?__(.+)$/.exec(tool)?.[1]
  if (!name) return false
  const words = name.replace(/([a-z0-9])([A-Z])/g, '$1_$2').toLowerCase().split(/[_\-.]+/)
  return words.some(w => WRITE_VERB.test(w))
}

function writesCode(tool: string, path: string, command: string): boolean {
  if (tool === 'Edit' || tool === 'Write' || tool === 'NotebookEdit') return !PLAN_FILE.test(path)
  if (tool !== 'Bash') return false
  const target = />>?\s*([^\s>&|;]+)/.exec(command.replace(HARMLESS_REDIRECT, ''))?.[1]
  return target !== undefined && !PLAN_FILE.test(target)
}

const INSTEAD: Record<Exclude<Mode, 'off'>, string> = {
  audit: 'report the change instead of making it',
  'no-pr': 'commit on the branch and leave the pull request to the user',
  chat: 'put the result in the reply instead',
  product: 'put the plan in the tracker or a Markdown plan file instead',
}

function isBlocked(mode: Exclude<Mode, 'off'>, tool: string, command: string, path: string): boolean {
  if (mode === 'product') {
    if (tool.endsWith('create_pull_request')) return true
    return writesCode(tool, path, command) || (tool === 'Bash' && (PR_CREATE.test(command) || PUSH.test(command)))
  }
  if (mode === 'audit') {
    if (tool === 'Edit' || tool === 'Write' || tool === 'NotebookEdit') return true
    return tool === 'Bash' && (AUDIT_BASH.test(command) || redirectsToFile(command))
  }
  if (tool.endsWith('create_pull_request')) return true
  if (tool !== 'Bash') return false
  return PR_CREATE.test(command) || (mode === 'chat' && PUSH.test(command))
}

export type Call = { tool: string; command?: string; path?: string; planned?: boolean }

export function verdict(mode: Mode, call: Call): string | undefined {
  const { tool, command = '', path = '', planned = false } = call
  if (mode === 'off') return undefined
  if (isBlocked(mode, tool, command, path)) return `${mode} mode is on: ${INSTEAD[mode]}; /mode off to leave.`
  if (mode === 'product' && !planned && writesOutside(tool, command)) {
    return 'product mode is on: load the planning skill for the level you are writing first (vision for the product, shape for a project, tickets for work items); /mode off to leave.'
  }
  return undefined
}

export function report(mode: Mode): string {
  return `Current mode: ${mode}. Modes: ${MODES.join(', ')}.`
}
