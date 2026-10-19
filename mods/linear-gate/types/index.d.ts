export type Asks = Record<string, string>

declare module 'claude-code' {
  interface PluginState {
    'linear-gate': { asks: Asks }
  }
}
