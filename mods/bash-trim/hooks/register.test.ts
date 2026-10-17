import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

function world(on: On, answer: Record<string, unknown>) {
  on('tool.call', () => answer as never)
}

const ok = (stdout: string) => ({ result: { stdout, stderr: '', interrupted: false } })
const bash = ($: any, command: string) => $.tool.call({ tool: 'Bash', command })
const lines = (n: number, width = 59) => Array.from({ length: n }, (_, i) => `line ${i} `.padEnd(width, '.')).join('\n')

const TEST_RUN = `${lines(300)}\n26 passed, 0 failed`

test('an 18,000-character test output keeps its head, a cut line and its last line', async ($, on) => {
  const out = TEST_RUN.slice(-18_000)
  world(on, ok(out))
  const r = await bash($, 'npm test')
  const got: string = r.result.stdout
  expect(got.startsWith(out.slice(0, 2_000))).toBe(true)
  expect(got).toMatch(/\[… [\d,]+ lines, 13,000 characters cut …\]/)
  expect(got.endsWith('26 passed, 0 failed')).toBe(true)
  expect(got.length).toBeLessThan(5_100)
})

test('the cut line counts the cut lines', async ($, on) => {
  world(on, ok('a\n'.repeat(10_000)))
  const r = await bash($, 'yes a | head -10000 | cat -n | sort')
  expect(r.result.stdout).toContain('[… 7,500 lines, 15,000 characters cut …]')
})

for (const command of [
  'gh pr diff 17',
  'cd repo && git diff',
  'cd a && cd b && cat big.log',
  "sed -n '1,400p' big.ts",
  'head -500 big.log',
  'tail -n 400 big.log',
  'jq . big.json',
  'git show HEAD',
  'git log -p -5',
  'gh api repos/o/r/pulls',
  'gh issue view 6 --comments',
]) {
  test(`${JSON.stringify(command)} passes whole`, async ($, on) => {
    const out = lines(240)
    world(on, ok(out))
    expect((await bash($, command)).result.stdout).toBe(out)
  })
}

test('a failed command passes whole', async ($, on) => {
  const text = lines(300)
  world(on, { isError: true, result: text, text })
  const r = await bash($, 'npm test')
  expect(r.isError).toBe(true)
  expect(r.text).toBe(text)
})

test('a 9,000-character output passes whole', async ($, on) => {
  const out = 'x'.repeat(9_000)
  world(on, ok(out))
  expect((await bash($, 'npm test')).result.stdout).toBe(out)
})

test('an output the harness saved to a file passes whole', async ($, on) => {
  const out = 'x'.repeat(20_000)
  world(on, { result: { stdout: out, stderr: '', interrupted: false, persistedOutputPath: '/tmp/o.txt' } })
  expect((await bash($, 'npm test')).result.stdout).toBe(out)
})

for (const extra of [{ interrupted: true }, { isImage: true }, { backgroundTaskId: 'b1' }]) {
  test(`a result with ${Object.keys(extra)[0]} passes whole`, async ($, on) => {
    const out = 'x'.repeat(20_000)
    world(on, { result: { stdout: out, stderr: '', interrupted: false, ...extra } })
    expect((await bash($, 'npm test')).result.stdout).toBe(out)
  })
}

test('git log without -p is trimmed', async ($, on) => {
  world(on, ok(lines(300)))
  expect((await bash($, 'git log --oneline')).result.stdout).toContain('characters cut')
})

test('a broken result passes as it came and is reported', async ($, on) => {
  world(on, { result: { stdout: 42, stderr: '', interrupted: false } })
  const r = await bash($, 'npm test')
  expect(r.result.stdout).toBe(42)
})
