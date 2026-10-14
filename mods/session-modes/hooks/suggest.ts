import type { PromptAutocompleteSuggestion } from 'claude-code'
import { LADDER, MODES } from './modes'
import type { Mode } from './modes'

const hint = (m: Mode): string => (m === 'off' ? 'lift the current mode' : LADDER[m].hint)

const EXTRA = [
  { text: 'clear', description: 'clear the modes Claude set' },
  { text: 'agents', description: 'turn agent_mode on or off' },
]

const AGENT_VALUES = [
  { text: 'on', description: 'let Claude set modes' },
  { text: 'off', description: 'stop Claude setting modes' },
]

const PARTIAL = /^\/mode ([^\s]*)$/
const AGENTS_PARTIAL = /^\/mode agents ([^\s]*)$/i

export function modeSuggestions(text: string, cursor: number, current: Mode): PromptAutocompleteSuggestion[] {
  if (cursor !== text.length) return []
  const agents = AGENTS_PARTIAL.exec(text)
  if (agents) {
    const partial = agents[1].toLowerCase()
    return AGENT_VALUES.filter(v => v.text.startsWith(partial))
  }
  const found = PARTIAL.exec(text)
  if (!found) return []
  const partial = found[1].toLowerCase()
  const modes = MODES.filter(m => m.startsWith(partial)).map(m => ({
    text: m,
    description: m !== current ? hint(m) : m === 'off' ? 'no mode is on' : `${hint(m)} (on)`,
  }))
  return [...modes, ...EXTRA.filter(x => x.text.startsWith(partial))]
}
