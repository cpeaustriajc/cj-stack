import type { Hook, Register } from 'claude-code'

type Api = Parameters<Hook<'classic.Stop'>>[0]

const MOD = 'loop-brake'
const WEEK = 7 * 86_400_000
const DEFAULT_CAP = 3

function capFrom(value: unknown): number {
  return typeof value === 'number' && Number.isInteger(value) && value >= 1 && value <= 20 ? value : DEFAULT_CAP
}

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

async function publishState($: Api, streak: number, cap: number): Promise<void> {
  try {
    const dir = await stateDir($)
    if (!dir) return
    const path = `${dir}/${await $.session.id()}.${MOD}.json`
    await $.fs.write(path, JSON.stringify({ v: 1, streak, cap }))
  } catch (cause) {
    throw new Error(`${MOD}: could not publish state for the status line`, { cause })
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
    await remove($, stale.map(f => `${dir}/${f.name}`))
  } catch (cause) {
    throw new Error(`${MOD}: could not prune old state files`, { cause })
  }
}

async function drawStatus($: Api, streak: number, cap: number): Promise<void> {
  const surfaces = await $.session.surfaces()
  const shown = streak > 0 && surfaces.some(s => s !== 'terminal')
  await $.ui.status(shown ? `${streak} of ${cap} forced continuations` : undefined)
}

async function show($: Api, streak: number, cap: number): Promise<void> {
  await drawStatus($, streak, cap)
  await publishState($, streak, cap)
}

async function clearStreak($: Api, streak: number, cap: number): Promise<void> {
  if (streak > 0) await show($, 0, cap)
}

export const register: Register = (on, options) => {
  const cap = capFrom(options.maxContinuations)
  let streak = 0

  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await pruneState($)
    return result
  })

  on('session.attach', async ($, e, next) => {
    const result = await next(e)
    await drawStatus($, streak, cap)
    return result
  })

  on('session.detach', async ($, e, next) => {
    const result = await next(e)
    await drawStatus($, streak, cap)
    return result
  })

  on('prompt.submit', async ($, e, next) => {
    if (e.origin.kind === 'composer' || e.origin.kind === 'bridge') {
      await clearStreak($, streak, cap)
      streak = 0
    }
    return next(e)
  })

  on('classic.Stop', async ($, e, next) => {
    const result = await next(e)
    if (result.block === undefined || result.preventContinuation) {
      await clearStreak($, streak, cap)
      streak = 0
      return result
    }
    if (streak >= cap) {
      await clearStreak($, streak, cap)
      streak = 0
      $.ui.toast(`loop-brake: stopped after ${cap} forced continuations — reply to keep going`)
      return { ...result, block: undefined }
    }
    streak++
    await show($, streak, cap)
    return result
  })
}
