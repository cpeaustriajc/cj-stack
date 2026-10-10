import { expect, mock, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On } from 'claude-code'

const SURFACES = ['terminal', 'desktop'] as const
const LOG = '/private/tmp/scratch/e2e.log'

const opened: string[] = []

function world(on: On, logs: Record<string, string>, opts: { bashFails?: boolean; tailFails?: boolean } = {}) {
  opened.length = 0
  const clock = mock.clock(on)
  on('tool.register', () => ({ value: { tool: 'mcp__work-pane__progress' } }) as never)
  on('command.register', () => ({ value: {} }) as never)
  on('ui.open', ($, e) => (opened.push((e as { id: string }).id), { value: true }) as never)
  on('agent.list', () => ({ value: [] }) as never)
  on('session.start', ($, e) => e as never)
  on('process.run', ($, e) => {
    if (opts.tailFails) return { deny: 'no tail' } as never
    const path = (e as { argv: string[] }).argv.at(-1)!
    return { value: { exitCode: 0, stdout: logs[path] ?? '', stderr: '' } } as never
  })
  on('tool.call', () => (opts.bashFails ? { result: 'exit 1', text: 'exit 1', isError: true } : { result: 'ok', text: 'ok' }) as never)
  return clock
}

const mounted = new WeakMap<Engine, Awaited<ReturnType<Engine['ui']['mount']>>>()

async function pane($: Engine, surface: (typeof SURFACES)[number], requestId = 'tests') {
  const key = $
  const drawn =
    mounted.get(key) ??
    (await $.ui.mount({
      plugin: 'work-pane',
      surface,
      component: 'Pane',
      requestId,
      props: { title: 'Work', isFocused: false, bodyColumns: 60, placement: 'dock', scroll: { bodyRows: 40 } } as never,
    }))
  mounted.set(key, drawn)
  return (await drawn.findAll({ type: 'Text' })).map(t => t.text).join('\n')
}

const bash = ($: Engine, command: string, background = false) =>
  $.tool.call({ tool: 'Bash', command, run_in_background: background } as never)

for (const surface of SURFACES) {
  test(`${surface}: a background run piped through tee shows live counts`, async ($, on) => {
    const logs: Record<string, string> = { [LOG]: '' }
    const clock = world(on, logs)
    await $.session.start({ cwd: '/tmp' } as never)
    await bash($, `uv run pytest e2e 2>&1 | tee ${LOG}`, true)
    let text = await pane($, surface)
    expect(text).toMatch(/uv run pytest e2e/)
    logs[LOG] = '[11/146] ✔ Cart (12s) pass 10 fail 1\n[12/146] ✔ Suite test (19s) pass 11 fail 1\n'
    await clock.advance(1000)
    text = await pane($, surface)
    expect(text).toMatch(/12\/146/)
    expect(text).toMatch(/pass 11 fail 1/)
  })

  test(`${surface}: a background run ends when the last unit is reached`, async ($, on) => {
    const logs: Record<string, string> = { [LOG]: '' }
    const clock = world(on, logs)
    await $.session.start({ cwd: '/tmp' } as never)
    await bash($, `pnpm test | tee -a ${LOG}`, true)
    logs[LOG] = '[3/3] ✔ Last (1s) pass 3 fail 0\n'
    await clock.advance(1000)
    const text = await pane($, surface)
    expect(text).toMatch(/3\/3/)
    expect(text).toMatch(/✓/)
  })

  test(`${surface}: a foreground run shows its final counts and a cross when it fails`, async ($, on) => {
    const logs: Record<string, string> = { [LOG]: '[5/9] ✘ Checkout (4s) pass 4 fail 1\n' }
    world(on, logs, { bashFails: true })
    await $.session.start({ cwd: '/tmp' } as never)
    await bash($, `pytest | tee ${LOG}`)
    const text = await pane($, surface)
    expect(text).toMatch(/5\/9/)
    expect(text).toMatch(/✗/)
  })

  test(`${surface}: a run opens the Tests pane`, async ($, on) => {
    world(on, {})
    await $.session.start({ cwd: '/tmp' } as never)
    await bash($, `pytest | tee ${LOG}`)
    expect(opened).toContain('tests')
  })

  test(`${surface}: an empty Tests pane says no runs yet`, async ($, on) => {
    world(on, {})
    await $.session.start({ cwd: '/tmp' } as never)
    expect(await pane($, surface)).toMatch(/No test runs yet/)
  })

  test(`${surface}: tee inside a heredoc body adds no test row`, async ($, on) => {
    world(on, {})
    await $.session.start({ cwd: '/tmp' } as never)
    await bash($, `cd /x && python3 - <<'EOF'\ns = "pytest | tee /tmp/a.log"\nEOF`)
    await bash($, `cat > /tmp/s.sh <<'EOF'\npnpm test | tee /tmp/b.log\nEOF`)
    expect(await pane($, surface)).toMatch(/No test runs yet/)
  })

  test(`${surface}: a command without tee adds no test row`, async ($, on) => {
    world(on, {})
    await $.session.start({ cwd: '/tmp' } as never)
    await bash($, 'pytest -q')
    expect(await pane($, surface)).not.toMatch(/pytest/)
  })

  test(`${surface}: an unreadable log keeps the row running without counts`, async ($, on) => {
    const clock = world(on, {}, { tailFails: true })
    await $.session.start({ cwd: '/tmp' } as never)
    await bash($, `pytest | tee ${LOG}`, true)
    await clock.advance(1000)
    const text = await pane($, surface)
    expect(text).toMatch(/pytest/)
    expect(text).toMatch(/running/)
  })

  test(`${surface}: only the newest three runs are listed`, async ($, on) => {
    world(on, {})
    await $.session.start({ cwd: '/tmp' } as never)
    for (let i = 1; i <= 5; i++) await bash($, `run-suite-${i} | tee /tmp/r${i}.log`)
    const text = await pane($, surface)
    expect(text).toMatch(/run-suite-5/)
    expect(text).toMatch(/run-suite-3/)
    expect(text).not.toMatch(/run-suite-2/)
  })
}
