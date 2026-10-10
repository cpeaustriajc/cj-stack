import { atom, read, update } from 'claude-code'
import type { Hook, Register } from 'claude-code'
import { SECTION, parseMode, report, verdict } from './modes'
import type { Mode } from './modes'

type Api = Parameters<Hook<'session.start'>>[0]

const MOD = 'session-modes'
const WEEK = 7 * 86_400_000

async function stateDir($: Api): Promise<string | undefined> {
  const config = await $.env.get('CLAUDE_CONFIG_DIR')
  if (config) return `${config}/mod-state`
  const home = (await $.env.get('HOME')) || (await $.env.get('USERPROFILE'))
  return home ? `${home}/.claude/mod-state` : undefined
}

async function remove($: Api, paths: string[]): Promise<void> {
  if (paths.length === 0) return
  await $.process.run(['rm', '-f', '--', ...paths])
}

export async function publishState($: Api, mode: string): Promise<void> {
  try {
    const dir = await stateDir($)
    if (!dir) return
    const path = `${dir}/${await $.session.id()}.${MOD}.json`
    await $.fs.write(path, JSON.stringify({ v: 1, mode: mode === 'off' ? null : mode }))
  } catch (cause) {
    throw new Error(`${MOD}: could not publish state for the status line`, { cause })
  }
}

export async function pruneState($: Api): Promise<void> {
  try {
    const dir = await stateDir($)
    if (!dir || !(await $.fs.exists(dir))) return
    const now = await $.clock.now()
    const stale = (await $.fs.list(dir)).filter(
      f => f.kind === 'file' && f.name.endsWith(`.${MOD}.json`) && now - f.mtimeMs > WEEK,
    )
    await remove($, stale.map(f => `${dir}/${f.name}`))
  } catch (cause) {
    throw new Error(`${MOD}: could not prune old state files`, { cause })
  }
}

const mode = atom({ plugin: 'session-modes', key: 'mode' } as const, 'off' as Mode)
const SECTION_ID = 'session-modes:mode'

const STATUS: Record<Exclude<Mode, 'off'>, string> = {
  audit: 'audit — read and report only',
  'no-pr': 'no-pr — no pull requests',
  chat: 'chat — answer here, no PR or push',
}

async function drawStatus($: Api, current: Mode): Promise<void> {
  const surfaces = await $.session.surfaces()
  const shown = current !== 'off' && surfaces.some(s => s !== 'terminal')
  await $.ui.status(shown ? STATUS[current as Exclude<Mode, 'off'>] : undefined)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    if (e.isInteractive === false) return result
    await $.command.register({ name: 'mode', description: 'Set the session mode: audit, no-pr, chat or off' })
    const current = await read($, mode)
    await drawStatus($, current)
    if (current !== 'off') await publishState($, current)
    await pruneState($)
    return result
  })

  on('session.attach', async ($, e, next) => {
    const result = await next(e)
    await drawStatus($, await read($, mode))
    return result
  })

  on('session.detach', async ($, e, next) => {
    const result = await next(e)
    await drawStatus($, await read($, mode))
    return result
  })

  on('command.run', { command: 'mode' }, async ($, e) => {
    const wanted = e.args.trim() === '' ? undefined : parseMode(e.args)
    if (e.args.trim() === '') return { text: report(await read($, mode)) }
    if (!wanted) return { text: `Unknown mode "${e.args.trim()}". ${report(await read($, mode))}` }
    await update($, mode, () => wanted)
    await drawStatus($, wanted)
    await publishState($, wanted)
    return { text: wanted === 'off' ? 'Mode off.' : `Mode ${wanted} on.` }
  })

  on('tool.call', async ($, e, next) => {
    const command = e.tool === 'Bash' && typeof (e as { command?: unknown }).command === 'string' ? (e as { command: string }).command : ''
    const deny = verdict(await read($, mode), e.tool, command)
    return deny ? { deny } : next(e)
  })

  on('prompt.compose', async ($, e, next) => {
    const result = await next(e)
    const current = await read($, mode)
    if (current === 'off') return result
    return { sections: [...result.sections, { id: SECTION_ID, text: SECTION[current], scope: 'session' }] }
  })
}
