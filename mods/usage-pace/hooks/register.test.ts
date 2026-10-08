import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

const DAY = 86_400_000
const reset = new Date(2026, 9, 13, 16, 0).getTime()
const start = reset - 7 * DAY

type Limit = { kind: string; percentUsed: number; resetsAt?: string }

function world(on: On, limits: Limit[] | 'throw') {
  const state = { limits, reads: 0, statuses: [] as (string | undefined)[] }
  const clock = mock.clock(on, { now: start + 4 * DAY })
  on('session.start', (_$, e) => e as never)
  on('session.measure', (_$, e) => ({ changed: e.changed }) as never)
  on('session.usage', () => {
    state.reads++
    if (state.limits === 'throw') return { deny: 'usage unavailable' } as never
    return { value: { startedAt: 0, context: {}, rateLimits: state.limits } } as never
  })
  on('ui.status', (_$, e) => {
    state.statuses.push(e.text)
    return { value: undefined } as never
  })
  return { state, clock }
}

const seven = (percentUsed: number): Limit => ({ kind: 'seven_day', percentUsed, resetsAt: new Date(reset).toISOString() })
const last = (s: (string | undefined)[]) => s[s.length - 1]

test('session start shows the weekly pace', async ($, on) => {
  const { state } = world(on, [seven(40)])
  await $.session.start({ cwd: '/tmp', isInteractive: true } as never)
  expect(last(state.statuses)).toBe('Week 40% · lasts to Tue 4:00 PM · 20%/day left')
})

test('a non-interactive session reads nothing and draws nothing', async ($, on) => {
  const { state, clock } = world(on, [seven(40)])
  await $.session.start({ cwd: '/tmp', isInteractive: false } as never)
  await clock.advance(120_000)
  expect(state.reads).toBe(0)
  expect(state.statuses).toEqual([])
})

test('no seven-day reading clears the status', async ($, on) => {
  const { state } = world(on, [{ kind: 'five_hour', percentUsed: 30 }])
  await $.session.start({ cwd: '/tmp', isInteractive: true } as never)
  expect(state.statuses).toEqual([undefined])
})

test('a new reading from a measured turn updates the status', async ($, on) => {
  const { state } = world(on, [])
  await $.session.start({ cwd: '/tmp', isInteractive: true } as never)
  state.limits = [seven(81)]
  await $.session.measure({ changed: ['rateLimits'] } as never)
  expect(last(state.statuses)).toBe('Week 81% · out ~Sun 2:31 PM · 6%/day left')
})

test('a measurement that moved only the context does not re-read usage', async ($, on) => {
  const { state } = world(on, [seven(40)])
  await $.session.start({ cwd: '/tmp', isInteractive: true } as never)
  const before = state.reads
  await $.session.measure({ changed: ['context'] } as never)
  expect(state.reads).toBe(before)
})

test('the status refreshes every 60 seconds as time passes', async ($, on) => {
  const { state, clock } = world(on, [seven(40)])
  await $.session.start({ cwd: '/tmp', isInteractive: true } as never)
  const before = state.reads
  await clock.advance(60_000)
  expect(state.reads).toBe(before + 1)
  expect(last(state.statuses)).toContain('Week 40%')
})

test('a second session start replaces the timer instead of doubling it', async ($, on) => {
  const { state, clock } = world(on, [seven(40)])
  await $.session.start({ cwd: '/tmp', isInteractive: true } as never)
  await $.session.start({ cwd: '/tmp', isInteractive: true } as never)
  const before = state.reads
  await clock.advance(60_000)
  expect(state.reads).toBe(before + 1)
})

test('a failing timer read clears the status', async ($, on) => {
  const { state, clock } = world(on, [seven(40)])
  await $.session.start({ cwd: '/tmp', isInteractive: true } as never)
  state.limits = 'throw'
  await clock.advance(60_000)
  expect(last(state.statuses)).toBeUndefined()
  expect(state.statuses.length).toBeGreaterThan(1)
})

test('a failing read in a hook clears the status', async ($, on) => {
  const { state } = world(on, 'throw')
  await $.session.start({ cwd: '/tmp', isInteractive: true } as never)
  expect(state.statuses).toEqual([undefined])
})
