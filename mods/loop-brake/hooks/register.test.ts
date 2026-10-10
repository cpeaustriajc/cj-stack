import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

type Surface = 'terminal' | 'desktop'

function world(on: On, hookBlocks: () => boolean = () => true, extra: object = {}, surfaces: Surface[] = ['desktop']) {
  const state = {
    toasts: [] as string[],
    statuses: [] as (string | undefined)[],
    surfaces,
    writes: [] as { path: string; text: string }[],
    removed: [] as string[],
    failRm: false,
    files: [] as { name: string; kind: string; mtimeMs: number }[],
    env: { HOME: '/home/cj' } as Record<string, string | undefined>,
    now: 100 * 86_400_000,
  }
  on('session.id', () => ({ value: 'sess1' }) as never)
  on('session.surfaces', () => ({ value: state.surfaces }) as never)
  on('session.start', (_$, e) => e as never)
  on('session.attach', (_$, e) => e as never)
  on('session.detach', (_$, e) => e as never)
  on('env.get', (_$, e) => ({ value: state.env[(e as { name: string }).name] }) as never)
  on('clock.now', () => ({ value: state.now }) as never)
  on('fs.exists', () => ({ value: true }) as never)
  on('fs.list', () => ({ value: state.files }) as never)
  on('fs.write', (_$, e) => (state.writes.push(e as never), { value: undefined }) as never)
  on('process.run', (_$, e) => {
    if (state.failRm) return { deny: 'no' } as never
    state.removed.push(...(e as { argv: string[] }).argv.slice(3))
    return { value: { exitCode: 0, stdout: '', stderr: '' } } as never
  })
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
  expect(last(w.statuses)).toBe('2 of 3 forced continuations')
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
  expect(last(w.statuses)).toBe('1 of 3 forced continuations')
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
  expect(last(w.statuses)).toBe('1 of 3 forced continuations')
  await stop($)
  expect(last(w.statuses)).toBe('2 of 3 forced continuations')
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

const DIR = '/home/cj/.claude/mod-state'
const FILE = `${DIR}/sess1.loop-brake.json`
const DAY = 86_400_000
const lastWrite = (w: { writes: { path: string; text: string }[] }) => w.writes[w.writes.length - 1]
const startSession = ($: any) => $.session.start({ cwd: '/tmp', isInteractive: true })

test('each forced continuation writes the streak and cap for the status line', async ($, on) => {
  const w = world(on)
  await stop($)
  expect(lastWrite(w).path).toBe(FILE)
  expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, streak: 1, cap: 3 })
  await stop($)
  expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, streak: 2, cap: 3 })
})

test('the file carries the configured cap', { options: { maxContinuations: 5 } }, async ($, on) => {
  const w = world(on)
  await stop($)
  expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, streak: 1, cap: 5 })
})

test('CLAUDE_CONFIG_DIR moves the state directory', async ($, on) => {
  const w = world(on)
  w.env.CLAUDE_CONFIG_DIR = '/cfg'
  await stop($)
  expect(lastWrite(w).path).toBe('/cfg/mod-state/sess1.loop-brake.json')
})

test('a stop let through at the cap removes the file', async ($, on) => {
  const w = world(on)
  for (let i = 0; i < 4; i++) await stop($)
  expect(w.removed).toEqual([FILE])
})

test('a user prompt after a streak removes the file', async ($, on) => {
  const w = world(on)
  await stop($)
  await submit($)
  expect(w.removed).toEqual([FILE])
})

test('a prompt with no streak running touches no file', async ($, on) => {
  const w = world(on)
  await submit($)
  expect(w.removed).toEqual([])
  expect(w.writes).toEqual([])
})

test('a normal stop ending a streak removes the file', async ($, on) => {
  let blocks = true
  const w = world(on, () => blocks)
  await stop($)
  blocks = false
  await stop($)
  expect(w.removed).toEqual([FILE])
})

test('a terminal-only session draws no status row but still writes the file', async ($, on) => {
  const w = world(on, () => true, {}, ['terminal'])
  await stop($)
  expect(w.statuses.filter(s => s !== undefined)).toEqual([])
  expect(lastWrite(w).path).toBe(FILE)
})

test('attaching a non-terminal surface shows the streak and detaching clears it', async ($, on) => {
  const w = world(on, () => true, {}, ['terminal'])
  await stop($)
  await stop($)
  w.surfaces = ['terminal', 'desktop']
  await $.session.attach({ clientId: 'c' })
  expect(last(w.statuses)).toBe('2 of 3 forced continuations')
  w.surfaces = ['terminal']
  await $.session.detach({ clientId: 'c' })
  expect(last(w.statuses)).toBeUndefined()
})

test('attaching with no streak running draws no status', async ($, on) => {
  const w = world(on)
  await $.session.attach({ clientId: 'c' })
  expect(last(w.statuses)).toBeUndefined()
})

test('session start removes this mod\'s files older than seven days and keeps the rest', async ($, on) => {
  const w = world(on)
  w.files = [
    { name: 'old.loop-brake.json', kind: 'file', mtimeMs: w.now - 8 * DAY },
    { name: 'new.loop-brake.json', kind: 'file', mtimeMs: w.now - 6 * DAY },
    { name: 'old.session-modes.json', kind: 'file', mtimeMs: w.now - 9 * DAY },
  ]
  await startSession($)
  expect(w.removed).toEqual([`${DIR}/old.loop-brake.json`])
})

test('a failed prune does not stop the brake from counting', async ($, on) => {
  const w = world(on)
  w.files = [{ name: 'old.loop-brake.json', kind: 'file', mtimeMs: 0 }]
  w.failRm = true
  await startSession($)
  expect((await stop($)).block).toBeDefined()
  expect(last(w.statuses)).toBe('1 of 3 forced continuations')
})
