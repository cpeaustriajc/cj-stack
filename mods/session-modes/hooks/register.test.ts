import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

type Surface = 'terminal' | 'desktop'

function world(on: On, surfaces: Surface[] = ['desktop']) {
  const state = {
    commands: [] as string[],
    hints: [] as (string | undefined)[],
    statusCalls: [] as unknown[],
    toasts: [] as string[],
    surfaces,
    writes: [] as { path: string; text: string }[],
    removed: [] as string[],
    runs: [] as string[][],
    failRm: false,
    throwRm: false,
    files: [] as { name: string; kind: string; mtimeMs: number }[],
    env: { HOME: '/home/cj' } as Record<string, string | undefined>,
    now: 100 * 86_400_000,
    spawned: [] as string[],
    prompts: [] as { text: string; context?: readonly string[] }[],
  }
  on('session.id', () => ({ value: 'sess1' }) as never)
  on('session.surfaces', () => ({ value: state.surfaces }) as never)
  on('env.get', (_$, e) => ({ value: state.env[(e as { name: string }).name] }) as never)
  on('clock.now', () => ({ value: state.now }) as never)
  on('fs.exists', () => ({ value: true }) as never)
  on('fs.list', () => ({ value: state.files }) as never)
  on('fs.write', (_$, e) => (state.writes.push(e as never), { value: undefined }) as never)
  on('process.run', (_$, e) => {
    const argv = (e as { argv: string[] }).argv
    state.runs.push(argv)
    if (state.throwRm) throw new Error('rm: Permission denied')
    if (state.failRm) return { deny: 'no' } as never
    state.removed.push(...argv.slice(3))
    return { value: { exitCode: 0, stdout: '', stderr: '' } } as never
  })
  on('command.register', (_$, e) => {
    state.commands.push((e as { name: string }).name)
    state.hints.push((e as { argumentHint?: string }).argumentHint)
    return { value: {} } as never
  })
  on('session.start', (_$, e) => e as never)
  on('ui.status', (_$, e) => {
    state.statusCalls.push(e)
    return { value: undefined } as never
  })
  on('ui.toast', (_$, e) => {
    state.toasts.push((e as { text: string }).text)
    return { value: undefined } as never
  })
  on('ui.render', () => ({ type: 'Box', props: {}, children: [] }) as never)
  on('prompt.compose', () => ({ sections: [{ id: 'base', text: 'base', scope: 'shared' }] }) as never)
  on('skill.prompt', (_$, e) => ({ text: (e as { text: string }).text }) as never)
  on('agent.spawn', (_$, e) => (state.spawned.push((e as { prompt: string }).prompt), { model: 'm', agentId: 'a1' }) as never)
  on('prompt.submit', (_$, e) => {
    const input = e as { text: string; context?: readonly string[] }
    state.prompts.push(input)
    return { text: input.text, context: input.context } as never
  })
  return state
}

const start = ($: { session: { start: (e: never) => Promise<unknown> } }, isInteractive = true) =>
  $.session.start({ cwd: '/tmp', isInteractive } as never)
const mode = ($: { command: { run: (e: never) => Promise<{ text?: string }> } }, args = '') =>
  $.command.run({ command: 'mode', args } as never)
const bash = ($: { tool: { call: (e: never) => Promise<{ deny?: string }> } }, command: string) =>
  $.tool.call({ tool: 'Bash', command } as never)

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
  for (const m of ['audit', 'no-pr', 'chat', 'product', 'off']) expect(none.text).toContain(m)
  await mode($ as never, 'chat')
  expect((await mode($ as never)).text).toMatch(/current mode: chat/i)
})

test('an unknown mode lists the modes and changes nothing', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  await setUp(on, $ as never, 'audit')
  const out = await mode($ as never, 'foo')
  expect(out.text).toMatch(/foo/)
  for (const m of ['audit', 'no-pr', 'chat', 'product', 'off']) expect(out.text).toContain(m)
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
})

test('the mode argument is case and space tolerant', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await mode($ as never, '  AUDIT ')
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
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

test('/mode off replaces the mode section with an off section', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await mode($ as never, 'off')
  const { sections } = await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)
  expect(sections.map(s => s.id)).toEqual(['base', 'session-modes:mode'])
  expect(sections.at(-1)!.text).not.toMatch(/^Audit mode:/)
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

test('the mode command hints its five arguments', async ($, on) => {
  const w = world(on)
  await start($ as never)
  expect(w.hints).toEqual(['audit | no-pr | chat | product | off'])
})

test('a non-interactive session, as in the desktop app, still registers /mode', async ($, on) => {
  const w = world(on)
  await start($ as never, false)
  expect(w.commands).toEqual(['mode'])
  expect((await mode($ as never, 'audit')).text).toBe('Mode audit on.')
})

test('a non-interactive session still enforces a mode that was set', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await start($ as never, false)
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
  expect((await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)).sections.length).toBe(2)
})

test('a second session start keeps the mode', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await start($ as never)
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
})

const DIR = '/home/cj/.claude/mod-state'
const FILE = `${DIR}/sess1.session-modes.json`
const lastWrite = (w: { writes: { path: string; text: string }[] }) => w.writes[w.writes.length - 1]
const DAY = 86_400_000

test('setting a mode writes the status-line file named for the session and mod', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  expect(lastWrite(w).path).toBe(FILE)
  expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, mode: 'audit' })
})

test('changing the mode rewrites the file with the new mode', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await mode($ as never, 'chat')
  expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, mode: 'chat' })
})

test('turning the mode off marks the state file off instead of deleting it', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await mode($ as never, 'off')
  expect(lastWrite(w).path).toBe(FILE)
  expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, mode: null })
  expect(w.runs).toEqual([])
})

test('CLAUDE_CONFIG_DIR moves the state directory', async ($, on) => {
  const w = world(on)
  w.env.CLAUDE_CONFIG_DIR = '/cfg'
  await start($ as never)
  await mode($ as never, 'audit')
  expect(lastWrite(w).path).toBe('/cfg/mod-state/sess1.session-modes.json')
})

test('USERPROFILE is the home directory when HOME is unset', async ($, on) => {
  const w = world(on)
  w.env = { USERPROFILE: '/profiles/cj' }
  await start($ as never)
  await mode($ as never, 'audit')
  expect(lastWrite(w).path).toBe('/profiles/cj/.claude/mod-state/sess1.session-modes.json')
})

test('with neither HOME nor USERPROFILE nothing is written or pruned', async ($, on) => {
  const w = world(on)
  w.env = {}
  w.files = [{ name: 'old.session-modes.json', kind: 'file', mtimeMs: 0 }]
  await start($ as never)
  await mode($ as never, 'audit')
  expect(w.writes).toEqual([])
  expect(w.runs).toEqual([])
})

test('a prune that throws does not stop /mode from being registered', async ($, on) => {
  const w = world(on)
  w.files = [{ name: 'old.session-modes.json', kind: 'file', mtimeMs: 0 }]
  w.throwRm = true
  await start($ as never)
  expect(w.commands).toEqual(['mode'])
  expect((await mode($ as never, 'audit')).text).toBe('Mode audit on.')
})

test('an unknown mode writes no file', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'foo')
  expect(w.writes).toEqual([])
})

test('a non-interactive session writes no state file', async ($, on) => {
  const w = world(on)
  await start($ as never, false)
  expect(w.writes).toEqual([])
})

test('a terminal-only session writes the state file', async ($, on) => {
  const w = world(on, ['terminal'])
  await start($ as never)
  await mode($ as never, 'audit')
  expect(lastWrite(w).path).toBe(FILE)
})

test('session start removes this mod\'s files older than seven days and keeps the rest', async ($, on) => {
  const w = world(on)
  w.files = [
    { name: 'old.session-modes.json', kind: 'file', mtimeMs: w.now - 8 * DAY },
    { name: 'new.session-modes.json', kind: 'file', mtimeMs: w.now - 6 * DAY },
    { name: 'old.loop-brake.json', kind: 'file', mtimeMs: w.now - 9 * DAY },
  ]
  await start($ as never)
  expect(w.removed).toEqual([`${DIR}/old.session-modes.json`])
})

test('a failed prune never breaks the mode command', async ($, on) => {
  const w = world(on)
  w.files = [{ name: 'old.session-modes.json', kind: 'file', mtimeMs: 0 }]
  w.failRm = true
  await start($ as never)
  expect(w.commands).toEqual(['mode'])
  expect((await mode($ as never, 'audit')).text).toBe('Mode audit on.')
  expect(lastWrite(w).path).toBe(FILE)
})

test('a resumed session with a mode on republishes its file at start', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'chat')
  w.writes.length = 0
  await start($ as never)
  expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, mode: 'chat' })
})

const skill = ($: { skill: { prompt: (e: never) => Promise<unknown> } }, name: string) =>
  $.skill.prompt({ skill: name, text: 'x' } as never)

const PRODUCT_TABLE: [string, Record<string, unknown>, boolean][] = [
  // tool call, denied before any planning skill loads
  ['Edit', { file_path: '/repo/src/app.ts' }, true],
  ['Write', { file_path: '/repo/src/new.tsx' }, true],
  ['NotebookEdit', { notebook_path: '/repo/a.ipynb' }, true],
  ['Write', { file_path: '/repo/plans/vision.md' }, false],
  ['Edit', { file_path: '/repo/docs/spec.MD' }, false],
  ['Read', { file_path: '/repo/src/app.ts' }, false],
  ['mcp__github__create_pull_request', {}, true],
  ['Bash:git push origin main', {}, true],
  ['Bash:gh pr create --fill', {}, true],
  ['Bash:echo x > src/app.ts', {}, true],
  ['Bash:echo x >> plans/tickets.md', {}, false],
  ['Bash:git commit -m plan', {}, false],
  ['Bash:pnpm test 2>&1', {}, false],
]

for (const [tool, input, denied] of PRODUCT_TABLE) {
  test(`product mode ${denied ? 'denies' : 'allows'} ${tool}${input.file_path ? ` on ${input.file_path}` : ''}`, async ($, on) => {
    on('tool.call', () => ({ result: 'ok' }) as never)
    await setUp(on, $ as never, 'product')
    const out = tool.startsWith('Bash:') ? await bash($ as never, tool.slice(5)) : await $.tool.call({ tool, ...input } as never)
    expect(blocked(out)).toBe(denied)
  })
}

const OUTSIDE: [string, string, boolean][] = [
  // tool, bash command, counts as a write outside the repo
  ['mcp__linear-server__save_issue', '', true],
  ['mcp__linear-server__save_milestone', '', true],
  ['mcp__atlassian__createJiraIssue', '', true],
  ['mcp__asana__asana_create_task', '', true],
  ['mcp__notion__notion-update-page', '', true],
  ['mcp__linear-server__get_issue', '', false],
  ['mcp__linear-server__list_projects', '', false],
  ['mcp__atlassian__getJiraIssue', '', false],
  ['mcp__github__get_settings', '', false],
  ['Bash', 'gh issue create --title x', true],
  ['Bash', 'gh api repos/o/r/milestones -X POST -f title=x', true],
  ['Bash', 'acli jira workitem create --summary x', true],
  ['Bash', 'gh issue list', false],
  ['Bash', 'gh api repos/o/r/milestones', false],
]

for (const [tool, command, outside] of OUTSIDE) {
  test(`product mode ${outside ? 'holds' : 'allows'} ${command || tool} until a planning skill loads`, async ($, on) => {
    on('tool.call', () => ({ result: 'ok' }) as never)
    await setUp(on, $ as never, 'product')
    const call = () => (tool === 'Bash' ? bash($ as never, command) : $.tool.call({ tool } as never))
    expect(blocked(await call())).toBe(outside)
    await skill($ as never, 'shape')
    expect(blocked(await call())).toBe(false)
  })
}

test('a held tracker write tells Claude which skill to load', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  await setUp(on, $ as never, 'product')
  const out = await $.tool.call({ tool: 'mcp__linear-server__save_issue' } as never)
  expect(out.deny).toMatch(/product mode is on/)
  expect(out.deny).toMatch(/tickets for work items/)
  expect(out.deny).toMatch(/\/mode off/)
})

for (const name of ['vision', 'tickets', 'cj-stack:shape', '/tickets']) {
  test(`loading ${name} opens tracker writes`, async ($, on) => {
    on('tool.call', () => ({ result: 'ok' }) as never)
    await setUp(on, $ as never, 'product')
    await skill($ as never, name)
    expect(blocked(await $.tool.call({ tool: 'mcp__linear-server__save_project' } as never))).toBe(false)
  })
}

for (const name of ['triage', 'other:shape', 'commit']) {
  test(`loading ${name} keeps tracker writes held`, async ($, on) => {
    on('tool.call', () => ({ result: 'ok' }) as never)
    await setUp(on, $ as never, 'product')
    await skill($ as never, name)
    expect(blocked(await $.tool.call({ tool: 'mcp__linear-server__save_project' } as never))).toBe(true)
  })
}

test('a planning skill never opens code edits in product mode', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  await setUp(on, $ as never, 'product')
  await skill($ as never, 'tickets')
  expect(blocked(await $.tool.call({ tool: 'Edit', file_path: '/repo/src/app.ts' } as never))).toBe(true)
})

test('a skill loaded before product mode was set still counts', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await skill($ as never, 'vision')
  await mode($ as never, 'product')
  expect(blocked(await $.tool.call({ tool: 'mcp__linear-server__save_initiative' } as never))).toBe(false)
})

for (const m of ['audit', 'no-pr', 'chat']) {
  test(`${m} mode never holds a tracker write`, async ($, on) => {
    on('tool.call', () => ({ result: 'ok' }) as never)
    await setUp(on, $ as never, m)
    expect(blocked(await $.tool.call({ tool: 'mcp__linear-server__save_issue' } as never))).toBe(false)
  })
}

test('the skill prompt passes through unchanged', async ($, on) => {
  world(on)
  await start($ as never)
  expect(await skill($ as never, 'shape')).toEqual({ text: 'x' })
})

test('product mode states itself in the prompt', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'product')
  const text = (await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)).sections.at(-1)!.text
  expect(text).toMatch(/^Product mode: plan top-down/)
  expect(text).toMatch(/triage/)
})

const COPY: [string, string, string, string][] = [
  ['audit', 'Audit', 'Read and report only.', 'Edits, commits, pushes and PRs are blocked.'],
  ['no-pr', 'No PR', 'Commit on the branch.', 'Opening a PR is blocked.'],
  ['chat', 'Chat', 'Edits and commits are allowed.', 'Pushes and PRs are blocked.'],
  ['product', 'Product', 'Plan in Markdown and the tracker.', 'Tracker writes wait for vision, shape or tickets.'],
]

const props = (over: Record<string, unknown> = {}) =>
  ({ hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 100, scroll: { offset: 0, bodyRows: 10 }, view: {}, ...over }) as never

type Band = { surface: Surface; over?: Record<string, unknown> }
const mount = ($: any, { surface, over }: Band) =>
  $.ui.mount({ plugin: 'session-modes', surface, component: 'AbovePrompt', props: props(over) })

for (const surface of ['terminal', 'desktop'] as const) {
  test(`${surface}: the band draws nothing while the mode is off`, async ($, on) => {
    world(on, [surface])
    await start($ as never)
    const band = await mount($, { surface })
    expect(await band.find({ type: 'Button', key: 'off' })).toBeUndefined()
    for (const [, label] of COPY) expect(await band.find({ type: 'Text', text: new RegExp(`^${label}$`) })).toBeUndefined()
  })

  for (const [name, label, lead, detail] of COPY) {
    test(`${surface}: the ${name} band shows its chip, lead and detail`, async ($, on) => {
      world(on, [surface])
      await start($ as never)
      await mode($ as never, name)
      const band = await mount($, { surface })
      expect(await band.find({ type: 'Text', text: new RegExp(`^${label}$`) })).toBeDefined()
      expect(await band.find({ text: lead })).toBeDefined()
      expect(await band.find({ text: detail })).toBeDefined()
      expect(await band.find({ type: 'Button', key: 'off' })).toBeDefined()
    })
  }

  test(`${surface}: the band yields to a survey`, async ($, on) => {
    world(on, [surface])
    await start($ as never)
    await mode($ as never, 'audit')
    const band = await mount($, { surface, over: { hasSurvey: true } })
    expect(await band.find({ type: 'Button', key: 'off' })).toBeUndefined()
    expect(await band.find({ type: 'Text', text: /^Audit$/ })).toBeUndefined()
  })

  test(`${surface}: a narrow band shows the lead but not the detail`, async ($, on) => {
    world(on, [surface])
    await start($ as never)
    await mode($ as never, 'audit')
    const band = await mount($, { surface, over: { bodyColumns: 40 } })
    expect(await band.find({ text: 'Read and report only.' })).toBeDefined()
    expect(await band.find({ text: 'Edits, commits, pushes and PRs are blocked.' })).toBeUndefined()
  })

  test(`${surface}: the product band opens its detail after a planning skill`, async ($, on) => {
    world(on, [surface])
    await start($ as never)
    await mode($ as never, 'product')
    const band = await mount($, { surface })
    expect(await band.find({ text: 'Tracker writes wait for vision, shape or tickets.' })).toBeDefined()
    await skill($ as never, 'shape')
    expect(await band.find({ text: 'Tracker writes are open.' })).toBeDefined()
    expect(await band.find({ text: 'Tracker writes wait for vision, shape or tickets.' })).toBeUndefined()
  })

  test(`${surface}: pressing Turn off ends the mode`, async ($, on) => {
    on('tool.call', () => ({ result: 'ok' }) as never)
    const w = world(on, [surface])
    await start($ as never)
    await mode($ as never, 'audit')
    expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
    const band = await mount($, { surface })
    await band.press({ key: 'off' })
    expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(false)
    expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, mode: null })
    expect(w.toasts).toEqual(['Mode off.'])
    const fresh = await mount($, { surface })
    expect(await fresh.find({ type: 'Button', key: 'off' })).toBeUndefined()
  })

  test(`${surface}: the status row is never used`, async ($, on) => {
    const w = world(on, [surface])
    await start($ as never)
    await mode($ as never, 'audit')
    await mode($ as never, 'off')
    await mount($, { surface })
    expect(w.statusCalls).toEqual([])
  })
}

const compose = ($: any) =>
  $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)

const OFF_AUDIT =
  'Session mode: off. Audit mode has ended; its rules no longer apply, even if the conversation still shows it on.'

test('after /mode audit then /mode off the prompt says the mode has ended', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await mode($ as never, 'off')
  const last = (await compose($)).sections.at(-1)
  expect(last.id).toBe('session-modes:mode')
  expect(last.scope).toBe('session')
  expect(last.text).toBe(OFF_AUDIT)
})

test('after the band Turn off button the prompt says the mode has ended', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  const band = await mount($, { surface: 'desktop' })
  await band.press({ key: 'off' })
  const last = (await compose($)).sections.at(-1)
  expect(last.id).toBe('session-modes:mode')
  expect(last.text).toBe(OFF_AUDIT)
})

test('a session that never set a mode gets no mode section', async ($, on) => {
  world(on)
  await start($ as never)
  expect((await compose($)).sections.map((s: { id: string }) => s.id)).not.toContain('session-modes:mode')
})

test('turning a mode on again drops the off text, and the next off names the new mode', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await mode($ as never, 'off')
  await mode($ as never, 'chat')
  expect((await compose($)).sections.at(-1).text).toMatch(/^Chat mode:/)
  await mode($ as never, 'off')
  expect((await compose($)).sections.at(-1).text).toBe(
    'Session mode: off. Chat mode has ended; its rules no longer apply, even if the conversation still shows it on.',
  )
})

const spawn = ($: any, extra: Record<string, unknown> = {}) =>
  $.agent.spawn({ prompt: 'Find the bug.', description: 'd', subagentType: 'general-purpose', fork: false, ...extra } as never)

test('a subagent started in audit mode gets the rule at the top of its task', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await spawn($)
  expect(w.spawned).toHaveLength(1)
  expect(w.spawned[0]).toBe(
    'The main session is in Audit mode, and it applies to you too. Audit mode: read and report only. Do not edit files, commit, push or open pull requests; list findings instead. Tool calls that break it are denied.\n\nFind the bug.',
  )
})

test('a subagent started with the mode off keeps its prompt', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await spawn($)
  await mode($ as never, 'audit')
  await mode($ as never, 'off')
  await spawn($)
  expect(w.spawned).toEqual(['Find the bug.', 'Find the bug.'])
})

test('a workflow agent keeps its prompt in audit mode', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await spawn($, { workflow: { runId: 'wf_x', agentIndex: 1 } })
  expect(w.spawned).toEqual(['Find the bug.'])
})

const submit = ($: any, text = 'hello', context?: string[]) =>
  $.prompt.submit({ text, wait: false, origin: { kind: 'composer' }, ...(context ? { context } : {}) } as never)

const notes = (w: { prompts: { context?: readonly string[] }[] }, i = -1) => w.prompts.at(i)!.context ?? []

test('a prompt carries no mode note while no mode was ever set', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await submit($)
  expect(notes(w)).toEqual([])
})

test('the prompt after /mode audit carries the Audit note once', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await submit($)
  expect(notes(w)).toHaveLength(1)
  expect(notes(w)[0]).toMatch(/^Session mode: Audit is on\. Audit mode: read and report only\./)
  await submit($)
  expect(notes(w)).toEqual([])
})

test('the prompt after the band Turn off button carries the off note', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await submit($)
  const band = await mount($, { surface: 'desktop' })
  await band.press({ key: 'off' })
  await submit($)
  expect(notes(w)).toHaveLength(1)
  expect(notes(w)[0]).toMatch(/^Session mode: off\. Audit mode has ended/)
})

test('two mode changes before a prompt give one note, the last mode', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await mode($ as never, 'chat')
  await submit($)
  expect(notes(w)).toHaveLength(1)
  expect(notes(w)[0]).toMatch(/^Session mode: Chat is on\. Chat mode:/)
})

test('a mode set and cleared before any prompt gives no note', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  await mode($ as never, 'off')
  await submit($)
  expect(notes(w)).toEqual([])
})

test('the mode note goes after the context a prompt already has', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'audit')
  const out = await submit($, 'hello', ['x'])
  expect(notes(w)).toHaveLength(2)
  expect(notes(w)[0]).toBe('x')
  expect(notes(w)[1]).toMatch(/^Session mode: Audit is on\./)
  expect(out.context).toEqual(notes(w))
})
