import { expect, test } from 'claude-code/testing'

const LOG = '/private/tmp/scratch/headless.log'

function world(on: Parameters<Parameters<typeof test>[1]>[1]) {
  const opened: string[] = []
  const commands: string[] = []
  const asked: string[] = []
  const ran: string[] = []
  on('command.register', (_$, e) => (commands.push((e as { name: string }).name), { value: {} }) as never)
  on('ui.open', (_$, e) => (opened.push((e as { id: string }).id), { value: true }) as never)
  on('ui.toast', () => undefined)
  on('session.start', (_$, e) => e as never)
  on('tool.call', (_$, e) => {
    if (e.tool === 'AskUserQuestion') {
      asked.push((e as { questions: { question: string }[] }).questions[0].question)
      return { deny: 'dismissed' } as never
    }
    ran.push(e.tool)
    return { result: 'ok', text: 'ok' } as never
  })
  return { opened, commands, asked, ran }
}

test('a non-interactive session registers no tests command', async ($, on) => {
  const w = world(on)
  await $.session.start({ cwd: '/tmp', isInteractive: false } as never)
  expect(w.commands).not.toContain('tests')
})

test('an interactive session registers the tests command', async ($, on) => {
  const w = world(on)
  await $.session.start({ cwd: '/tmp', isInteractive: true } as never)
  expect(w.commands).toContain('tests')
})

test('a tee-d test command in a non-interactive session opens no pane', async ($, on) => {
  const w = world(on)
  await $.session.start({ cwd: '/tmp', isInteractive: false } as never)
  await $.tool.call({ tool: 'Bash', command: `pytest | tee ${LOG}` } as never)
  expect(w.opened).toEqual([])
})

test('a Linear write in a non-interactive session is still asked about', async ($, on) => {
  const w = world(on)
  await $.session.start({ cwd: '/tmp', isInteractive: false } as never)
  const out = await $.tool.call({ tool: 'mcp__linear-server__save_issue', id: 'ABC-1', state: 'Done' } as never)
  expect(w.asked.length).toBe(1)
  expect(w.ran).toEqual([])
  expect(out.deny).toBeDefined()
})
