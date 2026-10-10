import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

function world(on: On) {
  const state = { commands: [] as string[], statuses: [] as (string | undefined)[] }
  on('command.register', (_$, e) => (state.commands.push((e as { name: string }).name), { value: {} }) as never)
  on('session.start', (_$, e) => e as never)
  on('ui.status', (_$, e) => {
    state.statuses.push(e.text)
    return { value: undefined } as never
  })
  on('prompt.compose', () => ({ sections: [{ id: 'base', text: 'base', scope: 'shared' }] }) as never)
  return state
}

const start = ($: { session: { start: (e: never) => Promise<unknown> } }, isInteractive = true) =>
  $.session.start({ cwd: '/tmp', isInteractive } as never)
const mode = ($: { command: { run: (e: never) => Promise<{ text?: string }> } }, args = '') =>
  $.command.run({ command: 'mode', args } as never)
const bash = ($: { tool: { call: (e: never) => Promise<{ deny?: string }> } }, command: string) =>
  $.tool.call({ tool: 'Bash', command } as never)
const last = (s: (string | undefined)[]) => s[s.length - 1]

async function setUp(on: On, $: Parameters<typeof start>[0] & Parameters<typeof mode>[0], m: string) {
  const w = world(on)
  await start($)
  await mode($, m)
  return w
}

const blocked = (out: { deny?: string }) => typeof out.deny === 'string'

const BASH_TABLE: [string, string, boolean, boolean, boolean][] = [
  // command, audit, no-pr, chat denies
  ['git commit -m x', '', true, false, false],
  ['git push origin main', '', true, false, true],
  ['gh pr create --fill', '', true, true, true],
  ['gh pr merge 4', '', true, false, false],
  ['echo hi > out.txt', '', true, false, false],
  ['echo hi >> notes/out.txt', '', true, false, false],
  ['echo hi >out.txt', '', true, false, false],
  ['pnpm test 2>&1', '', false, false, false],
  ['pnpm test 2>&1 | tail -5', '', false, false, false],
  ['pnpm test >/dev/null', '', false, false, false],
  ['pnpm test > /dev/null 2>&1', '', false, false, false],
  ['pnpm test 2>/dev/null', '', false, false, false],
  ['echo oops >&2', '', false, false, false],
  ['ls -la', '', false, false, false],
  ['git status', '', false, false, false],
  ['git log --oneline', '', false, false, false],
  ['gh pr view 4', '', false, false, false],
].map(([c, , a, n, ch]) => [c, '', a, n, ch] as [string, string, boolean, boolean, boolean])

for (const [name, col] of [['audit', 2], ['no-pr', 3], ['chat', 4]] as const) {
  for (const row of BASH_TABLE) {
    const denied = row[col] as boolean
    test(`${name} mode ${denied ? 'denies' : 'allows'} Bash: ${row[0]}`, async ($, on) => {
      on('tool.call', () => ({ result: 'ok' }) as never)
      await setUp(on, $ as never, name)
      expect(blocked(await bash($ as never, row[0]))).toBe(denied)
    })
  }
}

const TOOL_TABLE: [string, boolean, boolean, boolean][] = [
  ['Edit', true, false, false],
  ['Write', true, false, false],
  ['NotebookEdit', true, false, false],
  ['Read', false, false, false],
  ['Grep', false, false, false],
  ['mcp__github__create_pull_request', false, true, true],
  ['mcp__github__list_pull_requests', false, false, false],
  ['mcp__github__merge_pull_request', false, false, false],
]

for (const [name, col] of [['audit', 1], ['no-pr', 2], ['chat', 3]] as const) {
  for (const row of TOOL_TABLE) {
    const denied = row[col] as boolean
    test(`${name} mode ${denied ? 'denies' : 'allows'} ${row[0]}`, async ($, on) => {
      on('tool.call', () => ({ result: 'ok' }) as never)
      await setUp(on, $ as never, name)
      expect(blocked(await $.tool.call({ tool: row[0] } as never))).toBe(denied)
    })
  }
}

test('with no mode set, nothing is denied', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  expect(blocked(await bash($ as never, 'git push && gh pr create'))).toBe(false)
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(false)
})

test('a denial names the mode and tells Claude what to do instead', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  await setUp(on, $ as never, 'audit')
  const out = await $.tool.call({ tool: 'Edit' } as never)
  expect(out.deny).toMatch(/audit mode is on/)
  expect(out.deny).toMatch(/report the change instead of making it/)
  expect(out.deny).toMatch(/\/mode off/)
})

test('a denied call never reaches the tool', async ($, on) => {
  const ran: string[] = []
  on('tool.call', (_$, e) => (ran.push(e.tool), { result: 'ok' }) as never)
  await setUp(on, $ as never, 'audit')
  await $.tool.call({ tool: 'Write' } as never)
  expect(ran).toEqual([])
})

test('/mode off lifts enforcement', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  await setUp(on, $ as never, 'audit')
  await mode($ as never, 'off')
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(false)
})

test('switching mode replaces the old one instead of stacking', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  await setUp(on, $ as never, 'audit')
  await mode($ as never, 'no-pr')
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(false)
  expect(blocked(await bash($ as never, 'gh pr create'))).toBe(true)
})

test('/mode alone reports the current mode and lists the modes', async ($, on) => {
  world(on)
  await start($ as never)
  const none = await mode($ as never)
  expect(none.text).toMatch(/off/)
  for (const m of ['audit', 'no-pr', 'chat', 'off']) expect(none.text).toContain(m)
  await mode($ as never, 'chat')
  expect((await mode($ as never)).text).toMatch(/current mode: chat/i)
})

test('an unknown mode lists the modes and changes nothing', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  const w = await setUp(on, $ as never, 'audit')
  const out = await mode($ as never, 'foo')
  expect(out.text).toMatch(/foo/)
  for (const m of ['audit', 'no-pr', 'chat', 'off']) expect(out.text).toContain(m)
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
  expect(last(w.statuses)).toBe('mode: audit')
})

test('the mode argument is case and space tolerant', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await mode($ as never, '  AUDIT ')
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
})

test('the status line follows the mode and clears on off', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'no-pr')
  expect(last(w.statuses)).toBe('mode: no-pr')
  await mode($ as never, 'chat')
  expect(last(w.statuses)).toBe('mode: chat')
  await mode($ as never, 'off')
  expect(last(w.statuses)).toBeUndefined()
  expect(w.statuses).toEqual([undefined, 'mode: no-pr', 'mode: chat', undefined])
})

test('the prompt gets one session section last while a mode is on', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  const { sections } = await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)
  const mine = sections[sections.length - 1]
  expect(sections.map(s => s.id)).toEqual(['base', mine.id])
  expect(mine.scope).toBe('session')
  expect(mine.text).toBe(
    'Audit mode: read and report only. Do not edit files, commit, push or open pull requests; list findings instead.',
  )
})

test('each mode states itself in the prompt, chat asks for the result in the reply', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'no-pr')
  expect((await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)).sections.at(-1)!.text).toMatch(/^No-PR mode:.*pull request/)
  await mode($ as never, 'chat')
  expect((await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)).sections.at(-1)!.text).toMatch(/^Chat mode:.*reply/)
})

test('/mode off removes the prompt section', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await mode($ as never, 'off')
  expect((await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)).sections.map(s => s.id)).toEqual(['base'])
})

test('with no mode the prompt is untouched', async ($, on) => {
  world(on)
  await start($ as never)
  expect((await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)).sections.map(s => s.id)).toEqual(['base'])
})

test('an interactive session registers the mode command', async ($, on) => {
  const w = world(on)
  await start($ as never)
  expect(w.commands).toEqual(['mode'])
})

test('a non-interactive session registers no command and draws no status', async ($, on) => {
  const w = world(on)
  await start($ as never, false)
  expect(w.commands).toEqual([])
  expect(w.statuses).toEqual([])
})

test('a non-interactive session still enforces a mode that was set', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  const before = w.statuses.length
  await start($ as never, false)
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
  expect((await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)).sections.length).toBe(2)
  expect(w.statuses.length).toBe(before)
})

test('a second session start keeps the mode and redraws its status', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await start($ as never)
  expect(last(w.statuses)).toBe('mode: audit')
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
})
