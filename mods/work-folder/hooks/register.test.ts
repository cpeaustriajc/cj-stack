import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'

const REPO = '/home/cj/app'

function world(on: On, opts: { files?: Record<string, string>; repo?: boolean; fsFails?: boolean } = {}) {
  const files: Record<string, string> = { ...(opts.repo === false ? {} : { [`${REPO}/.git`]: '' }), ...opts.files }
  const ran: string[] = []
  const probed: string[] = []
  on('fs.exists', (_$, e) => {
    const path = (e as { path: string }).path
    probed.push(path)
    if (opts.fsFails) throw new Error('EACCES: permission denied')
    return { value: path in files } as never
  })
  on('fs.read', (_$, e) => {
    const path = (e as { path: string }).path
    if (!(path in files)) throw new Error(`ENOENT: ${path}`)
    return { value: files[path] } as never
  })
  on('tool.call', (_$, e) => {
    const x = e as { file_path?: string; notebook_path?: string }
    ran.push(x.file_path ?? x.notebook_path ?? '')
    return { result: { ok: true } } as never
  })
  return { ran, probed }
}

const write = ($: any, rel: string) => $.tool.call({ tool: 'Write', file_path: `${REPO}/${rel}`, content: 'x' })

const DENY = [
  'docs/stories/MP-13-exact-match-check.md',
  'prototypes/merge-lane/index.html',
  'apps/market/prototypes/x/index.html',
  'qwen-voice-cost-draft.md',
  'FINDINGS.md',
  'validate.html',
  'packages/core/107-EVIDENCE.md',
  'packages/core/112-verification.json',
  '.scratch/mp-45-reply-aice.md',
  'research_notes/a/b.md',
  'reports/x.md',
  'spike-292/findings.md',
  'artifacts/probe-233/probe.spec.ts',
  '.e2e-evidence/mp-111/qa/run-e2e.sh',
  'apps/web/e2e/zz-probe-load.spec.ts',
  'e2e/tests/test_zz_scratch_a.py',
  'audit-issues.local/x.md',
]

const PASS = [
  'README.md',
  'CLAUDE.md',
  '.claude/work/mp-135/plan.md',
  '.agents/skills/x/SKILL.md',
  '.github/workflows/ci.yml',
  'apps/web/src/features/x.ts',
  'apps/web/src/features/evidence/panel.tsx',
  'packages/core/src/research.ts',
  'e2e/qa/mp-200-x.md',
]

for (const rel of DENY) {
  test(`a new ${rel} is denied`, async ($, on) => {
    const w = world(on)
    const r = await write($, rel)
    expect(r.deny).toContain(`work-folder: ${rel} looks like an agent working file (`)
    expect(r.deny).toContain('Write it under .claude/work/<topic>/ instead; that folder is gitignored.')
    expect(r.deny).toContain('add it to "allow" in .claude/work-folder.json')
    expect(w.ran).toEqual([])
  })
}

for (const rel of PASS) {
  test(`a new ${rel} passes`, async ($, on) => {
    const w = world(on)
    expect((await write($, rel)).deny).toBeUndefined()
    expect(w.ran).toEqual([`${REPO}/${rel}`])
  })
}

test('a path no rule can match never touches fs', async ($, on) => {
  const w = world(on)
  expect((await write($, 'apps/web/src/features/x.ts')).deny).toBeUndefined()
  expect(w.probed).toEqual([])
})

test('a file in a tool folder never touches fs, a worktree under one is still judged', async ($, on) => {
  const w = world(on, { files: { [`${REPO}/.claude/worktrees/wt/.git`]: 'gitdir: ../../../.git/worktrees/wt' } })
  expect((await write($, '.claude/commands/x.md')).deny).toBeUndefined()
  expect(w.probed).toEqual([])
  expect((await write($, '.claude/worktrees/wt/notes.md')).deny).toContain('work-folder: notes.md looks like')
})

test('an existing file at a deny path is overwritten',async ($, on) => {
  const w = world(on, { files: { [`${REPO}/reports/x.md`]: 'old' } })
  expect((await write($, 'reports/x.md')).deny).toBeUndefined()
  expect(w.ran).toEqual([`${REPO}/reports/x.md`])
})

test('a path outside any git repo passes', async ($, on) => {
  const w = world(on, { repo: false })
  expect((await write($, 'reports/x.md')).deny).toBeUndefined()
  expect((await write($, 'packages/core/107-EVIDENCE.md')).deny).toBeUndefined()
  expect(w.ran).toEqual([`${REPO}/reports/x.md`, `${REPO}/packages/core/107-EVIDENCE.md`])
})

test('the nearest .git, dir or file, sets the root the path is judged from', async ($, on) => {
  world(on, { files: { [`${REPO}/apps/web/.git`]: 'gitdir: ../../.git/worktrees/web' } })
  expect((await write($, 'apps/web/reports/x.md')).deny).toContain('work-folder: reports/x.md looks like')
  expect((await write($, 'apps/web/src/x.ts')).deny).toBeUndefined()
})

test('a deny path covered by an allow prefix passes', async ($, on) => {
  world(on, { files: { [`${REPO}/.claude/work-folder.json`]: '{ "allow": ["reports/"] }' } })
  expect((await write($, 'reports/x.md')).deny).toBeUndefined()
  expect((await write($, 'docs/plans/x.md')).deny).toContain('reports/ or docs/')
})

test('a deny path covered by an allow glob passes', async ($, on) => {
  world(on, { files: { [`${REPO}/.claude/work-folder.json`]: '{ "allow": ["docs/stories/*.md", "**/prototypes/**", "NOTES.md"] }' } })
  expect((await write($, 'docs/stories/MP-1.md')).deny).toBeUndefined()
  expect((await write($, 'docs/stories/a/MP-1.md')).deny).toContain('reports/ or docs/')
  expect((await write($, 'apps/market/prototypes/x/index.html')).deny).toBeUndefined()
  expect((await write($, 'prototypes/x/index.html')).deny).toBeUndefined()
  expect((await write($, 'NOTES.md')).deny).toBeUndefined()
  expect((await write($, 'TODO.md')).deny).toContain('loose document')
})

test('a NotebookEdit at an allowed path passes, at a deny path is denied', async ($, on) => {
  const w = world(on, { files: { [`${REPO}/.claude/work-folder.json`]: '{ "allow": ["prototypes/keep/"] }' } })
  const nb = (rel: string) => ($ as any).tool.call({ tool: 'NotebookEdit', notebook_path: `${REPO}/${rel}`, new_source: 'x' })
  expect((await nb('prototypes/keep/a.ipynb')).deny).toBeUndefined()
  expect((await nb('prototypes/other/a.ipynb')).deny).toContain('prototype')
  expect(w.ran).toEqual([`${REPO}/prototypes/keep/a.ipynb`])
})

test('an Edit at a deny path is left alone', async ($, on) => {
  const w = world(on)
  const r = await ($ as any).tool.call({ tool: 'Edit', file_path: `${REPO}/reports/x.md`, old_string: 'a', new_string: 'b' })
  expect(r.deny).toBeUndefined()
  expect(w.ran).toEqual([`${REPO}/reports/x.md`])
})

test('a malformed work-folder.json denies, naming the file and the fix', async ($, on) => {
  const w = world(on, { files: { [`${REPO}/.claude/work-folder.json`]: '{ "allow": [' } })
  const r = await write($, 'reports/x.md')
  expect(r.deny).toContain(`${REPO}/.claude/work-folder.json is not valid`)
  expect(r.deny).toContain('{ "allow": [')
  expect(w.ran).toEqual([])
})

test('an allow that is not a string array denies the same way', async ($, on) => {
  world(on, { files: { [`${REPO}/.claude/work-folder.json`]: '{ "allow": "reports/" }' } })
  expect((await write($, 'reports/x.md')).deny).toContain('"allow" is not an array of strings')
})

test('an allow array holding a non-string denies the same way', async ($, on) => {
  world(on, { files: { [`${REPO}/.claude/work-folder.json`]: '{ "allow": ["reports/", 3] }' } })
  expect((await write($, 'reports/x.md')).deny).toContain('work-folder.json is not valid')
})

test('an fs failure on a judged path denies with could not check', async ($, on) => {
  const w = world(on, { fsFails: true })
  const r = await write($, 'reports/x.md')
  expect(r.deny).toContain(`work-folder: could not check ${REPO}/reports/x.md`)
  expect(w.ran).toEqual([])
})
