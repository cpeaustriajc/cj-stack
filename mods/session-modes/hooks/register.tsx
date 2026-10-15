import { atom, read, update } from 'claude-code'
import type { Hook, Register } from 'claude-code'
import {
  AGENTS_OFF_DENY,
  AGENTS_OFF_NOTE,
  AGENTS_ON_NOTE,
  AGENT_TOOL,
  AGENT_TOOL_DESCRIPTION,
  AGENT_TOOL_SCHEMA,
  CHECK_NOTE,
  CLEARED_NOTE,
  INHERITED_NOTE,
  LADDER,
  MODE_NOTE,
  MODES,
  OFF_SECTION,
  SUBAGENT_NOTE,
  agentModeText,
  claudeParts,
  holdsAny,
  parseMode,
  parseOverride,
  parseScope,
  report,
  reword,
  verdict,
} from './modes'
import type { Active, Held, Mode } from './modes'
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

const mode = atom({ plugin: 'session-modes', key: 'mode' } as const, 'off' as Mode)
const ended = atom({ plugin: 'session-modes', key: 'ended' } as const, null as Active | null)
const told = atom({ plugin: 'session-modes', key: 'told' } as const, 'off' as Mode)
const agentModes = atom({ plugin: 'session-modes', key: 'agentModes' } as const, {} as Record<string, Held>)
const parents = atom({ plugin: 'session-modes', key: 'parents' } as const, {} as Record<string, string>)
const pending = atom({ plugin: 'session-modes', key: 'pending' } as const, [] as string[])
const agentsAllowed = atom({ plugin: 'session-modes', key: 'agentsAllowed' } as const, true)
const SECTION_ID = 'session-modes:mode'

const NARROW = 60
const MAIN = 'main'
const NONE: Held = { self: null, subagents: null }

const tell = ($: Api, note: string) => update($, pending, all => [...all, note])

async function clearAgentModes($: Api): Promise<boolean> {
  const all = await read($, agentModes)
  if (!holdsAny(all)) return false
  await update($, agentModes, () => ({}))
  await tell($, CLEARED_NOTE(claudeParts(all[MAIN]) ?? 'modes set by subagents'))
  return true
}

async function setMode($: Api, wanted: Mode): Promise<void> {
  const old = await read($, mode)
  await update($, mode, () => wanted)
  if (wanted === 'off') await clearAgentModes($)
  if (wanted !== 'off') await update($, ended, () => null)
  else if (old !== 'off') await update($, ended, () => old)
  await publishState($, wanted)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    // The desktop app runs sessions through the SDK, so isInteractive is false there.
    await $.tool.register({
      name: 'agent_mode',
      description: AGENT_TOOL_DESCRIPTION,
      inputSchema: AGENT_TOOL_SCHEMA,
      isDeferred: false,
    })
    await $.command.register({
      name: 'mode',
      description: 'Set the session mode: readonly, research, prototype, edit or off',
      argumentHint: 'readonly | research | prototype | edit | off',
    })
    const current = await read($, mode)
    if (current !== 'off') await publishState($, current)
    await pruneState($)
    return result
  })

  on('command.run', { command: 'mode' }, async ($, e) => {
    const wanted = e.args.trim() === '' ? undefined : parseMode(e.args)
    if (e.args.trim() === '') {
      const held = claudeParts((await read($, agentModes))[MAIN])
      const agentsOff = (await read($, agentsAllowed)) ? '' : ' Agent modes: off.'
      return { text: report(await read($, mode)) + (held ? ` Set by Claude: ${held}.` : '') + agentsOff }
    }
    const override = parseOverride(e.args)
    if (override === 'clear') {
      return { text: (await clearAgentModes($)) ? "Cleared Claude's modes." : 'Claude has no modes set.' }
    }
    if (override === 'agents-invalid') return { text: 'Use /mode agents off or /mode agents on.' }
    if (override === 'agents-off') {
      await update($, agentsAllowed, () => false)
      await clearAgentModes($)
      await tell($, AGENTS_OFF_NOTE)
      return { text: 'Agent modes off. Claude cannot set modes.' }
    }
    if (override === 'agents-on') {
      await update($, agentsAllowed, () => true)
      await tell($, AGENTS_ON_NOTE)
      return { text: 'Agent modes on.' }
    }
    if (!wanted) return { text: `Unknown mode "${e.args.trim()}". ${report(await read($, mode))}` }
    await setMode($, wanted)
    return { text: wanted === 'off' ? 'Mode off.' : `Mode ${wanted} on.` }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const current = await read($, mode)
    const claude = claudeParts((await read($, agentModes))[MAIN])
    if ((current === 'off' && !claude) || e.props.hasSurvey) return next(e)
    const { Box, Text, Button } = $.ui.resolve(e)
    const claudeRow = claude ? (
      <Box flexDirection="row" gap={1}>
        <Box flexGrow={1} flexShrink={1}>
          <Text dimColor wrap="truncate-end">{`Set by Claude: ${claude}`}</Text>
        </Box>
        <Button
          key="clear-agents"
          label="Clear"
          onPress={async () => {
            await clearAgentModes($)
            await $.ui.toast("Claude's modes cleared.")
          }}
        />
      </Box>
    ) : null
    if (current === 'off') return <Box flexDirection="column">{claudeRow}</Box>
    const { label, chip, lead, detail } = LADDER[current]
    return (
      <Box flexDirection="column">
        <Box flexDirection="row" gap={1}>
          <Text weight="semibold" color={chip}>
            {label}
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
        {claudeRow}
      </Box>
    )
  })

  on('tool.call', async ($, e, next) => {
    const input = e as { command?: unknown; file_path?: unknown; notebook_path?: unknown; mode?: unknown; scope?: unknown }
    const caller = e.agentId ?? MAIN
    if (e.tool === AGENT_TOOL) {
      const wanted = typeof input.mode === 'string' ? parseMode(input.mode) : undefined
      const scope = parseScope(input.scope)
      if (!wanted || !scope) {
        return { deny: `agent_mode needs a mode (${MODES.join(', ')}) and a scope (self or subagents).` }
      }
      if (wanted !== 'off' && !(await read($, agentsAllowed))) return { deny: AGENTS_OFF_DENY }
      const held = (await read($, agentModes))[caller] ?? NONE
      const user = await read($, mode)
      const text = agentModeText(wanted, scope, held[scope], user)
      await update($, agentModes, all => ({
        ...all,
        [caller]: { ...(all[caller] ?? NONE), [scope]: wanted === 'off' ? null : wanted },
      }))
      return { result: text } as never
    }
    const command = e.tool === 'Bash' && typeof input.command === 'string' ? input.command : ''
    const rawPath = input.file_path ?? input.notebook_path
    const path = typeof rawPath === 'string' ? rawPath : ''
    const action = (e as { action?: unknown }).action
    const call = { tool: e.tool, command, path, action: typeof action === 'string' ? action : '' }
    const user = verdict(await read($, mode), call)
    if (user) return { deny: user }
    const held = await read($, agentModes)
    const own = held[caller]?.self
    const ownDeny = own ? verdict(own, call) : undefined
    if (ownDeny) return { deny: reword(ownDeny, 'agent_mode off with scope self to leave.') }
    const links = await read($, parents)
    const seen = new Set<string>([caller])
    for (let at = links[caller]; at !== undefined && !seen.has(at); at = links[at]) {
      seen.add(at)
      const above = held[at]?.subagents
      const aboveDeny = above ? verdict(above, call) : undefined
      if (aboveDeny) return { deny: reword(aboveDeny, 'set by the agent that started you.') }
    }
    return next(e)
  }).catch(($, e, next) =>
    next.called ? next(e) : { deny: `session-modes: could not check this call, so it is denied (${next.error.message ?? next.error.kind}).` },
  )

  on('prompt.compose', async ($, e, next) => {
    const result = await next(e)
    const current = await read($, mode)
    const last = await read($, ended)
    const text = current !== 'off' ? LADDER[current].section : last ? OFF_SECTION(last) : undefined
    if (text === undefined) return result
    return { sections: [...result.sections, { id: SECTION_ID, text, scope: 'session' }] }
  })

  on('prompt.submit', async ($, e, next) => {
    const current = await read($, mode)
    const extra = await read($, pending)
    const added: string[] = []
    if (current !== (await read($, told))) {
      added.push(MODE_NOTE(current, await read($, ended)))
      await update($, told, () => current)
    }
    if (extra.length) {
      added.push(...extra)
      await update($, pending, () => [])
    }
    const kind = e.origin.kind
    if (
      (kind === 'composer' || kind === 'bridge' || kind === 'sdk') &&
      e.isMeta !== true &&
      (await read($, agentsAllowed)) &&
      current !== 'readonly'
    ) {
      added.push(CHECK_NOTE((await read($, agentModes))[MAIN]?.self ?? null))
    }
    if (added.length === 0) return next(e)
    return next({ ...e, context: [...(e.context ?? []), ...added] })
  })

  on('agent.spawn', async ($, e, next) => {
    const parent = e.parentAgentId ?? MAIN
    if (e.resume) {
      // The engine ignores a prompt rewrite on a resume, so pass the event on unchanged.
      const resumed = await next(e)
      const id = resumed.agentId
      if (id) await update($, parents, all => (id in all ? all : { ...all, [id]: parent }))
      return resumed
    }
    const current = await read($, mode)
    const notes: string[] = []
    if (current !== 'off') notes.push(SUBAGENT_NOTE(current))
    const held = await read($, agentModes)
    const links = await read($, parents)
    const inherited: Active[] = []
    const seen = new Set<string>()
    for (let at: string | undefined = parent; at !== undefined && !seen.has(at); at = links[at]) {
      seen.add(at)
      const m = held[at]?.subagents
      if (m && m !== current && !inherited.includes(m)) inherited.push(m)
    }
    notes.push(...inherited.map(INHERITED_NOTE))
    const result = await next(notes.length ? { ...e, prompt: `${notes.join(' ')}\n\n${e.prompt}` } : e)
    if (result.agentId) {
      const child = result.agentId
      await update($, parents, all => ({ ...all, [child]: parent }))
    }
    return result
  }).catch(async ($, e, next) => {
    if (next.error.kind !== 're-entry') {
      await $.ui.toast(`session-modes: the agent.spawn hook failed (${next.error.message ?? next.error.kind}); mode notes may be missing.`)
    }
    return next(e)
  })

  on('prompt.autocomplete', async ($, e, next) => {
    const rows = modeSuggestions(e.text, e.cursor, await read($, mode))
    const out = await next(e)
    return rows.length ? { suggestions: [...out.suggestions, ...rows] } : out
  })
}
