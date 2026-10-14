export type Mode = 'off' | 'audit' | 'no-pr' | 'chat' | 'product'

export type Active = Exclude<Mode, 'off'>

export type Held = { self: Active | null; subagents: Active | null }

declare module 'claude-code' {
  interface PluginState {
    'session-modes': {
      mode: Mode
      ended: Active | null
      told: Mode
      planned: boolean
      agentModes: Record<string, Held>
      parents: Record<string, string>
    }
  }
}
