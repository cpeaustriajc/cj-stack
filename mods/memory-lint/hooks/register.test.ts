import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

const DIR = '/home/cj/.claude/projects/-home-cj-app/memory'

function world(on: On) {
  const ran: string[] = []
  on('env.get', (_$, e) => ({ value: (e as { name: string }).name === 'HOME' ? '/home/cj' : undefined }) as never)
  on('tool.call', (_$, e) => {
    ran.push((e as { file_path: string }).file_path)
    return { result: { ok: true } } as never
  })
  return ran
}

const write = ($: any, file_path: string, content: string) => $.tool.call({ tool: 'Write', file_path, content })
const edit = ($: any, file_path: string, old_string: string, new_string: string) =>
  $.tool.call({ tool: 'Edit', file_path, old_string, new_string })

test('a durable preference is saved', async ($, on) => {
  const ran = world(on)
  const r = await write($, `${DIR}/feedback_pnpm.md`, '---\nname: pnpm\nmodified: 2026-10-11T09:00:00Z\n---\nUse pnpm, never npm: the lockfile is pnpm-lock.yaml.')
  expect(r.deny).toBeUndefined()
  expect(ran).toEqual([`${DIR}/feedback_pnpm.md`])
})

test('task state is denied with the bar it missed', async ($, on) => {
  const ran = world(on)
  const r = await write($, `${DIR}/project_auth.md`, 'Currently migrating auth to OAuth; next step is the callback route.')
  expect(r.deny).toContain('task state')
  expect(r.deny).toContain('restate it without the flagged parts')
  expect(ran).toEqual([])
})

test('PR numbers, commit hashes and claude/ branches are one-off references', async ($, on) => {
  world(on)
  for (const text of ['Fixed in PR #412.', 'Regression came from a1b2c3d.', 'Work lives on claude/doctor-prompt-audit.', 'See #88 for context.']) {
    const r = await write($, `${DIR}/x.md`, text)
    expect(r.deny).toContain('one-off reference')
  }
})

test('file:line pointers and code blocks are repo detail', async ($, on) => {
  world(on)
  expect((await write($, `${DIR}/x.md`, 'The retry lives in src/api/client.ts:42.')).deny).toContain('repo detail')
  expect((await write($, `${DIR}/x.md`, 'Retry like this:\n```ts\nretry(3)\n```')).deny).toContain('repo detail')
})

test('a long topic file is denied', async ($, on) => {
  world(on)
  const r = await write($, `${DIR}/x.md`, 'The user prefers small commits. '.repeat(50))
  expect(r.deny).toContain('topic file over')
})

test('a long MEMORY.md line is denied, a short one passes', async ($, on) => {
  world(on)
  expect((await edit($, `${DIR}/MEMORY.md`, '- [pnpm](feedback_pnpm.md)', `- [pnpm](feedback_pnpm.md)\n- [style](s.md): ${'x'.repeat(220)}`)).deny).toContain('index line')
  expect((await edit($, `${DIR}/MEMORY.md`, '- [pnpm](feedback_pnpm.md)', '- [pnpm](feedback_pnpm.md)\n- [style](s.md): small commits')).deny).toBeUndefined()
})

test('an Edit is judged only by the lines it adds, so pruning always passes', async ($, on) => {
  const ran = world(on)
  const old = '- Currently on PR #12\n- Use pnpm'
  expect((await edit($, `${DIR}/MEMORY.md`, old, '- Use pnpm')).deny).toBeUndefined()
  expect((await edit($, `${DIR}/MEMORY.md`, old, `${old}\n- Use tabs`)).deny).toBeUndefined()
  expect(ran.length).toBe(2)
})

test('the frontmatter timestamp is not mistaken for anything', async ($, on) => {
  world(on)
  const r = await write($, `${DIR}/x.md`, '---\nname: tabs\ndescription: indentation\nmodified: 2026-10-11T09:00:00.000Z\n---\nIndent with tabs.')
  expect(r.deny).toBeUndefined()
})

test('files outside the memory directory are left alone', async ($, on) => {
  const ran = world(on)
  expect((await write($, '/home/cj/app/NOTES.md', 'Currently working on PR #9')).deny).toBeUndefined()
  expect((await write($, `${DIR}/notes.txt`, 'Currently working on PR #9')).deny).toBeUndefined()
  expect(ran.length).toBe(2)
})

test('a configured memory directory is linted too', { options: { memoryDir: '~/notes/memory' } }, async ($, on) => {
  world(on)
  expect((await write($, '/home/cj/notes/memory/x.md', 'Currently stuck on the build')).deny).toContain('task state')
  expect((await write($, '/home/cj/notes/other/x.md', 'Currently stuck on the build')).deny).toBeUndefined()
})
