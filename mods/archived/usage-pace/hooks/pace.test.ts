import { expect, test } from 'claude-code/testing'
import { formatTime, weeklyStatus } from './pace'

const HOUR = 3_600_000
const DAY = 24 * HOUR
const reset = new Date(2026, 9, 13, 16, 0).getTime()
const start = reset - 7 * DAY
const iso = new Date(reset).toISOString()

test('on pace for the reset shows when it lasts and the daily allowance', () => {
  expect(weeklyStatus(40, iso, start + 4 * DAY)).toBe('Week 40% · lasts to Tue 4:00 PM · 20%/day left')
})

test('a rate that runs dry before the reset names when', () => {
  expect(weeklyStatus(81, iso, start + 4 * DAY)).toBe('Week 81% · out ~Sun 2:31 PM · 6%/day left')
})

test('exactly on pace at the reset counts as lasting', () => {
  expect(weeklyStatus(50, iso, start + 3.5 * DAY)).toContain('lasts to Tue 4:00 PM')
})

test('nothing used shows the reset without a projection', () => {
  expect(weeklyStatus(0, iso, start + 4 * DAY)).toBe('Week 0% · resets Tue 4:00 PM')
})

test('under 12 hours into the window shows the reset without a projection', () => {
  expect(weeklyStatus(3, iso, start + 11 * HOUR)).toBe('Week 3% · resets Tue 4:00 PM')
  expect(weeklyStatus(3, iso, start + 12 * HOUR)).toContain('lasts to')
})

test('a full allowance shows the reset and no daily figure', () => {
  expect(weeklyStatus(100, iso, start + 4 * DAY)).toBe('Week 100% · resets Tue 4:00 PM')
  expect(weeklyStatus(103.5, iso, start + 4 * DAY)).toBe('Week 104% · resets Tue 4:00 PM')
})

test('a reset in the past or missing gives no text', () => {
  expect(weeklyStatus(40, iso, reset)).toBeUndefined()
  expect(weeklyStatus(40, iso, reset + HOUR)).toBeUndefined()
  expect(weeklyStatus(40, undefined, start)).toBeUndefined()
  expect(weeklyStatus(40, 'not a date', start)).toBeUndefined()
})

test('a clock behind the window start gives no projection', () => {
  expect(weeklyStatus(40, iso, start - 2 * DAY)).toBe('Week 40% · resets Tue 4:00 PM')
})

test('noon and midnight read 12 PM and 12 AM', () => {
  expect(formatTime(new Date(2026, 9, 13, 12, 0).getTime())).toBe('Tue 12:00 PM')
  expect(formatTime(new Date(2026, 9, 13, 0, 0).getTime())).toBe('Tue 12:00 AM')
})

test('minutes are zero-padded', () => {
  expect(formatTime(new Date(2026, 9, 13, 16, 5).getTime())).toBe('Tue 4:05 PM')
})
