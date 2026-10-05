import { expect, mock, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On } from 'claude-code'

const PROGRESS = 'mcp__work-pane__progress'
const SURFACES = ['terminal', 'desktop'] as const

function world(on: On) {
  let next = 0
  on('tool.call', () => ({ result: 'ok' }) as never)
  on('classic.SubagentStop', () => ({}) as never)
  on('agent.spawn', ($, e) => ({ model: e.subagentType === 'Explore' ? 'claude-haiku-4-5' : 'claude-sonnet-5-5', agentId: `a${++next}` }))
}

const mounted = new WeakMap<Engine, Awaited<ReturnType<Engine['ui']['mount']>>>()

async function pane($: Engine, surface: (typeof SURFACES)[number]) {
  const drawn = mounted.get($) ?? (await $.ui.mount({
    plugin: 'work-pane',
    surface,
    component: 'Pane',
    requestId: 'work',
    props: { title: 'Work', isFocused: false, bodyColumns: 48, placement: 'dock', scroll: { bodyRows: 30 } } as never,
  }))
  mounted.set($, drawn)
  const texts = (await drawn.findAll({ type: 'Text' })).map(t => t.text)
  return texts.join('\n')
}

const progress = ($: Engine, input: Record<string, unknown>) => $.tool.call({ tool: PROGRESS, ...input } as never)
const spawn = ($: Engine, description: string, subagentType: string, model?: string) =>
  $.agent.spawn({ tool_use_id: `t-${description}`, prompt: 'p', description, subagentType, model } as never)

for (const surface of SURFACES) {
  test(`${surface}: an empty pane says nothing is running`, async ($, on) => {
    world(on)
    const text = await pane($, surface)
    expect(text).toMatch(/No task in progress/)
    expect(text).toMatch(/No subagents yet/)
  })

  test(`${surface}: a plan shows its title, count and current step`, async ($, on) => {
    world(on)
    await progress($, { title: 'MP-77 rules', steps: ['scout', 'spec', 'build', 'test', 'commit'] })
    let text = await pane($, surface)
    expect(text).toMatch(/MP-77 rules/)
    expect(text).toMatch(/0\/5/)
    expect(text).toMatch(/Now: scout/)
    await progress($, { done: 3 })
    text = await pane($, surface)
    expect(text).toMatch(/3\/5/)
    expect(text).toMatch(/Now: test/)
  })

  test(`${surface}: done is clamped to the plan`, async ($, on) => {
    world(on)
    await progress($, { title: 't', steps: ['a', 'b'] })
    await progress($, { done: 9 })
    expect(await pane($, surface)).toMatch(/2\/2/)
    await progress($, { done: -4 })
    expect(await pane($, surface)).toMatch(/0\/2/)
  })

  test(`${surface}: clear empties the plan`, async ($, on) => {
    world(on)
    await progress($, { title: 't', steps: ['a'] })
    await progress($, { clear: true })
    expect(await pane($, surface)).toMatch(/No task in progress/)
  })

  test(`${surface}: a subagent row shows type, task and model, then its last tool`, async ($, on) => {
    world(on)
    await spawn($, 'find rule files', 'Explore', 'haiku')
    let text = await pane($, surface)
    expect(text).toMatch(/Explore/)
    expect(text).toMatch(/find rule files/)
    expect(text).toMatch(/haiku/)
    await $.tool.call({ tool: 'Read', file_path: '/x/linear.md', agentId: 'a1' } as never)
    text = await pane($, surface)
    expect(text).toMatch(/Read/)
  })

  test(`${surface}: main-loop tool calls add no subagent row`, async ($, on) => {
    world(on)
    await $.tool.call({ tool: 'Read', file_path: '/x' } as never)
    expect(await pane($, surface)).toMatch(/No subagents yet/)
  })

  test(`${surface}: a stopped subagent shows as done`, async ($, on) => {
    world(on)
    await spawn($, 'docs lookup', 'researcher')
    await $.classic.SubagentStop({ agent_id: 'a1', agent_type: 'researcher', stop_hook_active: false } as never)
    expect(await pane($, surface)).toMatch(/done/)
  })

  test(`${surface}: only the newest eight subagents are listed`, async ($, on) => {
    world(on)
    for (let i = 1; i <= 10; i++) await spawn($, `job ${i}`, 'Explore')
    const text = await pane($, surface)
    expect(text).toMatch(/job 10/)
    expect(text).toMatch(/job 3\b/)
    expect(text).not.toMatch(/job 2\b/)
  })
}

for (const surface of SURFACES) {
  test(`${surface}: a subagent that hands back its report shows as done`, async ($, on) => {
    world(on)
    await spawn($, 'list mod files', 'Explore')
    await $.tool.call({ tool: 'SubagentHandback', agentId: 'a1' } as never)
    const text = await pane($, surface)
    expect(text).toMatch(/done/)
    expect(text).not.toMatch(/SubagentHandback/)
  })

  test(`${surface}: a subagent the engine no longer runs shows as done on the next tick`, async ($, on) => {
    world(on)
    const clock = mock.clock(on)
    on('tool.register', () => ({ value: { tool: 'mcp__work-pane__progress' } }) as never)
    on('command.register', () => ({ value: {} }) as never)
    on('ui.open', () => ({ value: true }) as never)
    on('session.start', ($, e) => e as never)
    let status = 'running'
    on('agent.list', () => ({ value: [{ id: 'a1', description: 'scan', type: 'Explore', status }] }) as never)
    await $.session.start({ cwd: '/tmp' } as never)
    await spawn($, 'scan', 'Explore')
    await clock.advance(1000)
    expect(await pane($, surface)).not.toMatch(/done/)
    status = 'killed'
    await clock.advance(1000)
    expect(await pane($, surface)).toMatch(/done/)
  })
}

test('progress without a plan answers without throwing', async ($, on) => {
  world(on)
  const out = await progress($, { done: 2 })
  expect(out.deny).toBe(undefined)
})

test('the progress tool never asks the Linear gate', async ($, on) => {
  let asked = 0
  on('tool.call', { tool: 'AskUserQuestion' }, () => (asked++, { deny: 'no' }))
  world(on)
  await progress($, { title: 't', steps: ['a'] })
  expect(asked).toBe(0)
})
