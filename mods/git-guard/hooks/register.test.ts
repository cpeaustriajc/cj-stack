import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

type World = { ran: string[]; runs: { argv: string[]; cwd?: string }[]; dirty: string; branch: string; failRun: boolean; statusCode: number }

function world(on: On, given: Partial<World> = {}): World {
  const w: World = { ran: [], runs: [], dirty: ' M src/app.ts\n', branch: 'feature/x', failRun: false, statusCode: 0, ...given }
  on('session.cwd', () => ({ value: '/repo' }) as never)
  on('process.run', (_$, e) => {
    const { argv, init } = e as { argv: string[]; init?: { cwd?: string } }
    w.runs.push({ argv, cwd: init?.cwd })
    if (w.failRun) throw new Error('git: not found')
    if (argv.includes('status')) return { value: { exitCode: w.statusCode, stdout: w.dirty, stderr: '' } } as never
    if (argv.includes('symbolic-ref')) return { value: { exitCode: w.branch ? 0 : 128, stdout: `${w.branch}\n`, stderr: '' } } as never
    return { value: { exitCode: 1, stdout: '', stderr: '' } } as never
  })
  on('tool.call', (_$, e) => {
    w.ran.push((e as { command?: string }).command ?? '')
    return { result: { ok: true } } as never
  })
  return w
}

const bash = ($: any, command: unknown) => $.tool.call({ tool: 'Bash', command })

const DENY_BRANCH = [
  'git branch -D feature/x',
  'git branch -D a b',
  'git branch -Dq old',
  'git branch --delete --force old',
  'git branch -d -f old',
  'git branch --delete -f old',
  'git -C ../other branch -D old',
  'git fetch && git branch -D old',
  'echo $(git branch -D old)',
  'cd app; git branch -D old',
]

const DENY_PUSH_MAIN = [
  'git push --force origin main',
  'git push -f origin master',
  'git push origin main --force',
  'git push --force-with-lease origin main',
  'git push --force-with-lease=main:abc123 origin main',
  'git push -fu origin main',
  'git push origin +main',
  'git push origin +HEAD:main',
  'git push -f origin HEAD:refs/heads/main',
  'git push --force origin feature:master',
  'git -c push.default=current push -f origin main',
  'git --no-pager push -f origin main',
  'sudo git push -f origin main',
]

const DENY_DISCARD = [
  'git checkout -- .',
  'git checkout .',
  'git checkout HEAD -- .',
  'git checkout main -- .',
  'git restore .',
  'git restore -- .',
  'git restore --worktree .',
  'git restore -W -S .',
  'git restore --source=HEAD~2 .',
  'git restore :/',
  'git add -p && git checkout -- .',
]

const ALLOW = [
  'git reset --soft HEAD~1',
  'git reset HEAD~1',
  'git reset --mixed HEAD',
  'git branch -d feature/x',
  'git branch --delete feature/x',
  'git branch -m old new',
  'git branch -f topic HEAD',
  'git branch',
  'git push',
  'git push origin main',
  'git push -u origin feature/x',
  'git push --force origin feature/x',
  'git push -f origin HEAD:feature/x',
  'git push --force-with-lease origin claude/fix-main-page',
  'git push --force origin maintenance',
  'git push origin +feature/x',
  'git checkout main',
  'git checkout -b fix/x',
  'git checkout -- src/app.ts',
  'git checkout feature -- src/app.ts',
  'git restore src/app.ts',
  'git restore --staged .',
  'git restore -S .',
  'git clean -n',
  'git stash push -u -m wip',
  'git log --oneline -5',
  'echo "git branch -D old"',
  "echo 'git push -f origin main' > notes.txt",
  'echo ok # git branch -D old',
  'grep -n "git checkout -- ." README.md',
  'git commit -m "git push -f origin main"',
  'ls',
]

// Claude Code owns these (tests/claude-owned/actions.json A25, A26): the auto-mode classifier decides.
const OWNED = ['git reset --hard HEAD~1', 'git reset --hard', 'git clean -fd', 'git clean -f']

const runDeny = (list: string[], words: string[], given: Partial<World> = {}) => {
  for (const command of list) {
    test(`${JSON.stringify(command)} is denied`, async ($, on) => {
      const w = world(on, given)
      const r = await bash($, command)
      expect(r.deny).toContain('git-guard:')
      for (const word of words) expect(r.deny).toContain(word)
      expect(w.ran).toEqual([])
    })
  }
}

runDeny(DENY_BRANCH, ['git branch -d'])
runDeny(DENY_PUSH_MAIN, ['pull request', 'git revert'])
runDeny(DENY_DISCARD, ['git stash push -u'])

for (const command of [...ALLOW, ...OWNED]) {
  test(`${JSON.stringify(command)} passes`, async ($, on) => {
    const w = world(on)
    expect((await bash($, command)).deny).toBeUndefined()
    expect(w.ran).toEqual([command])
  })
}

test('a force push with no branch named is denied on main', async ($, on) => {
  const w = world(on, { branch: 'main' })
  for (const command of ['git push --force', 'git push -f origin', 'git push --force-with-lease']) {
    expect((await bash($, command)).deny).toContain('git-guard:')
  }
  expect(w.ran).toEqual([])
})

test('a force push with no branch named passes on a feature branch', async ($, on) => {
  const w = world(on, { branch: 'feature/x' })
  expect((await bash($, 'git push --force-with-lease')).deny).toBeUndefined()
  expect(w.ran).toEqual(['git push --force-with-lease'])
})

test('a force push with no branch named passes on a detached HEAD', async ($, on) => {
  const w = world(on, { branch: '' })
  expect((await bash($, 'git push -f origin')).deny).toBeUndefined()
  expect(w.ran).toEqual(['git push -f origin'])
})

test('checkout -- . and restore . pass on a clean tree', async ($, on) => {
  const w = world(on, { dirty: '' })
  for (const command of ['git checkout -- .', 'git restore .']) {
    expect((await bash($, command)).deny).toBeUndefined()
  }
  expect(w.ran).toEqual(['git checkout -- .', 'git restore .'])
})

test('the dirty check reads tracked files in the session cwd', async ($, on) => {
  const w = world(on)
  await bash($, 'git restore .')
  expect(w.runs).toEqual([{ argv: ['git', 'status', '--porcelain', '--untracked-files=no'], cwd: '/repo' }])
})

test('the dirty check follows -C and a plain cd', async ($, on) => {
  const w = world(on)
  await bash($, 'git -C ../other restore .')
  await bash($, 'cd sub && git checkout -- .')
  await bash($, 'cd /abs/repo; git restore .')
  expect(w.runs.map(r => r.cwd)).toEqual(['/repo/../other', '/repo/sub', '/abs/repo'])
})

test('a quoted cd target counts as a dirty tree', async ($, on) => {
  const w = world(on, { dirty: '' })
  expect((await bash($, 'cd "my repo" && git restore .')).deny).toContain('git-guard:')
  expect(w.runs).toEqual([])
})

test('a quoted cd target before a branchless force push is denied', async ($, on) => {
  const w = world(on, { branch: 'feature/x' })
  expect((await bash($, 'cd "my repo" && git push -f')).deny).toContain('git-guard:')
  expect(w.runs).toEqual([])
})

test('a git status that exits non-zero gives a deny', async ($, on) => {
  const w = world(on, { dirty: '', statusCode: 128 })
  const r = await bash($, 'git restore .')
  expect(r.deny).toContain('git-guard: could not check')
  expect(w.ran).toEqual([])
})

test('the current branch is read in the session cwd', async ($, on) => {
  const w = world(on, { branch: 'main' })
  await bash($, 'git push -f')
  expect(w.runs).toEqual([{ argv: ['git', 'symbolic-ref', '--short', '-q', 'HEAD'], cwd: '/repo' }])
})

test('a command with no destructive git runs no git probe', async ($, on) => {
  const w = world(on)
  await bash($, 'git status && git push origin main && git checkout -- src/app.ts')
  expect(w.runs).toEqual([])
})

test('a tool other than Bash is left alone', async ($, on) => {
  world(on)
  const r = await ($ as any).tool.call({ tool: 'Read', file_path: '/tmp/git branch -D old' })
  expect(r.deny).toBeUndefined()
})

test('a git probe that fails gives a deny', async ($, on) => {
  const w = world(on, { failRun: true })
  const r = await bash($, 'git restore .')
  expect(r.deny).toContain('git-guard: could not check')
  expect(w.ran).toEqual([])
})

test('a hook body that throws gives a deny', async ($, on) => {
  const w = world(on)
  const r = await bash($, null)
  expect(r.deny).toContain('git-guard: could not check')
  expect(w.ran).toEqual([])
})
