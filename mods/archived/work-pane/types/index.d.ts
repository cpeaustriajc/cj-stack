export type TestRun = {
  id: string
  label: string
  log: string
  done?: number
  total?: number
  pass?: number
  fail?: number
  endedAt?: number
  isFailed?: boolean
}

declare module 'claude-code' {
  interface PluginState {
    'work-pane': { runs: TestRun[] }
  }
}
