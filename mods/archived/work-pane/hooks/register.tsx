import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { TestRun } from '../types'

const TESTS_PANE = 'tests'
const BAR_CELLS = 16

const runs = atom({ plugin: 'work-pane', key: 'runs' } as const, [] as TestRun[])

const SHOWN_RUNS = 3
const TEE = /\|\s*tee\s+(?:-a\s+)?(['"]?)([^\s'"|;&]+)\1/
const UNIT = /\[(\d+)\/(\d+)\]/g

function teeLog(command: string): string | undefined {
  return TEE.exec(command.split("\n")[0])?.[2]
}

function parseLog(text: string): Pick<TestRun, 'done' | 'total' | 'pass' | 'fail'> {
  const units = [...text.matchAll(UNIT)]
  const last = units.at(-1)
  if (!last) return {}
  const line = text.slice(last.index).split('\n')[0]
  const pass = /pass (\d+)/.exec(line)?.[1]
  const fail = /fail (\d+)/.exec(line)?.[1]
  return {
    done: Number(last[1]),
    total: Number(last[2]),
    pass: pass === undefined ? undefined : Number(pass),
    fail: fail === undefined ? undefined : Number(fail),
  }
}

async function readRun($: Parameters<typeof read>[0], run: TestRun): Promise<TestRun> {
  try {
    const { stdout } = await $.process.run(['tail', '-n', '40', run.log], { timeoutMs: 2000 })
    return { ...run, ...parseLog(stdout) }
  } catch {
    return run
  }
}

export const register: Register = on => {
  let isInteractive = true

  on('session.start', async ($, e, next) => {
    isInteractive = e.isInteractive !== false
    if (!isInteractive) return next(e)
    await $.command.register({ name: 'tests', description: 'Open the Tests pane' })
    $.clock.every(1000, async () => {
      const runningRuns = (await read($, runs)).filter(r => r.endedAt === undefined)
      if (runningRuns.length === 0) return
      for (const run of runningRuns) {
        const read_ = await readRun($, run)
        const isComplete = read_.total !== undefined && read_.done === read_.total
        const next_ = isComplete ? { ...read_, endedAt: Date.now(), isFailed: (read_.fail ?? 0) > 0 } : read_
        await update($, runs, list => list.map(r => (r.id === run.id ? next_ : r)))
      }
      $.ui.invalidate('ui.render')
    })
    return next(e)
  })

  on('command.run', { command: 'tests' }, async $ => {
    await $.ui.open({ id: TESTS_PANE, title: 'Tests' })
    return { text: 'Tests pane opened.' }
  })

  on('tool.call', async ($, e, next) => {
    let args = e as unknown as Record<string, unknown>

    const log = isInteractive && e.tool === 'Bash' && typeof args.command === 'string' ? teeLog(args.command) : undefined
    if (log) {
      const command = args.command as string
      const run: TestRun = {
        id: e.tool_use_id ?? `${Date.now()}`,
        label: command.split('|')[0].trim().slice(0, 48),
        log,
      }
      await update($, runs, list => [...list, run].slice(-10))
      void $.ui.open({ id: TESTS_PANE, title: 'Tests' })
      const ran = await next(e)
      if (args.run_in_background !== true) {
        const final = await readRun($, run)
        const isFailed = ran.deny !== undefined || ran.isError === true || (final.fail ?? 0) > 0
        await update($, runs, list => list.map(r => (r.id === run.id ? { ...final, endedAt: Date.now(), isFailed } : r)))
      }
      return ran
    }

    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: TESTS_PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const testRows = (await read($, runs)).slice(-SHOWN_RUNS)
    if (testRows.length === 0) return <Text dimColor>No test runs yet</Text>

    return (
      <Box flexDirection="column">
        {testRows.map(r => {
          const mark = r.endedAt === undefined ? '●' : r.isFailed ? '✗' : '✓'
          const hasCount = r.total !== undefined && r.done !== undefined
          const cells = hasCount ? Math.round((r.done! / Math.max(1, r.total!)) * BAR_CELLS) : 0
          const counts = r.pass !== undefined ? ` · pass ${r.pass} fail ${r.fail ?? 0}` : ''
          const state = hasCount
            ? `${'█'.repeat(cells)}${'░'.repeat(BAR_CELLS - cells)} ${r.done}/${r.total}${counts}`
            : r.endedAt === undefined ? 'running' : 'finished'
          return (
            <Box flexDirection="column" marginBottom={1}>
              <Text dimColor={r.endedAt !== undefined}>{`${mark} ${r.label}`}</Text>
              <Text dimColor>{`  ${state}`}</Text>
            </Box>
          )
        })}
      </Box>
    )
  })
}
