import type { Register } from 'claude-code'
import { explanation, isClassifier } from './explain'

const count = { plugin: 'denial-explainer', key: 'count' } as const

export const register: Register = on => {
  on('classic.PermissionDenied', async ($, e, next) => {
    const result = await next(e)
    if (!isClassifier(e.reason)) return result
    const held = await $.state.get(count)
    const n = (held.value ?? 0) + 1
    await $.state.set(count, n)
    $.ui.toast(explanation({ tool: e.tool_name, input: e.tool_input, reason: e.reason }, n))
    return result
  })
}
