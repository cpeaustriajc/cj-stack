import { expect, test } from 'claude-code/testing'
import type { On } from 'claude-code'
import shape from './actions'

// Placeholders match run.py: "~/" is the fake home, "<project>" the fake project.
const HOME = '/home/cj'
const PROJECT = '/home/cj/app'

function place(value: unknown): unknown {
  if (typeof value === 'string') return value.replace(/^~(?=\/)/, HOME).replace(/<project>/g, PROJECT)
  if (Array.isArray(value)) return value.map(place)
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, place(v)]))
  }
  return value
}

function world(on: On) {
  on('env.get', (_$, e) => ({ value: (e as { name: string }).name === 'HOME' ? HOME : undefined }) as never)
  on('tool.call', () => ({ result: { ok: true } }) as never)
  on('tool.check', () => ({ decision: 'ask' }) as never)
}

for (const a of shape.actions) {
  test(`${a.id} ${a.owned} is not denied by a mod`, async ($: any, on) => {
    world(on)
    const r = await $.tool.call({ tool: a.tool, ...(place(a.input) as object) })
    expect(r.deny, `${a.id} (${a.owned}) denied`).toBeUndefined()
  })
}

for (const a of shape.actions) {
  test(`${a.id} ${a.owned} keeps Claude Code's permission verdict`, async ($: any, on) => {
    world(on)
    const r = await $.tool.check({ tool: a.tool, input: place(a.input) })
    expect(r.decision, `${a.id} (${a.owned}) decided by a mod`).toBe('ask')
  })
}
