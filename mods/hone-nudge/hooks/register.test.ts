import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

const line = (o: object) => JSON.stringify(o)
const skillUse = (skill: string) => line({ type: 'assistant', message: { content: [{ type: 'tool_use', id: 't', name: 'Skill', input: { skill } }] } })
const command = (name: string) => line({ type: 'user', message: { content: `<command-name>${name}</command-name>` } })
const said = (text: string) => line({ type: 'user', message: { content: text } })
const claude = line({ type: 'assistant', message: { content: [{ type: 'text', text: 'Done' }] } })
const lines = (...l: string[]) => l.join('\n')

function world(on: On, transcript: string | Error, blocks = false) {
  const state = {
    logs: [] as string[],
    writes: new Map<string, string>(),
    removed: [] as string[],
    files: [] as { name: string; kind: string; mtimeMs: number }[],
    env: { HOME: '/home/cj' } as Record<string, string | undefined>,
    transcript,
    now: 100 * 86_400_000,
    writeFails: false,
  }
  on('session.start', (_$, e) => e as never)
  on('env.get', (_$, e) => ({ value: state.env[(e as { name: string }).name] }) as never)
  on('clock.now', () => ({ value: state.now }) as never)
  on('fs.exists', (_$, e) => ({ value: state.writes.has((e as { path: string }).path) || (e as { path: string }).path.endsWith('mod-state') }) as never)
  on('fs.list', () => ({ value: state.files }) as never)
  on('fs.read', (_$, e) => {
    const path = (e as { path: string }).path
    if (state.writes.has(path)) return { value: state.writes.get(path) } as never
    if (state.transcript instanceof Error) throw state.transcript
    return { value: state.transcript } as never
  })
  on('fs.write', (_$, e) => {
    if (state.writeFails) throw new Error('disk full')
    state.writes.set((e as { path: string }).path, (e as { text: string }).text)
    return { value: undefined } as never
  })
  on('process.run', (_$, e) => {
    state.removed.push(...(e as { argv: string[] }).argv.slice(3))
    return { value: { exitCode: 0, stdout: '', stderr: '' } } as never
  })
  on('classic.Stop', () => (blocks ? { block: 'keep going' } : {}) as never)
  on('ui.log', (_$, e) => (state.logs.push(e.text), { value: undefined }) as never)
  return state
}

const stop = ($: any) => $.classic.Stop({ session_id: 's1', transcript_path: '/t.jsonl', stop_hook_active: false })

test('a correction during a skill run suggests hone for that skill', async ($, on) => {
  const w = world(on, lines(skillUse('cj-stack:ui-polish'), claude, said('no, wrong easing')))
  await stop($)
  expect(w.logs).toEqual(['1 correction during ui-polish. Run /hone ui-polish?'])
})

test('a slash command starts the skill', async ($, on) => {
  const w = world(on, lines(command('/cj-stack:break-it'), claude, said('[Request interrupted by user]'), said("don't do that")))
  await stop($)
  expect(w.logs).toEqual(['2 corrections during break-it. Run /hone break-it?'])
})

test('a rejected tool call counts', async ($, on) => {
  const rejectedResult = line({ type: 'user', message: { content: [{ type: 'tool_result', tool_use_id: 'x', content: "The user doesn't want to proceed with this tool use." }] } })
  const w = world(on, lines(skillUse('hone'), claude, rejectedResult))
  await stop($)
  expect(w.logs).toEqual(['1 correction during hone. Run /hone hone?'])
})

test('no correction means silence', async ($, on) => {
  const w = world(on, lines(skillUse('ui-polish'), claude, said('looks good, thanks')))
  await stop($)
  expect(w.logs).toEqual([])
  expect(w.writes.size).toBe(0)
})

test('a correction before any skill ran is silent', async ($, on) => {
  const w = world(on, lines(claude, said('no, not like that'), skillUse('ui-polish'), claude))
  await stop($)
  expect(w.logs).toEqual([])
})

test('a correction after another skill took over is credited to that skill', async ($, on) => {
  const w = world(on, lines(skillUse('ui-polish'), claude, skillUse('break-it'), claude, said('no, stop')))
  await stop($)
  expect(w.logs).toEqual(['1 correction during break-it. Run /hone break-it?'])
})

test('skills outside cj-stack are ignored, including a foreign prefix', async ($, on) => {
  const w = world(on, lines(skillUse('other:ui-polish'), claude, said('no'), skillUse('deploy'), claude, said('no')))
  await stop($)
  expect(w.logs).toEqual([])
})

test('a skill is nudged once per session', async ($, on) => {
  const w = world(on, lines(skillUse('ui-polish'), claude, said('no, wrong')))
  await stop($)
  await stop($)
  expect(w.logs.length).toBe(1)
  expect(w.writes.get('/home/cj/.claude/mod-state/s1.hone-nudge.json')).toBe(JSON.stringify({ v: 1, nudged: ['ui-polish'] }))
})

test('a second skill still gets its own nudge after the first', async ($, on) => {
  const w = world(on, lines(skillUse('ui-polish'), claude, said('no, wrong')))
  await stop($)
  w.transcript = lines(skillUse('ui-polish'), claude, said('no, wrong'), skillUse('break-it'), claude, said('no, wrong'))
  await stop($)
  expect(w.logs.length).toBe(2)
  expect(w.logs[1]).toContain('/hone break-it')
})

test('an unreadable transcript is handled quietly', async ($, on) => {
  const w = world(on, new Error('ENOENT'))
  const r = await stop($)
  expect(r.block).toBeUndefined()
  expect(w.logs).toEqual([])
})

test('a malformed line is skipped and the rest still counts', async ($, on) => {
  const w = world(on, lines(skillUse('ui-polish'), '{"type":"user","message":{"conte', 'not json', claude, said('no, wrong')))
  await stop($)
  expect(w.logs).toEqual(['1 correction during ui-polish. Run /hone ui-polish?'])
})

test('a stop that another hook is turning into a continuation stays silent', async ($, on) => {
  const w = world(on, lines(skillUse('ui-polish'), claude, said('no, wrong')), true)
  const r = await stop($)
  expect(r.block).toBe('keep going')
  expect(w.logs).toEqual([])
})

test('the stop result is never changed', async ($, on) => {
  world(on, lines(skillUse('ui-polish'), claude, said('no, wrong')))
  const r = await stop($)
  expect(r.block).toBeUndefined()
  expect(r.preventContinuation).toBeUndefined()
})

test('with no home directory nothing is nudged', async ($, on) => {
  const w = world(on, lines(skillUse('ui-polish'), claude, said('no, wrong')))
  w.env = {}
  await stop($)
  expect(w.logs).toEqual([])
})

test('a state file that cannot be written means no nudge, so it cannot repeat every stop', async ($, on) => {
  const w = world(on, lines(skillUse('ui-polish'), claude, said('no, wrong')))
  w.writeFails = true
  const r = await stop($)
  expect(r.block).toBeUndefined()
  expect(w.logs).toEqual([])
})

test('session start removes this mod\'s files older than seven days and keeps the rest', async ($, on) => {
  const w = world(on, '')
  const DAY = 86_400_000
  w.files = [
    { name: 'old.hone-nudge.json', kind: 'file', mtimeMs: w.now - 8 * DAY },
    { name: 'new.hone-nudge.json', kind: 'file', mtimeMs: w.now - 6 * DAY },
    { name: 'old.loop-brake.json', kind: 'file', mtimeMs: w.now - 9 * DAY },
  ]
  await $.session.start({ cwd: '/tmp', isInteractive: true })
  expect(w.removed).toEqual(['/home/cj/.claude/mod-state/old.hone-nudge.json'])
})
