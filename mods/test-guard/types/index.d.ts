export type Allowed = string[]

declare module 'claude-code' {
  interface PluginState {
    'test-guard': {
      allowed: Allowed
    }
  }
}
