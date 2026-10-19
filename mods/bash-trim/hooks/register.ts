import type { Register } from 'claude-code'

const MOD = 'bash-trim'
const TRIGGER = 10_000
const HEAD = 2_000
const TAIL = 3_000

const READ_LIKE = [
  /^(cat|head|tail|jq)\b/,
  /^sed\s+(-\S+\s+)*-n\b/,
  /^git\s+(diff|show)\b/,
  /^git\s+log\b.*\s-p\b/,
  /^gh\s+(pr|api|issue)\b/,
]

const group = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ',')

export function isReadLike(command: string): boolean {
  let rest = command.trim()
  for (let m; (m = /^cd\s+[^;&|]*&&\s*/.exec(rest)); ) rest = rest.slice(m[0].length)
  return READ_LIKE.some(re => re.test(rest))
}

export function trim(text: string): string {
  if (text.length <= TRIGGER) return text
  const cut = text.slice(HEAD, text.length - TAIL)
  const lines = cut.split('\n').length - 1
  return `${text.slice(0, HEAD)}\n[… ${group(lines)} lines, ${group(cut.length)} characters cut …]\n${text.slice(-TAIL)}`
}

export const register: Register = on => {
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    const ran = await next(e)
    if (ran.deny !== undefined || ran.isError) return ran
    try {
      const out = ran.result
      if (out.interrupted || out.isImage || out.persistedOutputPath || out.backgroundTaskId || isReadLike(e.command)) return ran
      const stdout = trim(out.stdout)
      return stdout === out.stdout ? ran : { result: { ...out, stdout }, context: ran.context }
    } catch (err) {
      $.ui.toast(`${MOD}: left this output whole (${(err as Error).message})`)
      return ran
    }
  }).catch(($, e, next) => next(e))
}
