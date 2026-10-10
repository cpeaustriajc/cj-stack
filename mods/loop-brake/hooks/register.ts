import type { Hook, Register } from 'claude-code'

type Api = Parameters<Hook<'classic.Stop'>>[0]

const DEFAULT_CAP = 3

function capFrom(value: unknown): number {
  return typeof value === 'number' && Number.isInteger(value) && value >= 1 && value <= 20 ? value : DEFAULT_CAP
}

function reset($: Api): void {
  $.ui.status(undefined)
}

export const register: Register = (on, options) => {
  const cap = capFrom(options.maxContinuations)
  let streak = 0

  on('prompt.submit', async ($, e, next) => {
    if (e.origin.kind === 'composer' || e.origin.kind === 'bridge') {
      reset($)
      streak = 0
    }
    return next(e)
  })

  on('classic.Stop', async ($, e, next) => {
    const result = await next(e)
    if (result.block === undefined || result.preventContinuation) {
      if (streak > 0) reset($)
      streak = 0
      return result
    }
    if (streak >= cap) {
      reset($)
      streak = 0
      $.ui.toast(`loop-brake: stopped after ${cap} forced continuations — reply to keep going`)
      return { ...result, block: undefined }
    }
    streak++
    $.ui.status(`loop ${streak}/${cap}`)
    return result
  })
}
