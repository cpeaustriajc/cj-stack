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
    spawnCount: 0,
    tools: [] as { name: string; description: string; isDeferred?: boolean; inputSchema?: unknown }[],
    prompts: [] as { text: string; context?: readonly string[] }[],
    throwGet: undefined as string | undefined,
    throwSet: undefined as string | undefined,
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
  on('agent.spawn', (_$, e) => {
    state.spawned.push((e as { prompt: string }).prompt)
    state.spawnCount += 1
    const resumed = (e as { resume?: { agentId: string } }).resume
    return { model: 'm', agentId: resumed?.agentId ?? `a${state.spawnCount}` } as never
  })
  on('state.get', (_$, e, next) => {
    if ((e as { key: string }).key === state.throwGet) return { value: null, version: 1 } as never
    return next(e)
  })
  on('state.set', (_$, e, next) => {
    if ((e as { key: string }).key === state.throwSet) return { deny: 'no' } as never
    return next(e)
  })
  on('tool.register', (_$, e) => {
    state.tools.push(e as never)
    return { value: { tool: `mcp__session-modes__${(e as { name: string }).name}` } } as never
  })
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

type Need = 'readonly' | 'research' | 'prototype' | 'build' | 'off'
const LADDER_ORDER: Need[] = ['readonly', 'research', 'prototype', 'build', 'off']

const bashCall = (command: string) => ({ tool: 'Bash', command })
const NEEDS: [string, Record<string, unknown>, Need][] = [
  ...[
    'git status', 'git log --oneline', 'ls -la', 'gh pr view 4', 'gh issue list', 'gh api repos/o/r/milestones',
    'gh api repos/o/r/pulls', 'pnpm test 2>&1', 'pnpm test 2>&1 | tail -5', 'pnpm test >/dev/null',
    'pnpm test > /dev/null 2>&1', 'pnpm test 2>/dev/null', 'echo oops >&2', 'gh api repos/o/r/pulls -X GET -f state=open',
    "sed -E 's/[0-9a-f]{8,}/<id>/g' log.txt", "grep '<task-notification>' t.jsonl", 'grep "a -> b" notes.txt',
    'grep "say \\"hi>\\"" f.txt', "grep 'a|<b>' f.txt", "grep \"it's\" f.txt | grep '>'", 'echo a\\>b',
  ].map(c => [c, bashCall(c), 'readonly'] as [string, Record<string, unknown>, Need]),
  ...['Read', 'Grep', 'mcp__github__list_pull_requests', 'mcp__linear-server__get_issue', 'mcp__linear-server__list_projects',
    'mcp__atlassian__getJiraIssue', 'mcp__github__get_settings',
    'mcp__ccd_turn__update_plan', 'mcp__ccd_turn__wrap_up', 'mcp__ccd_view__close_pane', 'mcp__ccd_window__set_sidebar_collapsed',
    'mcp__ccd_sidebar__move_sessions', 'mcp__ccd_sidebar__create_group', 'mcp__session-modes__set_mode',
  ].map(t => [t, { tool: t }, 'readonly'] as [string, Record<string, unknown>, Need]),
  ...[
    'git commit -m x', 'echo hi >> notes/out.md', 'gh issue create --title x',
    'gh api repos/o/r/milestones -X POST -f title=x', 'acli jira workitem create --summary x',
  ].map(c => [c, bashCall(c), 'research'] as [string, Record<string, unknown>, Need]),
  ['Write /repo/plans/vision.md', { tool: 'Write', file_path: '/repo/plans/vision.md' }, 'research'],
  ['Edit /repo/docs/spec.MD', { tool: 'Edit', file_path: '/repo/docs/spec.MD' }, 'research'],
  ...['mcp__linear-server__save_issue', 'mcp__linear-server__save_milestone', 'mcp__atlassian__createJiraIssue',
    'mcp__asana__asana_create_task', 'mcp__notion__notion-update-page', 'mcp__ccd_settings__set_setting',
    'mcp__ccd_session_mgmt__delete_session', 'mcp__ccd_turnstile__update_plan', 'mcp__session-modes-x__save_issue',
  ].map(t => [t, { tool: t }, 'research'] as [string, Record<string, unknown>, Need]),
  ...['read', 'list', 'quickstart', 'open'].map(a => [`Artifact ${a}`, { tool: 'Artifact', action: a }, 'readonly'] as [string, Record<string, unknown>, Need]),
  ['Artifact publish', { tool: 'Artifact', file_path: '/repo/.claude/work/x/page.html' }, 'research'],
  ['Artifact publish by action', { tool: 'Artifact', action: 'publish', type_url: 'https://claude.ai/t/design' }, 'research'],
  ['Write /repo/.claude/work/dividends/proto.html', { tool: 'Write', file_path: '/repo/.claude/work/dividends/proto.html' }, 'prototype'],
  ['Edit .claude/work/cart/app.tsx', { tool: 'Edit', file_path: '.claude/work/cart/app.tsx' }, 'prototype'],
  ['Write C:\\repo\\.claude\\work\\a.css', { tool: 'Write', file_path: 'C:\\repo\\.claude\\work\\a.css' }, 'prototype'],
  ['echo x > .claude/work/a/b.html', bashCall('echo x > .claude/work/a/b.html'), 'prototype'],
  ['Write /repo/.claude/workflows/x.js', { tool: 'Write', file_path: '/repo/.claude/workflows/x.js' }, 'build'],
  ['Write /repo/src/.claude/work-notes.ts', { tool: 'Write', file_path: '/repo/src/.claude/work-notes.ts' }, 'build'],
  ...['echo hi > out.txt', 'echo hi >out.txt', 'echo hi >> notes/out.txt', 'echo x > src/app.ts',
    "echo '<a>' > out.html", 'echo x > "out.txt"', "echo 'abc > out.txt",
  ].map(
    c => [c, bashCall(c), 'build'] as [string, Record<string, unknown>, Need],
  ),
  ['Edit /repo/src/app.ts', { tool: 'Edit', file_path: '/repo/src/app.ts' }, 'build'],
  ['Write /repo/src/new.tsx', { tool: 'Write', file_path: '/repo/src/new.tsx' }, 'build'],
  ['NotebookEdit /repo/a.ipynb', { tool: 'NotebookEdit', notebook_path: '/repo/a.ipynb' }, 'build'],
  ['Edit with no path', { tool: 'Edit' }, 'build'],
  ...[
    'git push origin main', 'gh pr create --fill', 'gh pr merge 4', 'gh api repos/o/r/pulls -X POST -f title=x',
    'gh api repos/o/r/pulls -f title=x -f head=b -f base=main', 'gh api repos/o/r/pulls/4/merge -X PUT',
    'git commit -m x && git push', 'gh api repos/o/r/pulls \\\n  -f title=x',
  ].map(c => [c, bashCall(c), 'off'] as [string, Record<string, unknown>, Need]),
  ...['mcp__github__create_pull_request', 'mcp__github__merge_pull_request', 'mcp__github__update_pull_request',
    'mcp__github__push_files', 'mcp__x__createPullRequest',
  ].map(t => [t, { tool: t }, 'off'] as [string, Record<string, unknown>, Need]),
]

for (const name of ['readonly', 'research', 'prototype', 'build'] as const) {
  for (const [label, input, need] of NEEDS) {
    const denied = LADDER_ORDER.indexOf(need) > LADDER_ORDER.indexOf(name)
    test(`${name} mode ${denied ? 'denies' : 'allows'} ${label}`, async ($, on) => {
      on('tool.call', () => ({ result: 'ok' }) as never)
      await setUp(on, $ as never, name)
      expect(blocked(await $.tool.call(input as never))).toBe(denied)
    })
  }
}

test('with no mode set, nothing is denied', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  for (const [, input] of NEEDS) expect(blocked(await $.tool.call(input as never))).toBe(false)
})

test('a denial names the mode and tells Claude what to do instead', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  await setUp(on, $ as never, 'readonly')
  const out = await $.tool.call({ tool: 'Edit' } as never)
  expect(out.deny).toMatch(/readonly mode is on/)
  expect(out.deny).toMatch(/report the change instead of making it/)
  expect(out.deny).toMatch(/\/mode off/)
})

test('a denied call never reaches the tool', async ($, on) => {
  const ran: string[] = []
  on('tool.call', (_$, e) => (ran.push(e.tool), { result: 'ok' }) as never)
  await setUp(on, $ as never, 'readonly')
  await $.tool.call({ tool: 'Write' } as never)
  expect(ran).toEqual([])
})

test('/mode off lifts enforcement', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  await setUp(on, $ as never, 'readonly')
  await mode($ as never, 'off')
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(false)
})

test('switching mode replaces the old one instead of stacking', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  await setUp(on, $ as never, 'readonly')
  await mode($ as never, 'build')
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(false)
  expect(blocked(await bash($ as never, 'gh pr create'))).toBe(true)
})

test('/mode alone reports the current mode and lists the modes', async ($, on) => {
  world(on)
  await start($ as never)
  const none = await mode($ as never)
  expect(none.text).toMatch(/off/)
  for (const m of ['readonly', 'research', 'build', 'off']) expect(none.text).toContain(m)
  await mode($ as never, 'build')
  expect((await mode($ as never)).text).toMatch(/current mode: build/i)
})

test('an unknown mode lists the modes and changes nothing', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  await setUp(on, $ as never, 'readonly')
  const out = await mode($ as never, 'foo')
  expect(out.text).toMatch(/foo/)
  for (const m of ['readonly', 'research', 'build', 'off']) expect(out.text).toContain(m)
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
})

test('the mode argument is case and space tolerant', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await mode($ as never, '  READONLY ')
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
})

test('the prompt gets one session section last while a mode is on', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  const { sections } = await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)
  const mine = sections[sections.length - 1]
  expect(sections.map(s => s.id)).toEqual(['base', mine.id])
  expect(mine.scope).toBe('session')
  expect(mine.text).toBe(
    'Read only mode: read and report only. Do not edit files, commit, push, open pull requests or write to trackers; list findings instead.',
  )
})

test('each mode states itself in the prompt, edit allows local commits', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'research')
  expect((await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)).sections.at(-1)!.text).toMatch(/^Research mode:.*Do not push or open pull requests/)
  await mode($ as never, 'build')
  expect((await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)).sections.at(-1)!.text).toMatch(/^Build mode:.*commit locally/)
})

test('/mode off replaces the mode section with an off section', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await mode($ as never, 'off')
  const { sections } = await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)
  expect(sections.map(s => s.id)).toEqual(['base', 'session-modes:mode'])
  expect(sections.at(-1)!.text).not.toMatch(/^Read only mode:/)
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

test('the mode command hints its six arguments', async ($, on) => {
  const w = world(on)
  await start($ as never)
  expect(w.hints).toEqual(['readonly | research | prototype | build | off'])
})

test('a non-interactive session, as in the desktop app, still registers /mode', async ($, on) => {
  const w = world(on)
  await start($ as never, false)
  expect(w.commands).toEqual(['mode'])
  expect((await mode($ as never, 'readonly')).text).toBe('Mode readonly on.')
})

test('a non-interactive session still enforces a mode that was set', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await start($ as never, false)
  expect(blocked(await $.tool.call({ tool: 'Edit' } as never))).toBe(true)
  expect((await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)).sections.length).toBe(2)
})

test('a second session start keeps the mode', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
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
  await mode($ as never, 'readonly')
  expect(lastWrite(w).path).toBe(FILE)
  expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, mode: 'readonly' })
})

test('changing the mode rewrites the file with the new mode', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await mode($ as never, 'build')
  expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, mode: 'build' })
})

test('turning the mode off marks the state file off instead of deleting it', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await mode($ as never, 'off')
  expect(lastWrite(w).path).toBe(FILE)
  expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, mode: null })
  expect(w.runs).toEqual([])
})

test('CLAUDE_CONFIG_DIR moves the state directory', async ($, on) => {
  const w = world(on)
  w.env.CLAUDE_CONFIG_DIR = '/cfg'
  await start($ as never)
  await mode($ as never, 'readonly')
  expect(lastWrite(w).path).toBe('/cfg/mod-state/sess1.session-modes.json')
})

test('USERPROFILE is the home directory when HOME is unset', async ($, on) => {
  const w = world(on)
  w.env = { USERPROFILE: '/profiles/cj' }
  await start($ as never)
  await mode($ as never, 'readonly')
  expect(lastWrite(w).path).toBe('/profiles/cj/.claude/mod-state/sess1.session-modes.json')
})

test('with neither HOME nor USERPROFILE nothing is written or pruned', async ($, on) => {
  const w = world(on)
  w.env = {}
  w.files = [{ name: 'old.session-modes.json', kind: 'file', mtimeMs: 0 }]
  await start($ as never)
  await mode($ as never, 'readonly')
  expect(w.writes).toEqual([])
  expect(w.runs).toEqual([])
})

test('a prune that throws does not stop /mode from being registered', async ($, on) => {
  const w = world(on)
  w.files = [{ name: 'old.session-modes.json', kind: 'file', mtimeMs: 0 }]
  w.throwRm = true
  await start($ as never)
  expect(w.commands).toEqual(['mode'])
  expect((await mode($ as never, 'readonly')).text).toBe('Mode readonly on.')
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
  await mode($ as never, 'readonly')
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
  expect((await mode($ as never, 'readonly')).text).toBe('Mode readonly on.')
  expect(lastWrite(w).path).toBe(FILE)
})

test('a resumed session with a mode on republishes its file at start', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'build')
  w.writes.length = 0
  await start($ as never)
  expect(JSON.parse(lastWrite(w).text)).toEqual({ v: 1, mode: 'build' })
})

const COPY: [string, string, string, string][] = [
  ['readonly', 'Read only', 'Read and report only.', 'Edits, commits, pushes, PRs and tracker writes are blocked.'],
  ['research', 'Research', 'Notes, plans and tracker items only.', 'Code edits, pushes and PRs are blocked.'],
  ['build', 'Build', 'Edits and commits are allowed.', 'Pushes and PRs are blocked.'],
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
    await mode($ as never, 'readonly')
    const band = await mount($, { surface, over: { hasSurvey: true } })
    expect(await band.find({ type: 'Button', key: 'off' })).toBeUndefined()
    expect(await band.find({ type: 'Text', text: /^Read only$/ })).toBeUndefined()
  })

  test(`${surface}: a narrow band shows the lead but not the detail`, async ($, on) => {
    world(on, [surface])
    await start($ as never)
    await mode($ as never, 'readonly')
    const band = await mount($, { surface, over: { bodyColumns: 40 } })
    expect(await band.find({ text: 'Read and report only.' })).toBeDefined()
    expect(await band.find({ text: 'Edits, commits, pushes and PRs are blocked.' })).toBeUndefined()
  })

  test(`${surface}: pressing Turn off ends the mode`, async ($, on) => {
    on('tool.call', () => ({ result: 'ok' }) as never)
    const w = world(on, [surface])
    await start($ as never)
    await mode($ as never, 'readonly')
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
    await mode($ as never, 'readonly')
    await mode($ as never, 'off')
    await mount($, { surface })
    expect(w.statusCalls).toEqual([])
  })
}

const compose = ($: any) =>
  $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: [], tools: [], outputStyle: null, traits: [] } as never)

const OFF_READONLY =
  'Session mode: off. Read only mode has ended; its rules no longer apply, even if the conversation still shows it on.'

test('after /mode readonly then /mode off the prompt says the mode has ended', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await mode($ as never, 'off')
  const last = (await compose($)).sections.at(-1)
  expect(last.id).toBe('session-modes:mode')
  expect(last.scope).toBe('session')
  expect(last.text).toBe(OFF_READONLY)
})

test('after the band Turn off button the prompt says the mode has ended', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  const band = await mount($, { surface: 'desktop' })
  await band.press({ key: 'off' })
  const last = (await compose($)).sections.at(-1)
  expect(last.id).toBe('session-modes:mode')
  expect(last.text).toBe(OFF_READONLY)
})

test('a session that never set a mode gets no mode section', async ($, on) => {
  world(on)
  await start($ as never)
  expect((await compose($)).sections.map((s: { id: string }) => s.id)).not.toContain('session-modes:mode')
})

test('turning a mode on again drops the off text, and the next off names the new mode', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await mode($ as never, 'off')
  await mode($ as never, 'build')
  expect((await compose($)).sections.at(-1).text).toMatch(/^Build mode:/)
  await mode($ as never, 'off')
  expect((await compose($)).sections.at(-1).text).toBe(
    'Session mode: off. Build mode has ended; its rules no longer apply, even if the conversation still shows it on.',
  )
})

const spawn = ($: any, extra: Record<string, unknown> = {}) =>
  $.agent.spawn({ prompt: 'Find the bug.', description: 'd', subagentType: 'general-purpose', fork: false, ...extra } as never)

test('a subagent started in readonly mode gets the rule at the top of its task', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await spawn($)
  expect(w.spawned).toHaveLength(1)
  expect(w.spawned[0]).toBe(
    'The main session is in Read only mode, and it applies to you too. Read only mode: read and report only. Do not edit files, commit, push, open pull requests or write to trackers; list findings instead. Tool calls that break it are denied.\n\nFind the bug.',
  )
})

test('a subagent started with the mode off keeps its prompt', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await spawn($)
  await mode($ as never, 'readonly')
  await mode($ as never, 'off')
  await spawn($)
  expect(w.spawned).toEqual(['Find the bug.', 'Find the bug.'])
})

test('a workflow agent gets the mode rule in readonly mode', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await spawn($, { workflow: { runId: 'wf_x', agentIndex: 1 } })
  expect(w.spawned[0]!.startsWith('The main session is in Read only mode')).toBe(true)
  expect(w.spawned[0]!.endsWith('\n\nFind the bug.')).toBe(true)
})

const submit = ($: any, text = 'hello', context?: string[], extra: Record<string, unknown> = {}) =>
  $.prompt.submit({ text, wait: false, origin: { kind: 'composer' }, ...(context ? { context } : {}), ...extra } as never)

const CHECK = 'Session mode check:'
type Prompts = { prompts: { context?: readonly string[] }[] }
const all = (w: Prompts, i = -1) => w.prompts.at(i)!.context ?? []
const notes = (w: Prompts, i = -1) => all(w, i).filter(n => !n.startsWith(CHECK))
const checks = (w: Prompts, i = -1) => all(w, i).filter(n => n.startsWith(CHECK))

test('a prompt carries no mode note while no mode was ever set', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await submit($)
  expect(notes(w)).toEqual([])
})

test('the prompt after /mode readonly carries the Read only note once', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await submit($)
  expect(notes(w)).toHaveLength(1)
  expect(notes(w)[0]).toMatch(/^Session mode: Read only is on\. Read only mode: read and report only\./)
  await submit($)
  expect(notes(w)).toEqual([])
})

test('the prompt after the band Turn off button carries the off note', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await submit($)
  const band = await mount($, { surface: 'desktop' })
  await band.press({ key: 'off' })
  await submit($)
  expect(notes(w)).toHaveLength(1)
  expect(notes(w)[0]).toMatch(/^Session mode: off\. Read only mode has ended/)
})

test('two mode changes before a prompt give one note, the last mode', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await mode($ as never, 'build')
  await submit($)
  expect(notes(w)).toHaveLength(1)
  expect(notes(w)[0]).toMatch(/^Session mode: Build is on\. Build mode:/)
})

test('a mode set and cleared before any prompt gives no note', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await mode($ as never, 'off')
  await submit($)
  expect(notes(w)).toEqual([])
})

test('the mode note goes after the context a prompt already has', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  const out = await submit($, 'hello', ['x'])
  expect(notes(w)).toHaveLength(2)
  expect(notes(w)[0]).toBe('x')
  expect(notes(w)[1]).toMatch(/^Session mode: Read only is on\./)
  expect(out.context).toEqual(notes(w))
})

test('a composer prompt with nothing set carries one check note, last, with Now: off.', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await submit($)
  expect(checks(w)).toHaveLength(1)
  expect(all(w).at(-1)).toBe(checks(w)[0])
  expect(checks(w)[0]).toMatch(/Now: off\./)
})

test('after agent_mode readonly self, the next check note says Now: readonly.', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await $.tool.call({ tool: 'mcp__session-modes__agent_mode', mode: 'readonly', scope: 'self' } as never)
  await submit($)
  expect(checks(w)).toHaveLength(1)
  expect(checks(w)[0]).toMatch(/Now: readonly\./)
})

test('the check note goes after the context and the mode note', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'build')
  const out = await submit($, 'hello', ['x'])
  expect(all(w)).toHaveLength(3)
  expect(all(w)[0]).toBe('x')
  expect(all(w)[1]).toMatch(/^Session mode: Build is on\./)
  expect(all(w)[2]).toMatch(/^Session mode check:/)
  expect(out.context).toEqual(all(w))
})

for (const kind of ['bridge', 'sdk']) {
  test(`a ${kind} prompt carries the check note`, async ($, on) => {
    const w = world(on)
    await start($ as never)
    await submit($, 'hello', undefined, { origin: { kind } })
    expect(checks(w)).toHaveLength(1)
  })
}

for (const kind of ['task-notification', 'scheduled-trigger', 'peer']) {
  test(`a ${kind} prompt carries no check note`, async ($, on) => {
    const w = world(on)
    await start($ as never)
    await submit($, 'hello', undefined, { origin: { kind } })
    expect(checks(w)).toEqual([])
  })
}

test('a meta prompt carries no check note', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await submit($, 'hello', undefined, { isMeta: true })
  expect(checks(w)).toEqual([])
})

test('/mode agents off stops the check note and /mode agents on brings it back', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'agents off')
  await submit($)
  expect(checks(w)).toEqual([])
  await mode($ as never, 'agents on')
  await submit($)
  expect(checks(w)).toHaveLength(1)
})

test('the check note is skipped while the user mode is readonly, not for research', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await submit($)
  expect(checks(w)).toEqual([])
  await mode($ as never, 'research')
  await submit($)
  expect(checks(w)).toHaveLength(1)
})

const TOOL = 'mcp__session-modes__agent_mode'
const DESCRIPTION =
  'Set a working mode for yourself (scope "self") or for your subagents (scope "subagents"); it applies at once, also to subagents already running, and subagents you start later get it in their task text. Modes: readonly (read and report only), research (notes, plans and tracker items; no code), prototype (a Claude Design artifact or files in .claude/work/; no app code), build (edit and commit; no push or PR). "off" clears the mode you set in that scope. You can only add limits: a mode the user set with /mode stays in force, and the stricter rule always wins. Pick your own mode at the start of each user message, read with the conversation: readonly for a question, a review, an explanation or "do not change anything"; research for a plan, a spec, notes or tickets; prototype for a UI idea, a layout choice or a design to see before the build; build for a code or config change; off only when the message asks you to push, or to open or merge a pull request. A short reply such as "yes" or "go ahead" takes the mode of the work it approves.'

const claudeSets = async ($: any, modeName: string, scope: string, agentId?: string): Promise<string> => {
  const out = await $.tool.call({ tool: TOOL, mode: modeName, scope, ...(agentId ? { agentId } : {}) } as never)
  expect(typeof out.result).toBe('string')
  return out.result as string
}
const editAs = ($: any, agentId?: string) => $.tool.call({ tool: 'Edit', ...(agentId ? { agentId } : {}) } as never)
const pushAs = ($: any, agentId?: string) => $.tool.call({ tool: 'Bash', command: 'git push', ...(agentId ? { agentId } : {}) } as never)
const prAs = ($: any, agentId?: string) => $.tool.call({ tool: 'Bash', command: 'gh pr create', ...(agentId ? { agentId } : {}) } as never)

const READONLY_NOTE_START = 'The agent that started you set Read only mode for its subagents'

test('the agent_mode tool is registered and not deferred', async ($, on) => {
  const w = world(on)
  await start($ as never)
  expect(w.tools).toHaveLength(1)
  expect(w.tools[0]!.name).toBe('agent_mode')
  expect(w.tools[0]!.isDeferred).toBe(false)
  expect(w.tools[0]!.description).toBe(DESCRIPTION)
  expect(w.tools[0]!.inputSchema).toEqual({
    type: 'object',
    properties: {
      mode: { type: 'string', enum: ['readonly', 'research', 'prototype', 'build', 'off'] },
      scope: { type: 'string', enum: ['self', 'subagents'] },
    },
    required: ['mode', 'scope'],
  })
})

test('agent_mode with an unknown mode or scope is refused and sets nothing', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  const bad = await $.tool.call({ tool: TOOL, mode: 'strict', scope: 'self' } as never)
  expect((bad as { deny?: string }).deny).toMatch(/^agent_mode needs a mode/)
  const noScope = await $.tool.call({ tool: TOOL, mode: 'readonly', scope: 'everyone' } as never)
  expect((noScope as { deny?: string }).deny).toMatch(/^agent_mode needs a mode/)
  expect(blocked(await editAs($))).toBe(false)
})

test('a mode the model sets for subagents reaches the next subagent and its calls', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  const w = world(on)
  await start($ as never)
  expect(await claudeSets($, 'readonly', 'subagents')).toBe('Your subagents are now in Read only mode, also those already running.')
  await spawn($)
  expect(w.spawned[0]!.startsWith(READONLY_NOTE_START)).toBe(true)
  expect(w.spawned[0]).toBe(
    'The agent that started you set Read only mode for its subagents, and it applies to you. Read only mode: read and report only. Do not edit files, commit, push, open pull requests or write to trackers; list findings instead. Tool calls that break it are denied.\n\nFind the bug.',
  )
  const out = await editAs($, 'a1')
  expect(out.deny).toMatch(/set by the agent that started you\.$/)
  expect(out.deny).toMatch(/^readonly mode is on: report the change instead of making it; /)
  expect(blocked(await editAs($))).toBe(false)
})

test('a mode the model sets for itself denies its own calls', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  const text = await claudeSets($, 'readonly', 'self')
  expect(text).toMatch(/^You are now in Read only mode\. Read only mode: read and report only\./)
  const out = await editAs($)
  expect(out.deny).toMatch(/agent_mode off with scope self to leave\.$/)
})

test('the model clears the mode it set for itself', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'self')
  expect(await claudeSets($, 'off', 'self')).toBe('Cleared the Read only mode you set for yourself.')
  expect(blocked(await editAs($))).toBe(false)
})

test('the model clears the mode it set for subagents', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await claudeSets($, 'build', 'subagents')
  expect(await claudeSets($, 'off', 'subagents')).toBe('Cleared the Build mode you set for your subagents.')
})

test('off with nothing set says so', async ($, on) => {
  world(on)
  await start($ as never)
  expect(await claudeSets($, 'off', 'self')).toBe('No mode was set for that scope.')
  expect(await claudeSets($, 'off', 'subagents')).toBe('No mode was set for that scope.')
})

test('the model cannot loosen the mode the user set', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  const text = await claudeSets($, 'off', 'self')
  expect(text).toBe("No mode was set for that scope. The user's Read only mode stays on.")
  expect(text.endsWith("The user's Read only mode stays on.")).toBe(true)
  expect(blocked(await editAs($))).toBe(true)
})

test('a self result names the user mode that stays on', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'build')
  expect(await claudeSets($, 'readonly', 'self')).toMatch(/The user's Build mode stays on\.$/)
})

test('the stricter rule wins: the user rule is checked first', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'build')
  await claudeSets($, 'readonly', 'subagents')
  await spawn($)
  expect(w.spawned[0]!.startsWith('The main session is in Build mode')).toBe(true)
  expect(w.spawned[0]).toContain(READONLY_NOTE_START)
  const edit = await editAs($, 'a1')
  expect(edit.deny).toMatch(/^readonly mode is on: /)
  const push = await pushAs($, 'a1')
  expect(push.deny).toBe('build mode is on: commit locally and leave the push and the pull request to the user; /mode off to leave.')
})

test('a nested subagent inherits the mode through its parent', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  const w = world(on)
  await start($ as never)
  await claudeSets($, 'build', 'subagents')
  await spawn($)
  await spawn($, { parentAgentId: 'a1' })
  expect(w.spawned[1]).toMatch(/^The agent that started you set Build mode for its subagents, and it applies to you\. Build mode:/)
  expect(blocked(await prAs($, 'a2'))).toBe(true)
  expect(blocked(await editAs($, 'a2'))).toBe(false)
})

test('a subagent sets a mode for its own subagents', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await spawn($)
  await spawn($, { parentAgentId: 'a1' })
  expect(await claudeSets($, 'readonly', 'subagents', 'a1')).toBe('Your subagents are now in Read only mode, also those already running.')
  expect(blocked(await editAs($, 'a1'))).toBe(false)
  expect(blocked(await editAs($, 'a2'))).toBe(true)
  expect(blocked(await editAs($))).toBe(false)
})

test('a subagent sets a mode for itself without touching the main thread', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await spawn($)
  await claudeSets($, 'readonly', 'self', 'a1')
  expect((await editAs($, 'a1')).deny).toMatch(/agent_mode off with scope self to leave\.$/)
  expect(blocked(await editAs($))).toBe(false)
})

test('the agent_mode tool is never denied', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  const out = await $.tool.call({ tool: TOOL, mode: 'readonly', scope: 'subagents' } as never)
  expect(blocked(out)).toBe(false)
  await claudeSets($, 'readonly', 'self')
  expect(blocked(await $.tool.call({ tool: TOOL, mode: 'off', scope: 'self' } as never))).toBe(false)
})

test('/mode off clears the modes the model set', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'subagents')
  await claudeSets($, 'readonly', 'self')
  await spawn($)
  expect(blocked(await editAs($, 'a1'))).toBe(true)
  await mode($ as never, 'off')
  expect(blocked(await editAs($, 'a1'))).toBe(false)
  expect(blocked(await editAs($))).toBe(false)
})

test('the band Turn off button clears the modes the model set', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await mode($ as never, 'build')
  await claudeSets($, 'readonly', 'self')
  const band = await mount($, { surface: 'desktop' })
  await band.press({ key: 'off' })
  expect(blocked(await editAs($))).toBe(false)
})

test('setting a user mode keeps the modes the model set', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'self')
  await mode($ as never, 'build')
  expect(blocked(await editAs($))).toBe(true)
})

test('a mode set by the model alone shows one row and no Turn off button', async ($, on) => {
  world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'self')
  const band = await mount($, { surface: 'desktop' })
  expect(await band.find({ text: 'Set by Claude: Read only for itself' })).toBeDefined()
  expect(await band.find({ type: 'Button', key: 'off' })).toBeUndefined()
  expect(await band.find({ text: 'Read and report only.' })).toBeUndefined()
})

test('each mode on the Set by Claude row is drawn in its own colour, as on the user row', async ($, on) => {
  world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'self')
  await claudeSets($, 'build', 'subagents')
  const band = await mount($, { surface: 'desktop' })
  const own = (await band.find({ type: 'Text', text: /^Read only$/ })) as { props: { color?: string } } | undefined
  const subs = (await band.find({ type: 'Text', text: /^Build$/ })) as { props: { color?: string } } | undefined
  expect(own?.props.color).toBe('planMode')
  expect(subs?.props.color).toBe('ide')
})

test('the band shows the user mode row and a Set by Claude row', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'build')
  await claudeSets($, 'readonly', 'subagents')
  const band = await mount($, { surface: 'desktop' })
  expect(await band.find({ type: 'Text', text: /^Build$/ })).toBeDefined()
  expect(await band.find({ text: 'Edits and commits are allowed.' })).toBeDefined()
  expect(await band.find({ type: 'Button', key: 'off' })).toBeDefined()
  expect(await band.find({ text: 'Set by Claude: Read only for subagents' })).toBeDefined()
})

test('the band hides a Claude mode that the user mode already covers', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await claudeSets($, 'readonly', 'self')
  await claudeSets($, 'build', 'subagents')
  const band = await mount($, { surface: 'desktop' })
  expect(await band.find({ text: 'Read and report only.' })).toBeDefined()
  expect(await band.find({ text: /Set by Claude/ })).toBeUndefined()
  expect(await band.find({ type: 'Button', key: 'clear-agents' })).toBeUndefined()
  expect((await mode($ as never)).text).not.toContain('Set by Claude')
})

test('the band keeps only the Claude scope that is stricter than the user mode', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'research')
  await claudeSets($, 'build', 'self')
  await claudeSets($, 'readonly', 'subagents')
  const band = await mount($, { surface: 'desktop' })
  expect(await band.find({ text: 'Set by Claude: Read only for subagents' })).toBeDefined()
})

test('a covered Claude mode shows again when the user loosens the mode', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await claudeSets($, 'readonly', 'self')
  await mode($ as never, 'build')
  const band = await mount($, { surface: 'desktop' })
  expect(await band.find({ text: 'Set by Claude: Read only for itself' })).toBeDefined()
})

test('the Set by Claude row joins both scopes', async ($, on) => {
  world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'self')
  await claudeSets($, 'build', 'subagents')
  const band = await mount($, { surface: 'desktop' })
  expect(await band.find({ text: 'Set by Claude: Read only for itself and Build for subagents' })).toBeDefined()
})

test('the Set by Claude row yields to a survey', async ($, on) => {
  world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'self')
  const band = await mount($, { surface: 'desktop', over: { hasSurvey: true } })
  expect(await band.find({ text: /Set by Claude/ })).toBeUndefined()
})

test('/mode alone reports the modes the model set', async ($, on) => {
  world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'subagents')
  expect((await mode($ as never)).text).toBe(
    'Current mode: off. Modes: readonly, research, prototype, build, off. Also: clear, agents on, agents off. Set by Claude: Read only for subagents.',
  )
})

test('/mode alone is unchanged when the model set nothing', async ($, on) => {
  world(on)
  await start($ as never)
  expect((await mode($ as never)).text).toBe(
    'Current mode: off. Modes: readonly, research, prototype, build, off. Also: clear, agents on, agents off.',
  )
})

test('a workflow agent gets the inherited mode and its calls are denied', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  const w = world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'subagents')
  await spawn($, { workflow: { runId: 'wf_x', agentIndex: 1 } })
  expect(w.spawned[0]).toContain(READONLY_NOTE_START)
  expect(blocked(await editAs($, 'a1'))).toBe(true)
})

test('a mode equal to the user mode is not repeated in the subagent note', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await claudeSets($, 'readonly', 'subagents')
  await spawn($)
  expect(w.spawned[0]).not.toContain(READONLY_NOTE_START)
  expect(w.spawned[0]!.startsWith('The main session is in Read only mode')).toBe(true)
})

const CLEARED_SELF =
  'Session mode: the user cleared the modes you set (Read only for itself). They no longer apply.'
const AGENTS_OFF_NOTE = 'Session mode: the user turned off agent_mode. Do not call it.'
const AGENTS_ON_NOTE = 'Session mode: the user turned agent_mode back on.'
const AGENTS_OFF_DENY = 'The user turned off agent modes with /mode agents off.'

test('the band Clear button clears the modes the model set and tells the model', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  const w = world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'self')
  expect(blocked(await editAs($))).toBe(true)
  const band = await mount($, { surface: 'desktop' })
  await band.press({ key: 'clear-agents' })
  expect(blocked(await editAs($))).toBe(false)
  expect(w.toasts).toEqual(["Claude's modes cleared."])
  await submit($)
  expect(notes(w)).toEqual([CLEARED_SELF])
})

test('the Clear button is only on the Set by Claude row', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'build')
  const band = await mount($, { surface: 'desktop' })
  expect(await band.find({ type: 'Button', key: 'clear-agents' })).toBeUndefined()
  await claudeSets($, 'readonly', 'subagents')
  const withClaude = await mount($, { surface: 'desktop' })
  expect(await withClaude.find({ type: 'Button', key: 'clear-agents' })).toBeDefined()
  expect(await withClaude.find({ type: 'Button', key: 'off' })).toBeDefined()
})

test('the Clear button note names subagent modes set by a subagent', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await spawn($)
  await claudeSets($, 'readonly', 'subagents', 'a1')
  await mode($ as never, 'clear')
  await submit($)
  expect(notes(w)).toEqual(['Session mode: the user cleared the modes you set (modes set by subagents). They no longer apply.'])
})

test('/mode clear removes the model modes and keeps the user mode', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await mode($ as never, 'build')
  await claudeSets($, 'readonly', 'self')
  expect(blocked(await editAs($))).toBe(true)
  expect((await mode($ as never, 'clear')).text).toBe("Cleared Claude's modes.")
  expect(blocked(await editAs($))).toBe(false)
  expect(blocked(await prAs($))).toBe(true)
})

test('/mode clear with nothing set says so and adds no note', async ($, on) => {
  const w = world(on)
  await start($ as never)
  expect((await mode($ as never, 'clear')).text).toBe('Claude has no modes set.')
  await submit($)
  expect(notes(w)).toEqual([])
})

test('/mode off after the model set a mode carries the cleared note', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'self')
  await mode($ as never, 'off')
  await submit($)
  expect(notes(w)).toEqual([CLEARED_SELF])
})

test('/mode agents off denies agent_mode, clears model modes and tells the model', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  const w = world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'self')
  expect((await mode($ as never, 'agents off')).text).toBe('Agent modes off. Claude cannot set modes.')
  const out = await $.tool.call({ tool: TOOL, mode: 'readonly', scope: 'self' } as never)
  expect((out as { deny?: string }).deny).toBe(AGENTS_OFF_DENY)
  expect(blocked(await editAs($))).toBe(false)
  await submit($)
  expect(notes(w)).toEqual([CLEARED_SELF, AGENTS_OFF_NOTE])
})

test('with agent modes off an off call returns the normal result', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'agents off')
  expect(await claudeSets($, 'off', 'self')).toBe('No mode was set for that scope.')
})

test('/mode agents on lets the tool work again and tells the model', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'agents off')
  await submit($)
  expect((await mode($ as never, 'agents on')).text).toBe('Agent modes on.')
  expect(await claudeSets($, 'readonly', 'subagents')).toBe('Your subagents are now in Read only mode, also those already running.')
  await submit($)
  expect(notes(w)).toEqual([AGENTS_ON_NOTE])
})

test('/mode agents with another value changes nothing', async ($, on) => {
  const w = world(on)
  await start($ as never)
  expect((await mode($ as never, 'agents maybe')).text).toBe('Use /mode agents off or /mode agents on.')
  expect((await mode($ as never, 'agents')).text).toBe('Use /mode agents off or /mode agents on.')
  expect(await claudeSets($, 'readonly', 'self')).toMatch(/^You are now in Read only mode/)
  await submit($)
  expect(notes(w)).toEqual([])
})

test('/mode alone ends with Agent modes: off while agent modes are off', async ($, on) => {
  world(on)
  await start($ as never)
  await mode($ as never, 'agents off')
  expect((await mode($ as never)).text).toBe(
    'Current mode: off. Modes: readonly, research, prototype, build, off. Also: clear, agents on, agents off. Agent modes: off.',
  )
})

test('pending notes are sent once', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'agents off')
  await submit($)
  expect(notes(w)).toEqual([AGENTS_OFF_NOTE])
  await submit($)
  expect(notes(w)).toEqual([])
})

test('pending notes follow the mode note and the caller context', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  await mode($ as never, 'agents off')
  await submit($, 'hello', ['x'])
  expect(notes(w)[0]).toBe('x')
  expect(notes(w)[1]).toMatch(/^Session mode: Read only is on\./)
  expect(notes(w)[2]).toBe(AGENTS_OFF_NOTE)
})

test('the mode argument tolerates case and spaces', async ($, on) => {
  world(on)
  await start($ as never)
  expect((await mode($ as never, '  AGENTS  OFF ')).text).toBe('Agent modes off. Claude cannot set modes.')
  expect((await mode($ as never, ' Agents   On')).text).toBe('Agent modes on.')
  expect((await mode($ as never, '  CLEAR ')).text).toBe('Claude has no modes set.')
})

test('a resume by another parent keeps the first parent link', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await spawn($)
  await spawn($, { parentAgentId: 'a1' })
  await claudeSets($, 'readonly', 'subagents', 'a1')
  await spawn($, { prompt: 'Go on.', resume: { agentId: 'a2' } })
  expect(blocked(await editAs($, 'a2'))).toBe(true)
})

test('a resume of an agent with no link records the resumer as its parent', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  world(on)
  await start($ as never)
  await spawn($)
  await claudeSets($, 'readonly', 'subagents')
  await spawn($, { prompt: 'Go on.', resume: { agentId: 'a9' } })
  expect(blocked(await editAs($, 'a9'))).toBe(true)
})

test('a tool call fails closed when the guard cannot read its state', async ($, on) => {
  on('tool.call', () => ({ result: 'ok' }) as never)
  const w = world(on)
  await start($ as never)
  await claudeSets($, 'readonly', 'self')
  expect(blocked(await editAs($))).toBe(true)
  w.throwGet = 'agentModes'
  const out = await editAs($)
  expect(out.deny).toMatch(/^session-modes: /)
})

test('a spawn that fails before next passes the task on and shows a toast', async ($, on) => {
  const w = world(on)
  await start($ as never)
  await mode($ as never, 'readonly')
  w.throwGet = 'agentModes'
  const out = await spawn($)
  expect(w.spawned).toEqual(['Find the bug.'])
  expect(out.agentId).toBe('a1')
  expect(w.toasts.some(t => t.startsWith('session-modes: '))).toBe(true)
})

test('a spawn that fails after next starts the agent once and shows a toast', async ($, on) => {
  const w = world(on)
  await start($ as never)
  w.throwSet = 'parents'
  const out = await spawn($)
  expect(w.spawnCount).toBe(1)
  expect(out.agentId).toBe('a1')
  expect(w.toasts.some(t => t.startsWith('session-modes: '))).toBe(true)
})
