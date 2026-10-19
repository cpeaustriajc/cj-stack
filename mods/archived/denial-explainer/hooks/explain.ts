const DANGEROUS = [
  /(^|[\s;&|(])rm(\s|$)/,
  /(^|[\s;&|(])sudo(\s|$)/,
  /\bgit\s+push\b.*(\s-f\b|--force)/,
  /\|\s*(sudo\s+)?(ba|z|da)?sh\b/,
]
const PLAIN_WORD = /^[\w./@:=+-]+$/
const MAX_ARG = 60

export type Denial = { tool: string; input: unknown; reason: string }

export function isClassifier(reason: string): boolean {
  return /classifier/i.test(reason) || /\[[^\]]+\]/.test(reason)
}

export function ruleName(reason: string): string {
  return reason.match(/\[([^\]]+)\]/)?.[1] ?? 'auto mode'
}

function field(input: unknown, key: string): string | undefined {
  const value = (input as Record<string, unknown> | null)?.[key]
  return typeof value === 'string' ? value : undefined
}

export function shortArg({ tool, input }: Denial): string {
  const raw =
    tool === 'Bash' ? field(input, 'command') : tool === 'WebFetch' ? field(input, 'url') : field(input, 'file_path')
  if (!raw) return ''
  const one = raw.replace(/\s+/g, ' ').trim()
  return one.length > MAX_ARG ? `${one.slice(0, MAX_ARG - 1)}…` : one
}

function bashRule(command: string | undefined): string | undefined {
  if (!command || DANGEROUS.some(d => d.test(command))) return undefined
  const words = command.trim().split(/\s+/).slice(0, 2)
  if (!words.every(w => PLAIN_WORD.test(w))) return undefined
  return `Bash(${words.join(' ')}:*)`
}

function domain(url: string | undefined): string | undefined {
  if (!url) return undefined
  try {
    return new URL(url).hostname || undefined
  } catch {
    return undefined
  }
}

export function allowRule({ tool, input }: Denial): string | undefined {
  if (tool === 'Bash') return bashRule(field(input, 'command'))
  if (tool.startsWith('mcp__')) return tool
  if (tool === 'WebFetch') {
    const host = domain(field(input, 'url'))
    return host && `WebFetch(domain:${host})`
  }
  if (tool === 'Edit' || tool === 'Write') {
    const path = field(input, 'file_path')
    return path && !path.includes('"') ? `${tool}(${path})` : undefined
  }
  return undefined
}

export function ordinal(n: number): string {
  const tens = n % 100
  if (tens >= 11 && tens <= 13) return `${n}th`
  return `${n}${({ 1: 'st', 2: 'nd', 3: 'rd' } as Record<number, string>)[n % 10] ?? 'th'}`
}

export function explanation(denial: Denial, count: number): string {
  const arg = shortArg(denial)
  const what = arg ? `${denial.tool} ${arg}` : denial.tool
  const nth = count >= 2 ? ` (${ordinal(count)} this session)` : ''
  const rule = allowRule(denial)
  const allow = rule ? `/permissions add "${rule}"` : 'no allow rule suggested'
  return `Blocked by ${ruleName(denial.reason)}: ${what}${nth}\nAllow it: ${allow}`
}
