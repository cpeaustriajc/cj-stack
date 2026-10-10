import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

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

test('a Linear write in a host with no surfaces is left to the host\'s approval', async ($, on) => {
  const w = world(on, [])
  await $.session.start({ cwd: '/tmp', isInteractive: false } as never)
  const out = await $.tool.call(write as never)
  expect(w.asked).toEqual([])
  expect(w.ran).toEqual([write.tool])
  expect(out.deny).toBe(undefined)
})

test('a non-interactive session that still has a surface asks about a Linear write', async ($, on) => {
  const w = world(on, ['terminal'])
  await $.session.start({ cwd: '/tmp', isInteractive: false } as never)
  const out = await $.tool.call(write as never)
  expect(w.asked.length).toBe(1)
  expect(w.ran).toEqual([])
  expect(out.deny).toBeDefined()
})
