import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

function world(on: On) {
  const ran: string[] = []
  on('tool.call', (_$, e) => {
    ran.push((e as { command?: string }).command ?? '')
    return { result: { ok: true } } as never
  })
  return { ran }
}

const bash = ($: any, command: unknown) => $.tool.call({ tool: 'Bash', command })

const DENY = [
  'pkill -f "node \\(vitest"',
  'pkill -f "wrangler dev" ; pkill -f workerd ; sleep 2',
  'kill $(lsof -tiTCP:8787 -sTCP:LISTEN) $(lsof -tiTCP:5173 -sTCP:LISTEN) 2>/dev/null',
  'lsof -ti tcp:3100 | xargs kill 2>/dev/null; sleep 1',
  'lsof -ti:3111 | xargs -r kill',
  'kill $(pgrep -f vite)',
  'killall node',
  'fuser -k 3000/tcp',
  'cd /some/worktree && npx tsc --noEmit && kill $(lsof -ti tcp:4180)',
  'kill "$(lsof -ti:3000)"',
  'kill -9 `lsof -ti:3000`',
  'kill -9 $(pidof node)',
  'ps aux | grep vite | awk \'{print $2}\' | xargs kill -9',
  'pgrep -f vite | xargs -n 1 kill',
  'sudo pkill -f vite',
  '/usr/bin/pkill vite',
  'FOO=1 env pkill vite',
  'echo start && (pkill vite)',
  'echo $(pkill vite)',
  'if pkill vite; then echo done; fi',
  'while true; do\n  pkill vite\ndone',
  'true || killall -9 node',
  '{ pkill vite; }',
  'xargs -I {} pkill {}',
]

const ALLOW = [
  'kill 27716; sleep 2; lsof -iTCP:3138 -sTCP:LISTEN -nP | tail -n +2',
  'lsof -a -p 18427 -d cwd | tail -1; kill 18427 && echo stopped',
  'kill $!',
  'kill %1',
  'kill $(cat .claude/work/app.pid) 2>/dev/null',
  'kill -0 22106',
  'while kill -0 22106 2>/dev/null; do sleep 10; done',
  'pgrep -fl vitest',
  'grep -n pkill README.md',
  'echo "do not use pkill"',
  "echo 'killall node' > notes.txt",
  'echo pkill # pkill vite',
  'cat app.pid | xargs kill',
  'fuser 3000/tcp',
  'lsof -ti:3000',
  'ps -o command= -p 123',
  'git commit -m "stop using pkill"',
  'npm run pkill-all',
  'ls',
]

for (const command of DENY) {
  test(`${JSON.stringify(command)} is denied`, async ($, on) => {
    const w = world(on)
    const r = await bash($, command)
    expect(r.deny).toContain('kill-guard:')
    expect(r.deny).toContain("another checkout's")
    expect(w.ran).toEqual([])
  })
}

for (const command of ALLOW) {
  test(`${JSON.stringify(command)} passes`, async ($, on) => {
    const w = world(on)
    expect((await bash($, command)).deny).toBeUndefined()
    expect(w.ran).toEqual([command])
  })
}

test('the deny text names both ways out', async ($, on) => {
  world(on)
  const r = await bash($, 'pkill -f vite')
  expect(r.deny).toContain('$!')
  expect(r.deny).toContain('pid file')
  expect(r.deny).toContain('lsof -a -p <pid> -d cwd')
  expect(r.deny).toContain('ps -o command= -p <pid>')
})

test('a tool other than Bash is left alone', async ($, on) => {
  world(on)
  const r = await ($ as any).tool.call({ tool: 'Read', file_path: '/tmp/pkill -f vite' })
  expect(r.deny).toBeUndefined()
})

test('a hook body that throws gives a deny', async ($, on) => {
  const w = world(on)
  const r = await bash($, null)
  expect(r.deny).toContain('kill-guard: could not check')
  expect(w.ran).toEqual([])
})
