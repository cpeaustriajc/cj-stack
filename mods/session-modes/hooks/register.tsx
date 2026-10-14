import { atom, read, update } from 'claude-code'
import type { Hook, Register } from 'claude-code'
import { LABEL, MODE_NOTE, OFF_SECTION, SECTION, SUBAGENT_NOTE, parseMode, planningSkill, report, verdict } from './modes'
import type { Mode } from './modes'
import { modeSuggestions } from './suggest'

type Api = Parameters<Hook<'session.start'>>[0]

const MOD = 'session-modes'
const WEEK = 7 * 86_400_000

async function stateDir($: Api): Promise<string | undefined> {
  const config = await $.env.get('CLAUDE_CONFIG_DIR')
  if (config) return `${config}/mod-state`
  const home = (await $.env.get('HOME')) || (await $.env.get('USERPROFILE'))
  return home ? `${home}/.claude/mod-state` : undefined
}

async function remove($: Api, paths: string[]): Promise<void> {
  if (paths.length === 0) return
  await $.process.run(['rm', '-f', '--', ...paths])
}

export async function publishState($: Api, mode: string): Promise<void> {
  try {
    const dir = await stateDir($)
    if (!dir) return
    const path = `${dir}/${await $.session.id()}.${MOD}.json`
    await $.fs.write(path, JSON.stringify({ v: 1, mode: mode === 'off' ? null : mode }))
  } catch (cause) {
    throw new Error(`${MOD}: could not publish state for the status line`, { cause })
  }
}

export async function pruneState($: Api): Promise<void> {
  try {
    const dir = await stateDir($)
    if (!dir || !(await $.fs.exists(dir))) return
    const now = await $.clock.now()
    const stale = (await $.fs.list(dir)).filter(
      f => f.kind === 'file' && f.name.endsWith(`.${MOD}.json`) && now - f.mtimeMs > WEEK,
    )
    await remove($, stale.map(f => `${dir}/${f.name}`))
  } catch (cause) {
    throw new Error(`${MOD}: could not prune old state files`, { cause })
  }
}

type Active = Exclude<Mode, 'off'>

const mode = atom({ plugin: 'session-modes', key: 'mode' } as const, 'off' as Mode)
const ended = atom({ plugin: 'session-modes', key: 'ended' } as const, null as Active | null)
const told = atom({ plugin: 'session-modes', key: 'told' } as const, 'off' as Mode)
// Whether vision, shape or tickets has loaded this session: product mode's key to outside writes.
const planned = atom({ plugin: 'session-modes', key: 'planned' } as const, false)
const SECTION_ID = 'session-modes:mode'

const CHIP: Record<Active, string> = {
  audit: 'planMode',
  'no-pr': 'suggestion',
  chat: 'ide',
  product: 'merged',
}

const RULE: Record<Exclude<Active, 'product'>, { lead: string; detail: string }> = {
  audit: { lead: 'Read and report only.', detail: 'Edits, commits, pushes and PRs are blocked.' },
  'no-pr': { lead: 'Commit on the branch.', detail: 'Opening a PR is blocked.' },
  chat: { lead: 'Edits and commits are allowed.', detail: 'Pushes and PRs are blocked.' },
}

const NARROW = 60

async function setMode($: Api, wanted: Mode): Promise<void> {
  const old = await read($, mode)
  await update($, mode, () => wanted)
  if (wanted !== 'off') await update($, ended, () => null)
  else if (old !== 'off') await update($, ended, () => old)
  await publishState($, wanted)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    // The desktop app runs sessions through the SDK, so isInteractive is false there.
    await $.command.register({
      name: 'mode',
      description: 'Set the session mode: audit, no-pr, chat, product or off',
      argumentHint: 'audit | no-pr | chat | product | off',
    })
    const current = await read($, mode)
    if (current !== 'off') await publishState($, current)
    await pruneState($)
    return result
  })

  on('command.run', { command: 'mode' }, async ($, e) => {
    const wanted = e.args.trim() === '' ? undefined : parseMode(e.args)
    if (e.args.trim() === '') return { text: report(await read($, mode)) }
    if (!wanted) return { text: `Unknown mode "${e.args.trim()}". ${report(await read($, mode))}` }
    await setMode($, wanted)
    return { text: wanted === 'off' ? 'Mode off.' : `Mode ${wanted} on.` }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const current = await read($, mode)
    if (current === 'off' || e.props.hasSurvey) return next(e)
    const isPlanned = await read($, planned)
    const { lead, detail } =
      current === 'product'
        ? {
            lead: 'Plan in Markdown and the tracker.',
            detail: isPlanned ? 'Tracker writes are open.' : 'Tracker writes wait for vision, shape or tickets.',
          }
        : RULE[current]
    const { Box, Text, Button } = $.ui.resolve(e)
    return (
      <Box flexDirection="row" gap={1}>
        <Text bold color={CHIP[current]}>
          {LABEL[current]}
        </Text>
        <Box flexGrow={1} flexShrink={1}>
          <Text wrap="truncate-end">
            {lead}
            {e.props.bodyColumns < NARROW ? null : <Text dimColor>{' ' + detail}</Text>}
          </Text>
        </Box>
        <Button
          key="off"
          label="Turn off"
          onPress={async () => {
            await setMode($, 'off')
            await $.ui.toast('Mode off.')
          }}
        />
      </Box>
    )
  })

  on('skill.prompt', async ($, e, next) => {
    if (planningSkill(e.skill)) await update($, planned, () => true)
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    const input = e as { command?: unknown; file_path?: unknown; notebook_path?: unknown }
    const command = e.tool === 'Bash' && typeof input.command === 'string' ? input.command : ''
    const rawPath = input.file_path ?? input.notebook_path
    const path = typeof rawPath === 'string' ? rawPath : ''
    const deny = verdict(await read($, mode), { tool: e.tool, command, path, planned: await read($, planned) })
    return deny ? { deny } : next(e)
  })

  on('prompt.compose', async ($, e, next) => {
    const result = await next(e)
    const current = await read($, mode)
    const last = await read($, ended)
    const text = current !== 'off' ? SECTION[current] : last ? OFF_SECTION(last) : undefined
    if (text === undefined) return result
    return { sections: [...result.sections, { id: SECTION_ID, text, scope: 'session' }] }
  })

  on('prompt.submit', async ($, e, next) => {
    const current = await read($, mode)
    if (current === (await read($, told))) return next(e)
    const note = MODE_NOTE(current, await read($, ended))
    await update($, told, () => current)
    return next({ ...e, context: [...(e.context ?? []), note] })
  })

  on('agent.spawn', async ($, e, next) => {
    const current = await read($, mode)
    if (current === 'off' || e.workflow) return next(e)
    return next({ ...e, prompt: `${SUBAGENT_NOTE(current)}\n\n${e.prompt}` })
  })

  on('prompt.autocomplete', async ($, e, next) => {
    const rows = modeSuggestions(e.text, e.cursor, await read($, mode))
    const out = await next(e)
    return rows.length ? { suggestions: [...out.suggestions, ...rows] } : out
  })
}
