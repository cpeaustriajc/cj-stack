export type Mode = 'off' | 'audit' | 'no-pr' | 'chat' | 'product'

declare module 'claude-code' {
  interface PluginState {
    'session-modes': { mode: Mode; ended: Exclude<Mode, 'off'> | null; told: Mode; planned: boolean }
  }
}
