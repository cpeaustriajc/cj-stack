import type { Hook, Register } from 'claude-code'

type Api = Parameters<Hook<'classic.Stop'>>[0]

const MOD = 'hone-nudge'
const WEEK = 7 * 86_400_000
// Keep SHIPPED in step with the skills array of the cj-stack plugin in marketplace.json.
const SHIPPED = new Set([
  'work-planning', 'triage', 'project-knowledge', 'hone', 'break-it', 'ui-polish',
  'feature-files', 'playbooks', 'interrogate', 'commit', 'create-pr',
])
// Keep this detection in step with skills/knowledge/hone/scripts/corrections.py, which a separate plugin cannot import.
const CORRECTION = /^\s*(no\b|nope|why\b|stop\b|don'?t\b|do not\b|i already|i said|i meant|that's not|wrong|huh|wait\b|actually\b|\?\?)/i
const INTERRUPT = '[Request interrupted by user'
const COMMAND = /<command-name>\s*([^<\s]+)\s*<\/command-name>/

type Entry = { type?: string; isSidechain?: boolean; message?: { content?: unknown } }
type Block = { type?: string; text?: string; name?: string; id?: string; tool_use_id?: string; input?: { skill?: unknown }; content?: unknown }

// A prefix other than cj-stack means someone else's skill of the same name.
function shippedName(raw: string): string | undefined {
  const parts = raw.trim().replace(/^\//, '').split(':')
  const name = parts[parts.length - 1]
  const prefixOk = parts.length === 1 || parts[0] === 'cj-stack'
  return prefixOk && SHIPPED.has(name) ? name : undefined
}

function textOf(content: unknown): string {
  if (typeof content === 'string') return content
  if (!Array.isArray(content)) return ''
  return (content as Block[]).filter(b => b && b.type === 'text').map(b => b.text ?? '').join('\n')
}

function parse(line: string): Entry | undefined {
  try {
    const entry: unknown = JSON.parse(line)
    return entry && typeof entry === 'object' ? (entry as Entry) : undefined
  } catch {
    return undefined
  }
}

function rejected(result: string): boolean {
  return result.includes("doesn't want to proceed") || result.slice(0, 200).toLowerCase().includes('rejected')
}

function correctionsBySkill(transcript: string): Map<string, number> {
  const counts = new Map<string, number>()
  let active: string | undefined
  const hit = () => {
    if (active) counts.set(active, (counts.get(active) ?? 0) + 1)
  }
  for (const line of transcript.split('\n')) {
    const entry = parse(line)
    if (!entry || entry.isSidechain) continue
    const content = entry.message?.content
    const blocks = Array.isArray(content) ? (content as Block[]).filter(b => b && typeof b === 'object') : []
    if (entry.type === 'assistant') {
      for (const b of blocks) {
        if (b.type !== 'tool_use') continue
        if (b.name === 'Skill' && typeof b.input?.skill === 'string') active = shippedName(b.input.skill)
      }
      continue
    }
    if (entry.type !== 'user') continue
    const started = COMMAND.exec(textOf(content))
    if (started) {
      active = shippedName(started[1])
      continue
    }
    for (const b of blocks) {
      if (b.type !== 'tool_result') continue
      const result = typeof b.content === 'string' ? b.content : textOf(b.content)
      if (rejected(result)) hit()
    }
    const said = textOf(content)
    if (!said.trim() || said.startsWith('<') || said.length > 2500) continue
    if (said.includes(INTERRUPT) || CORRECTION.test(said)) hit()
  }
  return counts
}

async function stateDir($: Api): Promise<string | undefined> {
  const config = await $.env.get('CLAUDE_CONFIG_DIR')
  if (config) return `${config}/mod-state`
  const home = (await $.env.get('HOME')) || (await $.env.get('USERPROFILE'))
  return home ? `${home}/.claude/mod-state` : undefined
}

async function readNudged($: Api, path: string): Promise<string[]> {
  if (!(await $.fs.exists(path))) return []
  try {
    const parsed = JSON.parse(await $.fs.read(path)) as { nudged?: unknown }
    return Array.isArray(parsed.nudged) ? parsed.nudged.filter((s): s is string => typeof s === 'string') : []
  } catch (cause) {
    throw new Error(`${MOD}: state file is unreadable: ${path}`, { cause })
  }
}

async function pruneState($: Api): Promise<void> {
  try {
    const dir = await stateDir($)
    if (!dir || !(await $.fs.exists(dir))) return
    const now = await $.clock.now()
    const stale = (await $.fs.list(dir)).filter(
      f => f.kind === 'file' && f.name.endsWith(`.${MOD}.json`) && now - f.mtimeMs > WEEK,
    )
    if (stale.length > 0) await $.process.run(['rm', '-f', '--', ...stale.map(f => `${dir}/${f.name}`)])
  } catch (cause) {
    throw new Error(`${MOD}: could not prune old state files`, { cause })
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await pruneState($)
    return result
  })

  on('classic.Stop', async ($, e, next) => {
    const result = await next(e)
    if (result.block !== undefined || result.preventContinuation) return result

    let transcript: string
    try {
      transcript = await $.fs.read(e.transcript_path)
    } catch {
      return result
    }
    const found = [...correctionsBySkill(transcript)].filter(([, n]) => n > 0)
    if (found.length === 0) return result

    const dir = await stateDir($)
    if (!dir) return result
    const path = `${dir}/${e.session_id}.${MOD}.json`
    const nudged = await readNudged($, path)
    const fresh = found.filter(([skill]) => !nudged.includes(skill))
    if (fresh.length === 0) return result

    try {
      await $.fs.write(path, JSON.stringify({ v: 1, nudged: [...nudged, ...fresh.map(([s]) => s)] }))
    } catch (cause) {
      throw new Error(`${MOD}: could not record the nudge for this session`, { cause })
    }
    for (const [skill, n] of fresh) {
      $.ui.log(`${n} ${n === 1 ? 'correction' : 'corrections'} during ${skill}. Run /hone ${skill}?`)
    }
    return result
  })
}
