import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

function world(on: On, hookBlocks: () => boolean = () => true, extra: object = {}) {
  const state = { toasts: [] as string[], statuses: [] as (string | undefined)[] }
  on('classic.Stop', () => ({ ...(hookBlocks() ? { block: 'Not satisfied: keep going' } : {}), ...extra }) as never)
  on('ui.toast', (_$, e) => {
    state.toasts.push(e.text)
    return { value: undefined } as never
  })
  on('ui.status', (_$, e) => {
    state.statuses.push(e.text)
    return { value: undefined } as never
  })
  on('prompt.submit', (_$, e) => e as never)
  return state
}

const stop = ($: any) => $.classic.Stop({ stop_hook_active: true })
const submit = ($: any, kind = 'composer') => $.prompt.submit({ text: 'go', origin: { kind }, wait: false })
const last = (s: (string | undefined)[]) => s[s.length - 1]

test('continuations below the cap are allowed and counted', async ($, on) => {
  const w = world(on)
  expect((await stop($)).block).toBeDefined()
  expect((await stop($)).block).toBeDefined()
  expect(w.toasts).toEqual([])
  expect(last(w.statuses)).toBe('loop 2/3')
})

test('the stop is let through at the cap and the user is told', async ($, on) => {
  const w = world(on)
  for (let i = 0; i < 3; i++) await stop($)
  const r = await stop($)
  expect(r.block).toBeUndefined()
  expect(w.toasts).toEqual(['loop-brake: stopped after 3 forced continuations — reply to keep going'])
})

test('a stop let through clears the status line', async ($, on) => {
  const w = world(on)
  for (let i = 0; i < 4; i++) await stop($)
  expect(last(w.statuses)).toBeUndefined()
})

test('after a release the next streak starts from zero', async ($, on) => {
  const w = world(on)
  for (let i = 0; i < 4; i++) await stop($)
  expect((await stop($)).block).toBeDefined()
  expect(last(w.statuses)).toBe('loop 1/3')
})

test('a prompt from the user resets the streak', async ($, on) => {
  const w = world(on)
  await stop($)
  await stop($)
  await submit($)
  expect(last(w.statuses)).toBeUndefined()
  for (let i = 0; i < 3; i++) expect((await stop($)).block).toBeDefined()
  expect(w.toasts).toEqual([])
})

test('a prompt from the phone also resets the streak', async ($, on) => {
  const w = world(on)
  await stop($)
  await submit($, 'bridge')
  expect(last(w.statuses)).toBeUndefined()
})

test('a machine-injected prompt does not reset the streak', async ($, on) => {
  const w = world(on)
  await stop($)
  await submit($, 'sdk')
  expect(last(w.statuses)).toBe('loop 1/3')
  await stop($)
  expect(last(w.statuses)).toBe('loop 2/3')
})

test('the cap follows the maxContinuations option', { options: { maxContinuations: 1 } }, async ($, on) => {
  const w = world(on)
  expect((await stop($)).block).toBeDefined()
  expect((await stop($)).block).toBeUndefined()
  expect(w.toasts[0]).toContain('after 1 forced continuations')
})

test('an option above 20 falls back to 3', { options: { maxContinuations: 21 } }, async ($, on) => {
  world(on)
  for (let i = 0; i < 3; i++) expect((await stop($)).block).toBeDefined()
  expect((await stop($)).block).toBeUndefined()
})

test('an option below 1 falls back to 3', { options: { maxContinuations: 0 } }, async ($, on) => {
  world(on)
  for (let i = 0; i < 3; i++) expect((await stop($)).block).toBeDefined()
  expect((await stop($)).block).toBeUndefined()
})

test('a fractional option falls back to 3', { options: { maxContinuations: 2.5 } }, async ($, on) => {
  world(on)
  for (let i = 0; i < 3; i++) expect((await stop($)).block).toBeDefined()
  expect((await stop($)).block).toBeUndefined()
})

test('a normal stop with no hook blocking is untouched', async ($, on) => {
  const w = world(on, () => false)
  const r = await stop($)
  expect(r.block).toBeUndefined()
  expect(w.toasts).toEqual([])
  expect(w.statuses.filter(s => s !== undefined)).toEqual([])
})

test('a normal stop ends the streak', async ($, on) => {
  let blocks = true
  const w = world(on, () => blocks)
  await stop($)
  await stop($)
  blocks = false
  await stop($)
  expect(last(w.statuses)).toBeUndefined()
  blocks = true
  for (let i = 0; i < 3; i++) expect((await stop($)).block).toBeDefined()
})

test('a hook that stops the session outright is left alone', async ($, on) => {
  const w = world(on, () => false, { preventContinuation: true, stopReason: 'done' })
  const r = await stop($)
  expect(r.preventContinuation).toBe(true)
  expect(w.toasts).toEqual([])
})
