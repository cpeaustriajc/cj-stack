import { atom, read, update } from 'claude-code'
import type { Hook, Register } from 'claude-code'

type Api = Parameters<Hook<'tool.call'>>[0]
type Change = { old_string: string; new_string: string; replace_all?: boolean }

const MOD = 'test-guard'
const TOOLS = new Set(['Edit', 'MultiEdit', 'Write'])
const TEST_NAME = [/\.(test|spec)\.[^/]+$/, /(^|\/)test_[^/]*\.py$/, /_test\.(py|go)$/]
const TEST_DIR = new Set(['test', 'tests', '__tests__', 'e2e', '__snapshots__'])
const NO_BASELINE = [/not a git repository/, /invalid object name '?HEAD'?/, /does not exist in '?HEAD'?/, /exists on disk, but not in '?HEAD'?/]
const USAGE = 'Use /test-guard allow <path> to let Claude change the lines that path has at HEAD, or /test-guard to list allowed paths.'

const allowed = atom({ plugin: 'test-guard', key: 'allowed' } as const, [] as string[])

const deny = (path: string, line: string) =>
  `${MOD}: this changes or removes a line that ${path} has at HEAD: \`${line.trim()}\`. ` +
  'Add a new test instead. If the old test is wrong, tell the user which test, the old line and why; ' +
  `the user can run \`/test-guard allow ${path}\`.`

function isTest(path: string): boolean {
  const p = path.replace(/\\/g, '/')
  return TEST_NAME.some(re => re.test(p)) || p.split('/').slice(0, -1).some(s => TEST_DIR.has(s))
}

function absolute(path: string, cwd: string): string {
  const parts: string[] = []
  for (const s of (path.startsWith('/') ? path : `${cwd}/${path}`).split('/')) {
    if (s === '..') parts.pop()
    else if (s && s !== '.') parts.push(s)
  }
  return `/${parts.join('/')}`
}

function apply(text: string, c: Change): string {
  if (typeof c.old_string !== 'string' || typeof c.new_string !== 'string') throw new Error('edit without old_string or new_string')
  return c.replace_all ? text.split(c.old_string).join(c.new_string) : text.replace(c.old_string, () => c.new_string)
}

async function after($: Api, e: Record<string, unknown>, path: string): Promise<string> {
  if (e.tool === 'Write') return String(e.content)
  const changes = e.tool === 'MultiEdit' ? (e.edits as Change[]) : [e as unknown as Change]
  return changes.reduce(apply, String(await $.fs.read(path)))
}

function firstLost(head: string, next: string): string | undefined {
  const lines = next.split(/\r?\n/)
  let at = 0
  for (const line of head.split(/\r?\n/)) {
    if (!line.trim()) continue
    while (at < lines.length && lines[at] !== line) at++
    if (at === lines.length) return line
    at++
  }
  return undefined
}

async function headText($: Api, path: string): Promise<string | undefined> {
  let dir = path.slice(0, path.lastIndexOf('/')) || '/'
  while (dir !== '/' && !(await $.fs.exists(dir))) dir = dir.slice(0, dir.lastIndexOf('/')) || '/'
  const rel = path.slice(dir === '/' ? 1 : dir.length + 1)
  const r = await $.process.run(['git', 'show', `HEAD:./${rel}`], { cwd: dir })
  if (r.exitCode === 0) return r.stdout
  if (NO_BASELINE.some(re => re.test(r.stderr))) return undefined
  throw new Error(`git show exited ${r.exitCode}: ${r.stderr.trim()}`)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await $.command.register({
      name: 'test-guard',
      description: 'Let Claude change the HEAD lines of one test file, or list the allowed files',
      argumentHint: 'allow <path>',
    })
    return result
  })

  on('command.run', { command: 'test-guard' }, async ($, e) => {
    const [verb, ...rest] = e.args.trim().split(/\s+/)
    if (!verb) {
      const paths = await read($, allowed)
      return { text: paths.length ? `Allowed: ${paths.join(', ')}` : `No path is allowed. ${USAGE}` }
    }
    if (verb !== 'allow' || !rest.length) return { text: USAGE }
    const path = absolute(rest.join(' '), await $.session.cwd())
    await update($, allowed, paths => (paths.includes(path) ? paths : [...paths, path]))
    return { text: `Claude can now change the HEAD lines of ${path} for the rest of this session.` }
  })

  on('tool.call', async ($, e, next) => {
    if (!TOOLS.has(e.tool)) return next(e)
    const input = e as unknown as Record<string, unknown>
    if (typeof input.file_path !== 'string' || !isTest(input.file_path)) return next(e)
    const path = absolute(input.file_path, await $.session.cwd())
    if ((await read($, allowed)).includes(path)) return next(e)
    const head = await headText($, path)
    if (head === undefined) return next(e)
    const lost = firstLost(head, await after($, input, path))
    return lost === undefined ? next(e) : { deny: deny(path, lost) }
  }).catch(($, e, next) =>
    next.called
      ? next(e)
      : { deny: `${MOD}: could not check this edit (${next.error.message}). Retry, or ask the user to run /test-guard allow <path>.` },
  )
}
