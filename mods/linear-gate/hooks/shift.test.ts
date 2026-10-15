import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

const MANILA = { timeZone: 'Asia/Manila' }
// MP-170 was filed by a headless run at about 20:35 Manila time, after the shift.
const MP_170_FILED = Date.UTC(2026, 9, 15, 12, 35)
const at = (h: number, m = 0) => Date.UTC(2026, 9, 15, h - 8, m)

function world(on: On, now: number | (() => number), surfaces: readonly string[] = ['terminal']) {
  const asked: string[] = []
  const ran: string[] = []
  on('clock.now', () => ({ value: typeof now === 'number' ? now : now() }) as never)
  on('ui.toast', () => ({ value: undefined }) as never)
  on('session.surfaces', () => ({ value: surfaces }) as never)
  on('ui.render', { component: 'AskUserQuestion' }, () => ({ type: 'engine', ref: 0 }) as never)
  on('tool.call', (_$, e) => {
    if (e.tool === 'AskUserQuestion') {
      asked.push((e as { questions: { question: string }[] }).questions[0].question)
      return { deny: 'dismissed' } as never
    }
    ran.push(e.tool)
    return { result: 'ok', text: 'ok' } as never
  })
  return { asked, ran }
}

const create = { tool: 'mcp__linear-server__save_issue', title: 'Agent guidance', team: 'MP' }
const cancel = { tool: 'mcp__linear-server__save_issue', id: 'MP-170', state: 'Canceled' }
const read = { tool: 'mcp__linear-server__get_issue', id: 'MP-170' }

test('the headless run that filed MP-170 off shift is denied', { options: MANILA }, async ($, on) => {
  const w = world(on, MP_170_FILED, [])
  const out = await $.tool.call(create as never)
  expect(w.ran).toEqual([])
  expect(out.deny).toContain('off shift')
})

test('an off-shift write in a terminal is denied without a dialog', { options: MANILA }, async ($, on) => {
  const w = world(on, at(21))
  const out = await $.tool.call(create as never)
  expect(w.asked).toEqual([])
  expect(w.ran).toEqual([])
  expect(out.deny).toContain('draft it in the chat')
})

test('an off-shift read passes', { options: MANILA }, async ($, on) => {
  const w = world(on, at(23))
  await $.tool.call(read as never)
  expect(w.ran).toEqual([read.tool])
})

test('an on-shift create goes to the host without a dialog', { options: MANILA }, async ($, on) => {
  const w = world(on, at(10))
  const out = await $.tool.call(create as never)
  expect(w.asked).toEqual([])
  expect(w.ran).toEqual([create.tool])
  expect(out.deny).toBe(undefined)
})

test('an on-shift cancel still asks', { options: MANILA }, async ($, on) => {
  const w = world(on, at(10))
  await $.tool.call(cancel as never)
  expect(w.asked.length).toBe(1)
  expect(w.ran).toEqual([])
})

test('onShift host asks nothing, even for a cancel', { options: { ...MANILA, onShift: 'host' } }, async ($, on) => {
  const w = world(on, at(10))
  await $.tool.call(cancel as never)
  expect(w.asked).toEqual([])
  expect(w.ran).toEqual([cancel.tool])
})

test('onShift ask asks for every write', { options: { ...MANILA, onShift: 'ask' } }, async ($, on) => {
  const w = world(on, at(10))
  await $.tool.call(create as never)
  expect(w.asked.length).toBe(1)
})

test('09:00 is on shift and 18:00 is off', { options: MANILA }, async ($, on) => {
  let now = at(9)
  const w = world(on, () => now)
  await $.tool.call(create as never)
  now = at(18)
  const out = await $.tool.call(create as never)
  expect(w.ran).toEqual([create.tool])
  expect(out.deny).toContain('off shift')
})

test('the shift is read in the configured time zone', { options: { timeZone: 'UTC' } }, async ($, on) => {
  const w = world(on, Date.UTC(2026, 9, 15, 12, 35))
  await $.tool.call(create as never)
  expect(w.ran).toEqual([create.tool])
})

test('a shift that crosses midnight', { options: { ...MANILA, shiftStart: '22:00', shiftEnd: '06:00' } }, async ($, on) => {
  const w = world(on, at(23))
  await $.tool.call(create as never)
  expect(w.ran).toEqual([create.tool])
})

test('a bad hour falls back to 09:00-18:00', { options: { ...MANILA, shiftStart: '9am', shiftEnd: '25:00' } }, async ($, on) => {
  const w = world(on, at(20))
  const out = await $.tool.call(create as never)
  expect(w.ran).toEqual([])
  expect(out.deny).toContain('09:00-18:00')
})
