import type { Register } from 'claude-code'

const MOD = 'memory-lint'
const DEFAULT_DIR = /\/projects\/[^/]+\/memory\//
const INDEX = /(^|\/)MEMORY\.md$/
const MAX_TOPIC = 1200
const MAX_INDEX_LINE = 200
// Only code files: a bare `\.\w+:\d+` also matches hosts with ports (127.0.0.1:8000).
const CODE_EXT = 'ts|tsx|js|jsx|mjs|cjs|php|py|rb|go|rs|swift|kt|java|vue|svelte|css|scss|sql|sh|c|h|cpp|cs|ex|exs'

// Each rule names one kind of note that is not worth carrying into later sessions.
const RULES: { why: string; test: (text: string) => boolean }[] = [
  {
    why: 'task state (in progress, next step, this session, today)',
    test: t => /\b(currently|in progress|this session|today|yesterday|right now|for now|next steps?|todo|wip|working on|just (fixed|added|merged|pushed|finished))\b/i.test(t),
  },
  {
    why: 'a one-off reference (PR, issue, commit or claude/ branch)',
    test: t =>
      /\b(pr|pull request|issue)\s*#?\d+\b/i.test(t) ||
      /(^|\s)#\d{2,}\b/.test(t) ||
      /(^|[\s(`'"])claude\/[\w.-]+/.test(t) ||
      (t.match(/\b[0-9a-f]{7,40}\b/g) ?? []).some(h => /\d/.test(h) && /[a-f]/.test(h)),
  },
  {
    why: 'repo detail Claude can read again (a file:line pointer or a code block)',
    test: t => new RegExp(`[\\w/-]+\\.(${CODE_EXT}):\\d+`).test(t) || /^\s*```/m.test(t),
  },
  {
    why: 'dated status ("since 2026-09-04", "as of 2026") that goes stale unseen',
    test: t => /\b20\d{2}-[01]\d-[0-3]\d\b/.test(t) || /\bas of (19|20)\d{2}\b/i.test(t),
  },
]

const BAR =
  'Memory keeps durable facts that would otherwise be relearned: the user\'s corrections and preferences, ' +
  'and non-obvious quirks of this project or environment. If this is one, restate it without the flagged parts. ' +
  'If it is task state, a finding, or readable from the repo, do not save it. ' +
  'A rule the team shares goes in AGENTS.md or a checked-in rule; a decision goes in the team\'s decision log.'

function body(text: string): string {
  return text.replace(/^---\n[\s\S]*?\n---\n?/, '')
}

// For an Edit, only the lines it adds: removing or shortening memory always passes.
function added(oldText: string, newText: string): string {
  const before = new Set(oldText.split('\n'))
  return newText.split('\n').filter(l => !before.has(l)).join('\n')
}

function problems(path: string, text: string, whole: boolean): string[] {
  const found = RULES.filter(r => r.test(text)).map(r => r.why)
  if (INDEX.test(path)) {
    if (text.split('\n').some(l => l.length > MAX_INDEX_LINE)) found.push(`an index line over ${MAX_INDEX_LINE} characters (put detail in a topic file)`)
  } else if (whole && text.length > MAX_TOPIC) {
    found.push(`a topic file over ${MAX_TOPIC} characters (one memory per file)`)
  }
  return found
}

function isMemory(path: string, configured: string, home: string): boolean {
  if (!path.endsWith('.md')) return false
  if (DEFAULT_DIR.test(path)) return true
  if (!configured) return false
  const dir = configured.startsWith('~/') ? `${home}/${configured.slice(2)}` : configured
  return path.startsWith(dir)
}

export const register: Register = (on, options) => {
  const raw = typeof options.memoryDir === 'string' ? options.memoryDir.trim() : ''
  const configured = raw && raw.replace(/\/?$/, '/')

  const deny = (found: string[]) => ({
    deny: `${MOD}: memory not saved. It holds ${found.join('; ')}. ${BAR}`,
  })

  on('tool.call', { tool: 'Write' }, async ($, e, next) => {
    if (!isMemory(e.file_path, configured, (await $.env.get('HOME')) ?? '')) return next(e)
    const found = problems(e.file_path, body(e.content), true)
    return found.length ? deny(found) : next(e)
  }).catch(($, e, next) => next(e))

  on('tool.call', { tool: 'Edit' }, async ($, e, next) => {
    if (!isMemory(e.file_path, configured, (await $.env.get('HOME')) ?? '')) return next(e)
    const found = problems(e.file_path, added(e.old_string, e.new_string), false)
    return found.length ? deny(found) : next(e)
  }).catch(($, e, next) => next(e))
}
