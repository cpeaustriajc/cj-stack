import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'
import type { Engine } from 'claude-code/testing'

// These tests drive the dialog: an on-shift clock in UTC, and a dialog for every write.
type Body = ($: Engine, on: On) => unknown
const asking = (name: string, body: Body) =>
  test(name, { options: { timeZone: 'UTC', onShift: 'ask' } }, (($: Engine, on: On) => {
    on('clock.now', () => ({ value: Date.UTC(2026, 9, 15, 10) }) as never)
    return body($, on)
  }) as never)

function world(on: On, surfaces: readonly string[]) {
  const asked: string[] = []
  const ran: string[] = []
  on('ui.toast', () => undefined)
  on('session.surfaces', () => ({ value: surfaces }) as never)
  on('session.start', (_$, e) => e as never)
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

const write = { tool: 'mcp__linear-server__save_issue', id: 'ABC-1', state: 'Done' }

asking('a Linear write in a host with no surfaces is left to the host\'s approval', async ($, on) => {
  const w = world(on, [])
  await $.session.start({ cwd: '/tmp', isInteractive: false } as never)
  const out = await $.tool.call(write as never)
  expect(w.asked).toEqual([])
  expect(w.ran).toEqual([write.tool])
  expect(out.deny).toBe(undefined)
})

asking('a non-interactive session that still has a surface asks about a Linear write', async ($, on) => {
  const w = world(on, ['terminal'])
  await $.session.start({ cwd: '/tmp', isInteractive: false } as never)
  const out = await $.tool.call(write as never)
  expect(w.asked.length).toBe(1)
  expect(w.ran).toEqual([])
  expect(out.deny).toBeDefined()
})
