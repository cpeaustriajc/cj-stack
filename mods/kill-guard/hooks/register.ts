import type { Register } from 'claude-code'

const MOD = 'kill-guard'

const WAY_OUT =
  'Kill the PID you saved (`$!` or a pid file), or check the PID\'s working directory is inside this worktree ' +
  '(`lsof -a -p <pid> -d cwd` or `ps -o command= -p <pid>`) and kill that PID.'

const DENY_TEXT = `${MOD}: a kill by name or port can stop another checkout's process. ${WAY_OUT}`

const FINDERS = new Set(['lsof', 'pgrep', 'pidof', 'ps', 'ss', 'netstat', 'fuser'])
const KILL_BY_NAME = new Set(['pkill', 'killall'])
const PREFIX = new Set(['!', 'if', 'then', 'do', 'else', 'elif', 'while', 'until', '{', 'time', 'exec', 'command', 'builtin', 'nohup', 'sudo', 'doas', 'env', 'nice'])
const XARGS_WITH_ARG = new Set(['-I', '-n', '-P', '-L', '-d', '-E', '-s', '-a'])

type Frame = { parent?: Seg; segs: Seg[] }
type Seg = { text: string; piped: boolean; frame: Frame; words?: string[]; via?: string }

function scan(input: string): Frame[] {
  const frames: Frame[] = []
  const open = (parent?: Seg): Frame => {
    const frame: Frame = { parent, segs: [] }
    frames.push(frame)
    return frame
  }
  const stack: { frame: Frame; kind: 'top' | 'sub' | 'grp' | 'bt' | 'dq' | 'sq' }[] = [{ frame: open(), kind: 'top' }]
  const begin = (frame: Frame, piped: boolean) => frame.segs.push({ text: '', piped, frame })
  const cur = () => {
    const frame = stack[stack.length - 1].frame
    if (!frame.segs.length) begin(frame, false)
    return frame.segs[frame.segs.length - 1]
  }
  const split = (piped: boolean) => begin(stack[stack.length - 1].frame, piped)
  const enter = (kind: 'sub' | 'grp' | 'bt') => {
    const parent = kind === 'grp' ? undefined : cur()
    const frame = kind === 'grp' ? stack[stack.length - 1].frame : open(parent)
    stack.push({ frame, kind })
    split(false)
  }

  for (let i = 0; i < input.length; i++) {
    const c = input[i]
    const top = stack[stack.length - 1].kind
    const next = input[i + 1]
    if (top === 'sq') {
      if (c === "'") stack.pop()
      cur().text += '_'
    } else if (top === 'dq') {
      if (c === '\\') {
        cur().text += '__'
        i++
      } else if (c === '"') {
        stack.pop()
        cur().text += '_'
      } else if (c === '$' && next === '(') {
        enter('sub')
        i++
      } else if (c === '`') {
        enter('bt')
      } else cur().text += '_'
    } else if (c === '\\') {
      cur().text += next === '\n' ? ' ' : '__'
      i++
    } else if (c === "'") {
      stack.push({ frame: stack[stack.length - 1].frame, kind: 'sq' })
      cur().text += '_'
    } else if (c === '"') {
      stack.push({ frame: stack[stack.length - 1].frame, kind: 'dq' })
      cur().text += '_'
    } else if (c === '#' && (i === 0 || /\s/.test(input[i - 1]))) {
      while (i + 1 < input.length && input[i + 1] !== '\n') i++
    } else if (c === '$' && next === '(') {
      enter('sub')
      i++
    } else if (c === '`') {
      if (top === 'bt') {
        stack.pop()
        cur()
      } else enter('bt')
    } else if (c === '(') {
      enter('grp')
    } else if (c === ')') {
      if (top === 'sub' || top === 'grp') stack.pop()
      split(false)
    } else if (c === '|' && next === '|') {
      split(false)
      i++
    } else if (c === '|') {
      split(true)
    } else if (c === '&' && next === '&') {
      split(false)
      i++
    } else if (c === '&' && input[i - 1] === '>') {
      cur().text += c
    } else if (c === ';' || c === '&' || c === '\n') {
      split(false)
    } else {
      cur().text += c
    }
  }
  return frames
}

function command(seg: Seg): string | undefined {
  const words = seg.text.split(/\s+/).filter(Boolean)
  let i = 0
  while (i < words.length) {
    const w = words[i]
    const base = w.replace(/^.*\//, '')
    if (/^[A-Za-z_]\w*=/.test(w) || PREFIX.has(base)) {
      i++
      if (base === 'sudo' || base === 'doas') while (words[i]?.startsWith('-')) i += /^-[ughCT]$/.test(words[i]) ? 2 : 1
    } else if (base === 'xargs') {
      seg.via = 'xargs'
      i++
      while (words[i]?.startsWith('-')) i += XARGS_WITH_ARG.has(words[i]) ? 2 : 1
    } else break
  }
  seg.words = words.slice(i)
  return seg.words[0]?.replace(/^.*\//, '')
}

function judge(input: string): boolean {
  const frames = scan(input)
  for (const frame of frames) {
    let pipeline: Seg[] = []
    for (const seg of frame.segs) {
      pipeline = seg.piped ? [...pipeline, seg] : [seg]
      const name = command(seg)
      if (!name) continue
      if (KILL_BY_NAME.has(name)) return true
      if (name === 'fuser' && seg.words!.slice(1).some(w => /^-[A-Za-z]*k/.test(w))) return true
      if (name === 'kill' && seg.via === 'xargs' && pipeline.slice(0, -1).some(p => FINDERS.has(command(p) ?? ''))) return true
    }
    const parent = frame.parent && command(frame.parent)
    if (parent === 'kill' && frame.segs.some(s => FINDERS.has(command(s) ?? ''))) return true
  }
  return false
}

export const register: Register = on => {
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    return judge(e.command) ? { deny: DENY_TEXT } : next(e)
  }).catch(($, e, next) =>
    next.called ? next(e) : { deny: `${MOD}: could not check this command (${next.error.message}). ${WAY_OUT}` },
  )
}
