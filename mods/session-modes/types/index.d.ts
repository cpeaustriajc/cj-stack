export type Mode = 'off' | 'audit' | 'no-pr' | 'chat'

declare module 'claude-code' {
  interface PluginState {
    'session-modes': { mode: Mode }
  }
}
