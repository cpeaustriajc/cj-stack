export type Mode = 'off' | 'readonly' | 'research' | 'edit'

export type Active = Exclude<Mode, 'off'>

export type Held = { self: Active | null; subagents: Active | null }

declare module 'claude-code' {
  interface PluginState {
    'session-modes': {
      mode: Mode
      ended: Active | null
      told: Mode
      agentModes: Record<string, Held>
      parents: Record<string, string>
      pending: string[]
      agentsAllowed: boolean
    }
  }
}
