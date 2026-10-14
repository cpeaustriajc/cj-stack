type Row = {
  label: string
  chip: string
  section: string
  instead: string
  lead: string
  detail: string
  hint: string
}

// Key order is the ladder, strictest first: need() compares positions.
export const LADDER = {
  readonly: {
    label: 'Read only',
    chip: 'planMode',
    section:
      'Read only mode: read and report only. Do not edit files, commit, push, open pull requests or write to trackers; list findings instead.',
    instead: 'report the change instead of making it',
    lead: 'Read and report only.',
    detail: 'Edits, commits, pushes, PRs and tracker writes are blocked.',
    hint: 'read and report only',
  },
  research: {
    label: 'Research',
    chip: 'merged',
    section:
      'Research mode: write no code. Put findings and plans in Markdown files or the tracker, and commit them if the work needs it. Do not push or open pull requests.',
    instead: 'put the finding or plan in a Markdown file or the tracker instead',
    lead: 'Notes, plans and tracker items only.',
    detail: 'Code edits, pushes and PRs are blocked.',
    hint: 'notes and plans, no code',
  },
  edit: {
    label: 'Edit',
    chip: 'ide',
    section:
      'Edit mode: edit and commit locally. Do not push or open pull requests; report the result in the reply and leave the push and the pull request to the user.',
    instead: 'commit locally and leave the push and the pull request to the user',
    lead: 'Edits and commits are allowed.',
    detail: 'Pushes and PRs are blocked.',
    hint: 'edit and commit, no push or PR',
  },
} as const satisfies Record<string, Row>

export type Active = keyof typeof LADDER

export type Mode = Active | 'off'

export const MODES: readonly Mode[] = [...(Object.keys(LADDER) as Active[]), 'off']

export function parseMode(args: string): Mode | undefined {
  const name = args.trim().toLowerCase()
  return (MODES as readonly string[]).includes(name) ? (name as Mode) : undefined
}

export const OFF_SECTION = (ended: Active): string =>
  `Session mode: off. ${LADDER[ended].label} mode has ended; its rules no longer apply, even if the conversation still shows it on.`

export const MODE_NOTE = (current: Mode, ended: Active | null): string =>
  current !== 'off'
    ? `Session mode: ${LADDER[current].label} is on. ${LADDER[current].section}`
    : ended
      ? OFF_SECTION(ended)
      : 'Session mode: off.'

export const SUBAGENT_NOTE = (mode: Active): string =>
  `The main session is in ${LADDER[mode].label} mode, and it applies to you too. ${LADDER[mode].section} Tool calls that break it are denied.`

export type Scope = 'self' | 'subagents'

export type Held = { self: Active | null; subagents: Active | null }

export const AGENT_TOOL = 'mcp__session-modes__agent_mode'

export const AGENT_TOOL_DESCRIPTION =
  'Set a working mode for yourself (scope "self") or for your subagents (scope "subagents"); it applies at once, also to subagents already running, and subagents you start later get it in their task text. Modes: readonly (read and report only), research (notes, plans and tracker items; no code), edit (edit and commit; no push or PR). "off" clears the mode you set in that scope. You can only add limits: a mode the user set with /mode stays in force, and the stricter rule always wins. Pick your own mode at the start of each user message, read with the conversation: readonly for a question, a review, an explanation or "do not change anything"; research for a plan, a spec, notes or tickets; edit for a code or config change; off only when the message asks you to push, or to open or merge a pull request. A short reply such as "yes" or "go ahead" takes the mode of the work it approves.'

export const CHECK_NOTE = (own: Active | null): string =>
  `Session mode check: pick your own mode for this message, as agent_mode describes. Now: ${own ?? 'off'}. If your pick differs, call agent_mode with that mode and scope self before any other tool call.`

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
  `The agent that started you set ${LADDER[mode].label} mode for its subagents, and it applies to you. ${LADDER[mode].section} Tool calls that break it are denied.`

export const agentModeText = (wanted: Mode, scope: Scope, before: Active | null, user: Mode): string => {
  const kept = scope === 'self' && user !== 'off' ? ` The user's ${LADDER[user].label} mode stays on.` : ''
  if (wanted === 'off') {
    if (!before) return `No mode was set for that scope.${kept}`
    return `Cleared the ${LADDER[before].label} mode you set for ${scope === 'self' ? 'yourself' : 'your subagents'}.${kept}`
  }
  if (scope === 'self') return `You are now in ${LADDER[wanted].label} mode. ${LADDER[wanted].section}${kept}`
  return `Your subagents are now in ${LADDER[wanted].label} mode, also those already running.`
}

export function claudeParts(held: Held | undefined): string | undefined {
  if (!held) return undefined
  const parts = [
    held.self ? `${LADDER[held.self].label} for itself` : null,
    held.subagents ? `${LADDER[held.subagents].label} for subagents` : null,
  ].filter((p): p is string => p !== null)
  return parts.length ? parts.join(' and ') : undefined
}

export const reword = (text: string, tail: string): string => text.replace('/mode off to leave.', tail)

const COMMIT = /\bgit\s+commit\b/
const PUBLISH = /\bgit\s+push\b|\bgh\s+pr\s+(create|merge)\b/
const GH_API = /\bgh\s+api\b/
const PULLS_PATH = /\/pulls\b/
const API_WRITE = /(?:-X|--method)[\s=]*(?:POST|PATCH|PUT|DELETE)\b|\s(?:-f|-F|--field|--raw-field|--input)(?=[\s=]|$)/i
const API_GET = /(?:-X|--method)[\s=]*GET\b/i
const WRITE_VERB =
  /^(create|save|update|delete|add|remove|set|edit|write|post|move|archive|close|reopen|assign|link|unlink|merge|upsert|patch|put|push|transition|submit|publish|batch)$/
// Tracker CLIs the shape adapters name; an MCP tool is judged by its name alone.
const TRACKER_CLI =
  /\bgh\s+(issue|project|label|milestone)\s+(create|edit|close|reopen|delete|comment|transfer|item-add|item-edit|item-archive|field-create|link)\b|\bgh\s+api\b.*(-X|--method)\s*(POST|PATCH|PUT|DELETE)\b|\bacli\s+jira\s+\S+\s+(create|edit|delete|transition|assign|comment|link)\b/
const PLAN_FILE = /\.(md|markdown)$/i
const HARMLESS_REDIRECT = /\d*>&\d+|\d*>>?\s*\/dev\/null/g
const REDIRECT_TARGET = />>?\s*([^\s>&|;]+)/g
const PART_SPLIT = /&&|\|\|?|;|\n/

const top = (needs: Mode[]): Mode => needs.reduce((a, b) => (MODES.indexOf(b) > MODES.indexOf(a) ? b : a), 'readonly')

function bashPartNeed(part: string): Mode {
  const pullsWrite = GH_API.test(part) && PULLS_PATH.test(part) && API_WRITE.test(part) && !API_GET.test(part)
  if (PUBLISH.test(part) || pullsWrite) return 'off'
  const targets = [...part.replace(HARMLESS_REDIRECT, '').matchAll(REDIRECT_TARGET)].map(m => m[1])
  if (targets.some(t => !PLAN_FILE.test(t))) return 'edit'
  return targets.length > 0 || COMMIT.test(part) || TRACKER_CLI.test(part) ? 'research' : 'readonly'
}

// mcp__server__create_issue or mcp__server__createIssue: any word of the tool's own name is a verb.
function mcpNeed(tool: string): Mode {
  const name = /^mcp__.+?__(.+)$/.exec(tool)?.[1]
  if (!name) return 'readonly'
  const words = name.replace(/([a-z0-9])([A-Z])/g, '$1_$2').toLowerCase().split(/[_\-.]+/)
  const writes = words.some(w => WRITE_VERB.test(w))
  if (words.includes('push') || (writes && words.includes('pull') && words.includes('request'))) return 'off'
  return writes ? 'research' : 'readonly'
}

export type Call = { tool: string; command?: string; path?: string }

export function need({ tool, command = '', path = '' }: Call): Mode {
  if (tool === 'Edit' || tool === 'Write' || tool === 'NotebookEdit') return PLAN_FILE.test(path) ? 'research' : 'edit'
  if (tool === 'Bash') return top(command.replace(/\\\n/g, ' ').split(PART_SPLIT).map(bashPartNeed))
  return mcpNeed(tool)
}

export function verdict(mode: Mode, call: Call): string | undefined {
  if (mode === 'off' || MODES.indexOf(need(call)) <= MODES.indexOf(mode)) return undefined
  return `${mode} mode is on: ${LADDER[mode].instead}; /mode off to leave.`
}

export function report(mode: Mode): string {
  return `Current mode: ${mode}. Modes: ${MODES.join(', ')}. Also: clear, agents on, agents off.`
}

export const CLEARED_NOTE = (parts: string): string =>
  `Session mode: the user cleared the modes you set (${parts}). They no longer apply.`

export const AGENTS_OFF_NOTE = 'Session mode: the user turned off agent_mode. Do not call it.'

export const AGENTS_ON_NOTE = 'Session mode: the user turned agent_mode back on.'

export const AGENTS_OFF_DENY = 'The user turned off agent modes with /mode agents off.'

export type Override = 'clear' | 'agents-on' | 'agents-off' | 'agents-invalid'

export function parseOverride(args: string): Override | undefined {
  const words = args.trim().toLowerCase().split(/\s+/)
  if (words.length === 1 && words[0] === 'clear') return 'clear'
  if (words[0] !== 'agents') return undefined
  if (words.length === 2 && words[1] === 'on') return 'agents-on'
  if (words.length === 2 && words[1] === 'off') return 'agents-off'
  return 'agents-invalid'
}

export const holdsAny = (all: Record<string, Held>): boolean =>
  Object.values(all).some(h => h.self !== null || h.subagents !== null)
