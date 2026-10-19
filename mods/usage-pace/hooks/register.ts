import type { Hook, Register } from 'claude-code'
import { weeklyStatus } from './pace'

type Api = Parameters<Hook<'session.start'>>[0]

async function show($: Api): Promise<void> {
  const surfaces = await $.session.surfaces()
  if (!surfaces.some(s => s !== 'terminal')) {
    $.ui.status(undefined)
    return
  }
  const { rateLimits } = await $.session.usage()
  const week = rateLimits.find(r => r.kind === 'seven_day')
  const text = week && weeklyStatus(week.percentUsed, week.resetsAt, await $.clock.now())
  $.ui.status(text)
}

async function showOrClear($: Api): Promise<void> {
  try {
    await show($)
  } catch (cause) {
    $.ui.status(undefined)
    throw new Error('usage-pace: could not read weekly usage', { cause })
  }
}

export const register: Register = on => {
  let timer: { cancel: () => void } | undefined

  on('session.start', async ($, e, next) => {
    const result = await next(e)
    if (e.isInteractive === false) return result
    timer?.cancel()
    timer = $.clock.every(60_000, () => {
      show($).catch(() => $.ui.status(undefined))
    })
    await showOrClear($)
    return result
  })

  on('session.measure', async ($, e, next) => {
    const result = await next(e)
    if (e.changed.includes('rateLimits')) await showOrClear($)
    return result
  })

  on('session.attach', async ($, e, next) => {
    const result = await next(e)
    await showOrClear($)
    return result
  })

  on('session.detach', async ($, e, next) => {
    const result = await next(e)
    await showOrClear($)
    return result
  })
}
