export type Mode = 'off' | 'audit' | 'no-pr' | 'chat'

export const MODES = ['audit', 'no-pr', 'chat', 'off'] as const

export function parseMode(args: string): Mode | undefined {
  const name = args.trim().toLowerCase()
  return (MODES as readonly string[]).includes(name) ? (name as Mode) : undefined
}

export const SECTION: Record<Exclude<Mode, 'off'>, string> = {
  audit: 'Audit mode: read and report only. Do not edit files, commit, push or open pull requests; list findings instead.',
  'no-pr': 'No-PR mode: do not open a pull request. Commit on the branch and say so in the reply.',
  chat: 'Chat mode: do not open a pull request or push. Put the result in the reply, not in a pull request.',
}

const PR_CREATE = /\bgh\s+pr\s+create\b/
const PUSH = /\bgit\s+push\b/
const AUDIT_BASH = /\bgit\s+commit\b|\bgit\s+push\b|\bgh\s+pr\s+(create|merge)\b/
const HARMLESS_REDIRECT = /\d*>&\d+|\d*>>?\s*\/dev\/null/g
const FILE_REDIRECT = />>?\s*[^\s>&|;]/

export function redirectsToFile(command: string): boolean {
  return FILE_REDIRECT.test(command.replace(HARMLESS_REDIRECT, ''))
}

const INSTEAD: Record<Exclude<Mode, 'off'>, string> = {
  audit: 'report the change instead of making it',
  'no-pr': 'commit on the branch and leave the pull request to the user',
  chat: 'put the result in the reply instead',
}

function isBlocked(mode: Exclude<Mode, 'off'>, tool: string, command: string): boolean {
  if (mode === 'audit') {
    if (tool === 'Edit' || tool === 'Write' || tool === 'NotebookEdit') return true
    return tool === 'Bash' && (AUDIT_BASH.test(command) || redirectsToFile(command))
  }
  if (tool.endsWith('create_pull_request')) return true
  if (tool !== 'Bash') return false
  return PR_CREATE.test(command) || (mode === 'chat' && PUSH.test(command))
}

export function verdict(mode: Mode, tool: string, command: string): string | undefined {
  if (mode === 'off' || !isBlocked(mode, tool, command)) return undefined
  return `${mode} mode is on: ${INSTEAD[mode]}; /mode off to leave.`
}

export function report(mode: Mode): string {
  return `Current mode: ${mode}. Modes: ${MODES.join(', ')}.`
}
