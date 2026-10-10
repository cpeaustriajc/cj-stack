import type { PromptAutocompleteSuggestion } from 'claude-code'
import { MODES } from './modes'
import type { Mode } from './modes'

const DIM: Record<Mode, string> = {
  audit: 'read and report only',
  'no-pr': 'no pull requests',
  chat: 'answer here, no PR or push',
  off: 'lift the current mode',
}

const PARTIAL = /^\/mode ([^\s]*)$/

export function modeSuggestions(text: string, cursor: number, current: Mode): PromptAutocompleteSuggestion[] {
  const found = PARTIAL.exec(text)
  if (cursor !== text.length || !found) return []
  const partial = found[1].toLowerCase()
  return MODES.filter(m => m.startsWith(partial)).map(m => ({
    text: m,
    description: m === current ? `${DIM[m]} (on)` : DIM[m],
  }))
}
