import { atom, read, update } from 'claude-code'
import type { Hook, Register } from 'claude-code'
import { SECTION, parseMode, report, verdict } from './modes'
import type { Mode } from './modes'

type Api = Parameters<Hook<'session.start'>>[0]

const mode = atom({ plugin: 'session-modes', key: 'mode' } as const, 'off' as Mode)
const SECTION_ID = 'session-modes:mode'

async function drawStatus($: Api, current: Mode): Promise<void> {
  await $.ui.status(current === 'off' ? undefined : `mode: ${current}`)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    if (e.isInteractive === false) return result
    await $.command.register({ name: 'mode', description: 'Set the session mode: audit, no-pr, chat or off' })
    await drawStatus($, await read($, mode))
    return result
  })

  on('command.run', { command: 'mode' }, async ($, e) => {
    const wanted = e.args.trim() === '' ? undefined : parseMode(e.args)
    if (e.args.trim() === '') return { text: report(await read($, mode)) }
    if (!wanted) return { text: `Unknown mode "${e.args.trim()}". ${report(await read($, mode))}` }
    await update($, mode, () => wanted)
    await drawStatus($, wanted)
    return { text: wanted === 'off' ? 'Mode off.' : `Mode ${wanted} on.` }
  })

  on('tool.call', async ($, e, next) => {
    const command = e.tool === 'Bash' && typeof (e as { command?: unknown }).command === 'string' ? (e as { command: string }).command : ''
    const deny = verdict(await read($, mode), e.tool, command)
    return deny ? { deny } : next(e)
  })

  on('prompt.compose', async ($, e, next) => {
    const result = await next(e)
    const current = await read($, mode)
    if (current === 'off') return result
    return { sections: [...result.sections, { id: SECTION_ID, text: SECTION[current], scope: 'session' }] }
  })
}
