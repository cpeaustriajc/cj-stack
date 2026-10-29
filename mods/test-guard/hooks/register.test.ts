import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

type World = {
  ran: unknown[]
  commands: string[]
  runs: { argv: string[]; cwd?: string }[]
  disk: Record<string, string>
  head: Record<string, string>
  repo: 'yes' | 'no' | 'unborn' | 'broken' | 'throws'
}

const A = '/repo/tests/a.test.ts'
const A_HEAD = [
  "import { notify } from '../src/notify'",
  '',
  "it('sends once', () => {",
  '  notify()',
  '  expect(send).toHaveBeenCalledTimes(1)',
  "  expect(send).toHaveBeenCalledWith('hi')",
  '})',
  '',
].join('\n')

function world(on: On, given: Partial<World> = {}): World {
  const w: World = { ran: [], commands: [], runs: [], disk: { [A]: A_HEAD }, head: { [A]: A_HEAD }, repo: 'yes', ...given }
  const isDir = (p: string) => p === '/repo' || Object.keys(w.disk).some(f => f.startsWith(`${p}/`))
  on('session.cwd', () => ({ value: '/repo' }) as never)
  on('fs.exists', (_$, e) => {
    const p = (e as { path: string }).path
    return { value: p in w.disk || isDir(p) } as never
  })
  on('fs.read', (_$, e) => {
    const p = (e as { path: string }).path
    if (!(p in w.disk)) throw new Error(`ENOENT: ${p}`)
    return { value: w.disk[p] } as never
  })
  on('process.run', (_$, e) => {
    const { argv, init } = e as { argv: string[]; init?: { cwd?: string } }
    w.runs.push({ argv, cwd: init?.cwd })
    const fail = (stderr: string) => ({ value: { exitCode: 128, stdout: '', stderr } }) as never
    if (w.repo === 'throws') throw new Error('git: not found')
    if (w.repo === 'no') return fail('fatal: not a git repository (or any of the parent directories): .git')
    if (w.repo === 'unborn') return fail("fatal: invalid object name 'HEAD'.")
    if (w.repo === 'broken') return fail('fatal: unable to read tree 1234abcd')
    const abs = `${init?.cwd}/${argv[argv.length - 1].replace(/^HEAD:\.\//, '')}`
    if (abs in w.head) return { value: { exitCode: 0, stdout: w.head[abs], stderr: '' } } as never
    return fail(`fatal: path '${abs.slice('/repo/'.length)}' does not exist in 'HEAD'`)
  })
  on('command.register', (_$, e) => (w.commands.push((e as { name: string }).name), { value: {} }) as never)
  on('session.start', (_$, e) => e as never)
  on('tool.call', (_$, e) => {
    w.ran.push(e)
    return { result: { ok: true } } as never
  })
  return w
}

const call = ($: any, input: Record<string, unknown>) => $.tool.call(input)
const edit = ($: any, file_path: string, old_string: string, new_string: string, replace_all?: boolean) =>
  call($, { tool: 'Edit', file_path, old_string, new_string, ...(replace_all ? { replace_all } : {}) })
const allow = ($: any, args: string) => $.command.run({ command: 'test-guard', args })

const passes = (r: { deny?: string }, w: World) => {
  expect(r.deny).toBeUndefined()
  expect(w.ran.length).toBe(1)
}
const denies = (r: { deny?: string }, w: World, line: string) => {
  expect(r.deny).toContain('test-guard:')
  expect(r.deny).toContain(line)
  expect(r.deny).toContain('/test-guard allow')
  expect(w.ran).toEqual([])
}

test('1. an Edit that adds a new it() block to a tracked test passes', async ($, on) => {
  const w = world(on)
  passes(await edit($, A, '})\n', "})\n\nit('sends nothing when muted', () => {\n  expect(send).not.toHaveBeenCalled()\n})\n"), w)
})

test('2. an Edit that weakens toHaveBeenCalledTimes(1) is denied and names the line', async ($, on) => {
  const w = world(on)
  const r = await edit($, A, 'toHaveBeenCalledTimes(1)', 'toHaveBeenCalled()')
  denies(r, w, 'expect(send).toHaveBeenCalledTimes(1)')
  expect(r.deny).toContain(A)
})

test('3. an Edit that removes an expect line is denied', async ($, on) => {
  const w = world(on)
  denies(await edit($, A, "  expect(send).toHaveBeenCalledWith('hi')\n", ''), w, "toHaveBeenCalledWith('hi')")
})

test('4. a Write that replaces a tracked test with fewer lines is denied', async ($, on) => {
  const w = world(on)
  const content = "it('sends once', () => {\n  notify()\n})\n"
  denies(await call($, { tool: 'Write', file_path: A, content }), w, "import { notify } from '../src/notify'")
})

test('5. a Write of a new untracked test file passes', async ($, on) => {
  const w = world(on)
  passes(await call($, { tool: 'Write', file_path: '/repo/src/foo.test.ts', content: "it('x', () => {})\n" }), w)
})

test('5b. a Write of a test file in a directory that does not exist yet passes', async ($, on) => {
  const w = world(on)
  passes(await call($, { tool: 'Write', file_path: '/repo/e2e/new/flow.spec.ts', content: 'x\n' }), w)
  expect(w.runs[0].cwd).toBe('/repo')
})

test('6. a MultiEdit whose second edit changes a HEAD line is denied', async ($, on) => {
  const w = world(on)
  const edits = [
    { old_string: '})\n', new_string: "})\n\nit('more', () => {})\n" },
    { old_string: 'toHaveBeenCalledTimes(1)', new_string: 'toHaveBeenCalled()' },
  ]
  denies(await call($, { tool: 'MultiEdit', file_path: A, edits }), w, 'toHaveBeenCalledTimes(1)')
})

test('6b. a MultiEdit that only adds passes', async ($, on) => {
  const w = world(on)
  const edits = [
    { old_string: '})\n', new_string: "})\n\nit('more', () => {})\n" },
    { old_string: "it('more', () => {})", new_string: "it('more', () => {\n  expect(1).toBe(1)\n})" },
  ]
  passes(await call($, { tool: 'MultiEdit', file_path: A, edits }), w)
})

test('7. an Edit to a file that is not a test passes and runs no git', async ($, on) => {
  const w = world(on, { disk: { '/repo/src/app.ts': 'a\n' }, head: { '/repo/src/app.ts': 'a\n' } })
  passes(await edit($, '/repo/src/app.ts', 'a', 'b'), w)
  expect(w.runs).toEqual([])
})

test('7b. each test file pattern is checked', async ($, on) => {
  const paths = [
    '/repo/src/a.spec.js', '/repo/pkg/test_util.py', '/repo/pkg/util_test.py', '/repo/cmd/main_test.go',
    '/repo/test/helper.ts', '/repo/src/__tests__/x.ts', '/repo/e2e/login.ts', '/repo/src/__snapshots__/x.snap',
  ]
  const files = Object.fromEntries(paths.map(p => [p, 'keep\n']))
  const w = world(on, { disk: files, head: files })
  for (const p of paths) expect((await edit($, p, 'keep', 'gone')).deny).toContain('test-guard:')
  expect(w.ran).toEqual([])
  for (const p of ['/repo/src/latest.ts', '/repo/src/contest/x.ts', '/repo/docs/testing.md']) {
    expect((await edit($, p, 'a', 'b')).deny).toBeUndefined()
  }
})

test('8. after /test-guard allow, a weakening Edit passes on that path only', async ($, on) => {
  const B = '/repo/tests/b.test.ts'
  const w = world(on, { disk: { [A]: A_HEAD, [B]: A_HEAD }, head: { [A]: A_HEAD, [B]: A_HEAD } })
  const out = await allow($, 'allow tests/a.test.ts')
  expect(out.text).toContain('tests/a.test.ts')
  expect((await edit($, A, 'toHaveBeenCalledTimes(1)', 'toHaveBeenCalled()')).deny).toBeUndefined()
  expect((await edit($, B, 'toHaveBeenCalledTimes(1)', 'toHaveBeenCalled()')).deny).toContain('test-guard:')
  expect(w.ran.length).toBe(1)
})

test('8b. /test-guard alone lists the allowed paths', async ($, on) => {
  world(on)
  expect((await allow($, '')).text).toContain('No path')
  await allow($, 'allow tests/a.test.ts')
  expect((await allow($, '')).text).toContain(A)
})

test('8c. /test-guard with an unknown argument names the usage and allows nothing', async ($, on) => {
  const w = world(on)
  expect((await allow($, 'tests/a.test.ts')).text).toContain('/test-guard allow <path>')
  denies(await edit($, A, 'toHaveBeenCalledTimes(1)', 'toHaveBeenCalled()'), w, 'toHaveBeenCalledTimes(1)')
})

test('8d. the session registers the /test-guard command', async ($, on) => {
  const w = world(on)
  await ($ as any).session.start({ cwd: '/repo', isInteractive: false })
  expect(w.commands).toEqual(['test-guard'])
})

test('9. a test file outside a git repo passes', async ($, on) => {
  const w = world(on, { repo: 'no' })
  passes(await edit($, A, 'toHaveBeenCalledTimes(1)', 'toHaveBeenCalled()'), w)
})

test('9b. a repo with no commit yet passes', async ($, on) => {
  const w = world(on, { repo: 'unborn' })
  passes(await edit($, A, 'toHaveBeenCalledTimes(1)', 'toHaveBeenCalled()'), w)
})

test('9c. git show failing for another reason is denied with could not check', async ($, on) => {
  const w = world(on, { repo: 'broken' })
  const r = await edit($, A, 'toHaveBeenCalledTimes(1)', 'toHaveBeenCalled()')
  expect(r.deny).toContain('test-guard: could not check')
  expect(w.ran).toEqual([])
})

test('9d. a git probe that throws is denied with could not check', async ($, on) => {
  const w = world(on, { repo: 'throws' })
  expect((await edit($, A, '})\n', '})\n// more\n')).deny).toContain('test-guard: could not check')
  expect(w.ran).toEqual([])
})

test('9e. HEAD is read with a path relative to the file directory', async ($, on) => {
  const w = world(on)
  await edit($, A, '})\n', '})\n\n')
  expect(w.runs).toEqual([{ argv: ['git', 'show', 'HEAD:./a.test.ts'], cwd: '/repo/tests' }])
})

test('10. a line added this session, not in HEAD, can change', async ($, on) => {
  const now = `${A_HEAD}it('new', () => {\n  expect(a).toBe(1)\n})\n`
  const w = world(on, { disk: { [A]: now } })
  passes(await edit($, A, 'expect(a).toBe(1)', 'expect(a).toBeTruthy()'), w)
})

test('a replace_all Edit is checked on every match', async ($, on) => {
  const text = `// toHaveBeenCalledTimes(1) is strict\n${A_HEAD}`
  const w = world(on, { disk: { [A]: text } })
  denies(await edit($, A, 'toHaveBeenCalledTimes(1)', 'toHaveBeenCalled()', true), w, 'toHaveBeenCalledTimes(1)')
})

test('removing a blank HEAD line passes', async ($, on) => {
  const w = world(on)
  passes(await call($, { tool: 'Write', file_path: A, content: A_HEAD.replace(/\n\n/g, '\n') }), w)
})

test('a relative path resolves against the session cwd', async ($, on) => {
  const w = world(on)
  denies(await edit($, 'tests/a.test.ts', 'toHaveBeenCalledTimes(1)', 'toHaveBeenCalled()'), w, 'toHaveBeenCalledTimes(1)')
})

test('a tool other than Edit, MultiEdit or Write is left alone', async ($, on) => {
  const w = world(on)
  passes(await call($, { tool: 'Bash', command: "sed -i 's/Times(1)/()/' tests/a.test.ts" }), w)
  expect(w.runs).toEqual([])
})

test('an Edit whose old_string is not in the file passes to the tool', async ($, on) => {
  const w = world(on)
  passes(await edit($, A, 'not there', 'x'), w)
})

test('a hook body that throws gives a deny', async ($, on) => {
  const w = world(on)
  const r = await call($, { tool: 'Edit', file_path: A, old_string: null, new_string: 'x' })
  expect(r.deny).toContain('test-guard: could not check')
  expect(w.ran).toEqual([])
})
