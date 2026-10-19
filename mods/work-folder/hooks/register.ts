import type { Hook, Register } from 'claude-code'

type Api = Parameters<Hook<'tool.call'>>[0]

const MOD = 'work-folder'
const CONFIG = '.claude/work-folder.json'
const WORK = '.claude/work'
const KEEP_DAYS = 1
const DAY = 86_400_000

const TOOL_FOLDERS = new Set([
  '.claude', '.agents', '.agent', '.codex', '.cursor', '.gemini', '.grok', '.muse', '.qwen', '.kimi', '.kimi-code',
  '.trae', '.codebuddy', '.comate', '.lingma', '.qoder', '.windsurf', '.devin', '.kiro', '.roo', '.cline',
  '.clinerules', '.continue', '.junie', '.opencode', '.factory', '.augment', '.kilo', '.kilocode', '.github',
  '.vscode', '.idea',
])

const ROOT_DOCS = new Set([
  'readme', 'claude', 'claude.local', 'agents', 'agents.override', 'gemini', 'qwen', 'codebuddy', 'codebuddy.local',
  'warp', 'changelog', 'contributing', 'security', 'code_of_conduct', 'license', 'notice', 'llms', 'llms-full',
])

const RULES: { why: string; test: (folders: string[], base: string, rel: string) => boolean }[] = [
  {
    why: 'a prototype, scratch, recovery, research-notes, spike or .local folder',
    test: f => f.some(s => ['prototypes', '.scratch', '.recovery', 'research_notes'].includes(s) || s.startsWith('spike-') || s.endsWith('.local')),
  },
  {
    why: 'a reports/ or docs/ planning folder',
    test: (_f, _b, rel) => /^(reports|docs\/(stories|epics|research|perf|qa|implementation|plans|plan|notes))\//.test(rel),
  },
  {
    why: 'a test artifact or evidence folder',
    test: f => f.some(s => ['artifacts', '.e2e-evidence', 'test-results'].includes(s)),
  },
  {
    why: 'a loose document at the repo root',
    test: (f, b) => f.length === 0 && /\.(md|html|txt)$/.test(b) && !ROOT_DOCS.has(b.replace(/\.[^.]*$/, '').toLowerCase()),
  },
  {
    why: 'a findings, report, plan or numbered evidence file name',
    test: (_f, b) =>
      /^\d+-[A-Z][A-Z0-9-]*\.md$/.test(b) ||
      /^\d+-[a-z-]*verification\.json$/.test(b) ||
      /^(findings|report|summary|scores)\.md$/i.test(b) ||
      /-(report|plan|draft)\.md$/.test(b) ||
      /-decisions-[^/]*\.md$/.test(b),
  },
  {
    why: 'a probe or temporary test file name',
    test: (_f, b) => b.startsWith('zz-probe-') || b.startsWith('test_zz_') || b.endsWith('_tmp.py'),
  },
]

function reason(rel: string): string | undefined {
  const segs = rel.split('/')
  if (TOOL_FOLDERS.has(segs[0])) return undefined
  const base = segs[segs.length - 1]
  const folders = segs.slice(0, -1)
  return RULES.find(r => r.test(folders, base, rel))?.why
}

// Every tail is a possible rel, as the root is unknown before fs; the claude-owned runner has no fs hook.
function mayMatch(segs: string[]): boolean {
  return segs.some(
    (_s, i) => !TOOL_FOLDERS.has(segs[i - 1]) && !TOOL_FOLDERS.has(segs[i - 2]) && reason(segs.slice(i).join('/')) !== undefined,
  )
}

function globToRegExp(glob: string): RegExp {
  const src = glob
    .replace(/[.+?^${}()|[\]\\]/g, '\\$&')
    .replace(/\*\*\//g, '\u0000')
    .replace(/\*\*/g, '\u0001')
    .replace(/\*/g, '[^/]*')
    .replace(/\u0000/g, '(?:.*/)?')
    .replace(/\u0001/g, '.*')
  return new RegExp(`^${src}$`)
}

function allowed(rel: string, allow: string[]): boolean {
  return allow.some(a => (a.endsWith('/') ? rel.startsWith(a) : globToRegExp(a).test(rel)))
}

function parseAllow(text: string): string[] {
  const data = JSON.parse(text) as unknown
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('not a JSON object')
  const allow = (data as { allow?: unknown }).allow
  if (allow === undefined) return []
  if (!Array.isArray(allow) || !allow.every(a => typeof a === 'string')) throw new Error('"allow" is not an array of strings')
  return allow
}

function parseKeepDays(text: string): number {
  const data = JSON.parse(text) as unknown
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('not a JSON object')
  const days = (data as { keepDays?: unknown }).keepDays
  if (days === undefined) return KEEP_DAYS
  if (typeof days !== 'number' || !Number.isFinite(days) || days < 0) throw new Error('"keepDays" is not a number of days, 0 or more')
  return days
}

async function repoRoot($: Api, path: string): Promise<string | undefined> {
  const norm = path.replace(/\\/g, '/')
  const lead = norm.startsWith('/') ? '/' : ''
  const segs = norm.split('/').filter(Boolean)
  for (let i = segs.length; i > 0; i--) {
    const dir = lead + segs.slice(0, i).join('/')
    if (await $.fs.exists(`${dir}/.git`)) return dir
  }
  return undefined
}

// Symbolic links are not followed: their own mtimeMs is 0 and git clean removes only the link.
async function changedSince($: Api, path: string, cutoff: number): Promise<boolean> {
  const stat = await $.fs.stat(path)
  if (stat.mtimeMs > cutoff) return true
  if (stat.kind !== 'dir' || stat.isLink) return false
  for (const entry of await $.fs.list(path)) {
    if (entry.kind === 'dir' ? await changedSince($, `${path}/${entry.name}`, cutoff) : entry.mtimeMs > cutoff) return true
  }
  return false
}

async function cleanWork($: Api, cwd: string): Promise<void> {
  const root = await repoRoot($, cwd)
  if (root === undefined || !(await $.fs.exists(`${root}/${WORK}`))) return
  const config = `${root}/${CONFIG}`
  let days = KEEP_DAYS
  if (await $.fs.exists(config)) {
    try {
      days = parseKeepDays((await $.fs.read(config)) as string)
    } catch (err) {
      $.ui.toast(`${MOD}: ${config} is not valid (${(err as Error).message}). Fix it to { "keepDays": 1 }, or delete it. Nothing in ${WORK} was cleaned.`)
      return
    }
  }
  if (days === 0) return
  const cutoff = (await $.clock.now()) - days * DAY
  const stale: string[] = []
  for (const entry of await $.fs.list(`${root}/${WORK}`)) {
    if (!(await changedSince($, `${root}/${WORK}/${entry.name}`, cutoff))) stale.push(entry.name)
  }
  if (stale.length === 0) return
  const { exitCode, stderr } = await $.process.run(['git', 'clean', '-ffdX', '--', ...stale.map(n => `${WORK}/${n}`)], { cwd: root })
  if (exitCode !== 0) throw new Error(`git clean exited ${exitCode}: ${stderr.trim()}`)
  $.ui.toast(`${MOD}: cleaned ${stale.length} ${stale.length === 1 ? 'entry' : 'entries'} in ${WORK} not changed for ${days} ${days === 1 ? 'day' : 'days'}: ${stale.join(', ')}`)
}

async function judge($: Api, path: string): Promise<string | undefined> {
  const abs = path.replace(/\\/g, '/')
  const segs = abs.split('/').filter(Boolean)
  if (!mayMatch(segs)) return undefined
  if (await $.fs.exists(abs)) return undefined
  let root: string | undefined
  for (let i = segs.length - 1; i >= 0 && root === undefined; i--) {
    const dir = `/${segs.slice(0, i).join('/')}`.replace(/^\/$/, '')
    if (await $.fs.exists(`${dir}/.git`)) root = dir
  }
  if (root === undefined) return undefined
  const rel = abs.slice(root.length + 1)
  const why = reason(rel)
  if (!why) return undefined
  const config = `${root}/${CONFIG}`
  let allow: string[] = []
  if (await $.fs.exists(config)) {
    const text = (await $.fs.read(config)) as string
    try {
      allow = parseAllow(text)
    } catch (err) {
      return `${MOD}: ${config} is not valid (${(err as Error).message}). Fix it to { "allow": ["path/prefix/", "glob/**/*.md"] }, or delete it.`
    }
  }
  if (allowed(rel, allow)) return undefined
  return (
    `${MOD}: ${rel} looks like an agent working file (${why}). Write it under .claude/work/<topic>/ instead; ` +
    `that folder is gitignored. If a person keeps this file in the repo, add it to "allow" in ${CONFIG}.`
  )
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    try {
      await cleanWork($, e.cwd)
    } catch (cause) {
      throw new Error(`${MOD}: could not clean ${WORK}`, { cause })
    }
    return result
  })

  const guard = (path: string, why = 'no answer') =>
    mayMatch(path.replace(/\\/g, '/').split('/').filter(Boolean))
      ? { deny: `${MOD}: could not check ${path} (${why}). Write it under .claude/work/<topic>/ instead, or retry.` }
      : undefined

  on('tool.call', { tool: 'Write' }, async ($, e, next) => {
    const deny = await judge($, e.file_path)
    return deny ? { deny } : next(e)
  }).catch(($, e, next) => (next.called ? next(e) : (guard(e.file_path, next.error.message) ?? next(e))))

  on('tool.call', { tool: 'NotebookEdit' }, async ($, e, next) => {
    const deny = await judge($, e.notebook_path)
    return deny ? { deny } : next(e)
  }).catch(($, e, next) => (next.called ? next(e) : (guard(e.notebook_path, next.error.message) ?? next(e))))
}
