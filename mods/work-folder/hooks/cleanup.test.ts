import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

const REPO = '/home/cj/app'
const WORK = `${REPO}/.claude/work`
const DAY = 86_400_000
const NOW = 1000 * DAY

type Node = { mtimeMs: number; children?: Record<string, Node> }

function world(on: On, opts: { work?: Record<string, Node>; config?: string; repo?: boolean; exitCode?: number } = {}) {
  const tree: Record<string, Node> = {}
  if (opts.repo !== false) tree[`${REPO}/.git`] = { mtimeMs: 0, children: {} }
  if (opts.work) tree[WORK] = { mtimeMs: NOW, children: opts.work }
  const find = (path: string): Node | undefined => {
    if (path in tree) return tree[path]
    const parent = path.slice(0, path.lastIndexOf('/'))
    const node = parent ? find(parent) : undefined
    return node?.children?.[path.slice(parent.length + 1)]
  }
  const runs: { argv: string[]; cwd?: string }[] = []
  const toasts: string[] = []
  const listed: string[] = []
  on('session.start', (_$, e) => e as never)
  on('clock.now', () => ({ value: NOW }) as never)
  on('fs.exists', (_$, e) => {
    const path = (e as { path: string }).path
    return { value: find(path) !== undefined || (path === `${REPO}/.claude/work-folder.json` && opts.config !== undefined) } as never
  })
  on('fs.read', (_$, e) => {
    if (opts.config === undefined) throw new Error('ENOENT')
    return { value: opts.config } as never
  })
  on('fs.stat', (_$, e) => {
    const node = find((e as { path: string }).path)
    if (!node) throw new Error('ENOENT')
    return { value: { kind: node.children ? 'dir' : 'file', size: 0, mtimeMs: node.mtimeMs, isLink: false } } as never
  })
  on('fs.list', (_$, e) => {
    const path = (e as { path: string }).path
    listed.push(path)
    const node = find(path)
    if (!node?.children) throw new Error('ENOTDIR')
    return {
      value: Object.entries(node.children).map(([name, n]) => ({
        name,
        kind: n.children ? 'dir' : 'file',
        size: 0,
        mtimeMs: n.children ? 0 : n.mtimeMs,
        isLink: false,
      })),
    } as never
  })
  on('process.run', (_$, e) => {
    const x = e as { argv: string[]; init?: { cwd?: string } }
    runs.push({ argv: [...x.argv], cwd: x.init?.cwd })
    return { value: { exitCode: opts.exitCode ?? 0, stdout: '', stderr: opts.exitCode ? 'fatal: boom' : '' } } as never
  })
  on('ui.toast', (_$, e) => (toasts.push((e as { text: string }).text), { value: undefined }) as never)
  return { runs, toasts, listed }
}

const file = (days: number): Node => ({ mtimeMs: NOW - days * DAY })
const dir = (days: number, children: Record<string, Node> = {}): Node => ({ mtimeMs: NOW - days * DAY, children })
const start = ($: any, cwd = REPO) => $.session.start({ cwd, isInteractive: true, surface: 'terminal' })
const cleaned = (runs: { argv: string[] }[]) => runs.flatMap(r => r.argv.slice(r.argv.indexOf('--') + 1))

test('a topic with no file newer than a day is cleaned with git, from the repo root', async ($, on) => {
  const w = world(on, { work: { 'm4-probe': dir(20, { 'a.log': file(20), sub: dir(20, { 'b.png': file(16) }) }) } })
  await start($)
  expect(w.runs).toEqual([{ argv: ['git', 'clean', '-ffdX', '--', '.claude/work/m4-probe'], cwd: REPO }])
})

test('one recent file deep in a topic keeps the whole topic', async ($, on) => {
  const w = world(on, { work: { live: dir(30, { a: file(30), sub: dir(30, { deep: dir(30, { 'b.md': file(0.5) }) }) }) } })
  await start($)
  expect(w.runs).toEqual([])
})

test('loose files are judged one by one, and an empty folder by its own time', async ($, on) => {
  const w = world(on, {
    work: { 'old.log': file(15), 'new.log': file(0.5), 'empty-old': dir(40), 'empty-new': dir(0.5), '.DS_Store': file(100) },
  })
  await start($)
  expect(cleaned(w.runs).sort()).toEqual(['.claude/work/.DS_Store', '.claude/work/empty-old', '.claude/work/old.log'])
})

test('the toast names what was cleaned, and nothing cleaned means no toast', async ($, on) => {
  const w = world(on, { work: { a: dir(20, { x: file(20) }), b: dir(0.5, { x: file(0.5) }) } })
  await start($)
  expect(w.toasts).toEqual(['work-folder: cleaned 1 entry in .claude/work not changed for 1 day: a'])
})

test('nothing stale leaves git alone and shows no toast', async ($, on) => {
  const w = world(on, { work: { b: dir(0.5, { x: file(0.5) }) } })
  await start($)
  expect(w.runs).toEqual([])
  expect(w.toasts).toEqual([])
})

test('a file 23 hours old keeps its entry, one 25 hours old does not', async ($, on) => {
  const w = world(on, { work: { young: dir(2, { x: file(23 / 24) }), old: dir(2, { x: file(25 / 24) }) } })
  await start($)
  expect(cleaned(w.runs)).toEqual(['.claude/work/old'])
})

test('keepDays in work-folder.json sets the age', async ($, on) => {
  const w = world(on, { work: { a: dir(5, { x: file(5) }), b: dir(2, { x: file(2) }) }, config: '{ "keepDays": 3 }' })
  await start($)
  expect(cleaned(w.runs)).toEqual(['.claude/work/a'])
  expect(w.toasts).toEqual(['work-folder: cleaned 1 entry in .claude/work not changed for 3 days: a'])
})

test('keepDays 0 turns the cleanup off', async ($, on) => {
  const w = world(on, { work: { a: dir(500, { x: file(500) }) }, config: '{ "keepDays": 0 }' })
  await start($)
  expect(w.runs).toEqual([])
  expect(w.listed).toEqual([])
})

test('a keepDays that is not a non-negative number cleans nothing and says how to fix it', async ($, on) => {
  const w = world(on, { work: { a: dir(500, { x: file(500) }) }, config: '{ "keepDays": "14" }' })
  await start($)
  expect(w.runs).toEqual([])
  expect(w.toasts[0]).toContain(`work-folder: ${REPO}/.claude/work-folder.json is not valid ("keepDays" is not a number of days, 0 or more)`)
})

test('a malformed work-folder.json cleans nothing and says so', async ($, on) => {
  const w = world(on, { work: { a: dir(500, { x: file(500) }) }, config: '{ "keepDays": ' })
  await start($)
  expect(w.runs).toEqual([])
  expect(w.toasts[0]).toContain('work-folder.json is not valid')
})

test('a session in a subfolder cleans the repo root work folder', async ($, on) => {
  const w = world(on, { work: { a: dir(20, { x: file(20) }) } })
  await start($, `${REPO}/apps/web`)
  expect(w.runs).toEqual([{ argv: ['git', 'clean', '-ffdX', '--', '.claude/work/a'], cwd: REPO }])
})

test('a session outside any git repo runs nothing', async ($, on) => {
  const w = world(on, { repo: false, work: { a: dir(20, { x: file(20) }) } })
  await start($)
  expect(w.runs).toEqual([])
})

test('a repo with no work folder runs nothing', async ($, on) => {
  const w = world(on)
  await start($)
  expect(w.runs).toEqual([])
  expect(w.listed).toEqual([])
})

test('a failed git clean still starts the session and claims no cleanup', async ($, on) => {
  const w = world(on, { work: { a: dir(20, { x: file(20) }) }, exitCode: 128 })
  expect(await start($)).toEqual({ cwd: REPO, isInteractive: true, surface: 'terminal' })
  expect(w.runs.length).toBe(1)
  expect(w.toasts).toEqual([])
})
