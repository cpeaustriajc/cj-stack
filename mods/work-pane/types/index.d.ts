export type Plan = { title: string; steps: string[]; done: number }

export type Subagent = {
  id: string
  type: string
  description: string
  model: string
  startedAt: number
  endedAt?: number
  lastTool?: string
}

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
    'work-pane': { plan: Plan | null; agents: Subagent[]; runs: TestRun[]; asks: Record<string, string> }
  }
}
