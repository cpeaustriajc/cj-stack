import type { Register } from 'claude-code'

const MOD = 'git-guard'

const DENY = {
  branch:
    `${MOD}: \`git branch -D\` deletes a branch even when no other branch holds its commits. ` +
    'Use `git branch -d <branch>`: it deletes only a merged branch. If git refuses, ask the user before you force it.',
  push:
    `${MOD}: a force push to main or master rewrites shared history. ` +
    'Push to your own branch and open a pull request, or undo a commit on main with `git revert <sha>` and a normal push.',
  discard:
    `${MOD}: this discards the uncommitted changes in every tracked file. ` +
    'Save them first with `git stash push -u -m <tag>` or a WIP commit, or name only the files to restore.',
}

const FAIL_WAY_OUT = 'Name the branch and the files in the git command, or ask the user.'

// Quoted text becomes Q, so a quoted word is never read as a flag, a branch or a path.
const Q = '\u0000'
const PREFIX = new Set(['!', 'if', 'then', 'do', 'else', 'elif', 'while', 'until', '{', 'time', 'exec', 'command', 'builtin', 'nohup', 'sudo', 'doas', 'env', 'nice'])
const GIT_OPT_WITH_ARG = new Set(['-C', '-c', '--git-dir', '--work-tree', '--namespace', '--config-env', '--super-prefix'])
const PUSH_OPT_WITH_ARG = new Set(['--repo', '-o', '--push-option', '--receive-pack', '--exec'])
const MAIN = new Set(['main', 'master'])
const WHOLE_TREE = new Set(['.', './', ':/', ':/.', ':', '*'])

type Frame = { segs: Seg[] }
type Seg = { text: string; frame: Frame }
type Where = { steps: string[]; unknown: boolean }
type Probe = { kind: 'branch' } | { kind: 'push'; current?: Where } | { kind: 'discard'; where: Where }

function scan(input: string): Frame[] {
  const frames: Frame[] = []
  const open = (): Frame => {
    const frame: Frame = { segs: [] }
    frames.push(frame)
    return frame
  }
  const stack: { frame: Frame; kind: 'top' | 'sub' | 'grp' | 'bt' | 'dq' | 'sq' }[] = [{ frame: open(), kind: 'top' }]
  const begin = (frame: Frame) => frame.segs.push({ text: '', frame })
  const cur = () => {
    const frame = stack[stack.length - 1].frame
    if (!frame.segs.length) begin(frame)
    return frame.segs[frame.segs.length - 1]
  }
  const split = () => begin(stack[stack.length - 1].frame)
  const enter = (kind: 'sub' | 'grp' | 'bt') => {
    const frame = kind === 'grp' ? stack[stack.length - 1].frame : open()
    stack.push({ frame, kind })
    split()
  }

  for (let i = 0; i < input.length; i++) {
    const c = input[i]
    const top = stack[stack.length - 1].kind
    const next = input[i + 1]
    if (top === 'sq') {
      if (c === "'") stack.pop()
      cur().text += Q
    } else if (top === 'dq') {
      if (c === '\\') {
        cur().text += Q + Q
        i++
      } else if (c === '"') {
        stack.pop()
        cur().text += Q
      } else if (c === '$' && next === '(') {
        enter('sub')
        i++
      } else if (c === '`') {
        enter('bt')
      } else cur().text += Q
    } else if (c === '\\') {
      cur().text += next === '\n' ? ' ' : Q + Q
      i++
    } else if (c === "'") {
      stack.push({ frame: stack[stack.length - 1].frame, kind: 'sq' })
      cur().text += Q
    } else if (c === '"') {
      stack.push({ frame: stack[stack.length - 1].frame, kind: 'dq' })
      cur().text += Q
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
      split()
    } else if ((c === '|' || c === '&') && next === c) {
      split()
      i++
    } else if (c === '&' && input[i - 1] === '>') {
      cur().text += c
    } else if (c === '|' || c === ';' || c === '&' || c === '\n') {
      split()
    } else {
      cur().text += c
    }
  }
  return frames
}

function words(seg: Seg): string[] {
  const all = seg.text.split(/\s+/).filter(Boolean)
  let i = 0
  while (i < all.length) {
    const base = all[i].replace(/^.*\//, '')
    if (!/^[A-Za-z_]\w*=/.test(all[i]) && !PREFIX.has(base)) break
    i++
    if (base === 'sudo' || base === 'doas') while (all[i]?.startsWith('-')) i += /^-[ughCT]$/.test(all[i]) ? 2 : 1
  }
  return all.slice(i)
}

const short = (w: string, letter: string) => /^-[A-Za-z]+$/.test(w) && w.includes(letter)

function branchDeletesForce(args: string[]): boolean {
  if (args.some(w => short(w, 'D'))) return true
  const del = args.some(w => w === '--delete' || short(w, 'd'))
  const force = args.some(w => w === '--force' || short(w, 'f'))
  return del && force
}

function destination(refspec: string): string {
  const spec = refspec.replace(/^\+/, '')
  const dest = spec.includes(':') ? spec.slice(spec.indexOf(':') + 1) : spec
  return dest.replace(/^refs\/heads\//, '')
}

function pushProbe(args: string[], where: Where): Probe | undefined {
  let force = false
  const positional: string[] = []
  for (let i = 0; i < args.length; i++) {
    const w = args[i]
    if (w === '--force' || w.startsWith('--force-with-lease') || short(w, 'f')) force = true
    else if (PUSH_OPT_WITH_ARG.has(w)) i++
    else if (!w.startsWith('-')) positional.push(w)
  }
  const refspecs = positional.slice(1)
  if (!refspecs.length) return force ? { kind: 'push', current: where } : undefined
  for (const spec of refspecs) {
    if (!force && !spec.startsWith('+')) continue
    const dest = destination(spec)
    if (MAIN.has(dest)) return { kind: 'push' }
    if (dest === 'HEAD') return { kind: 'push', current: where }
  }
  return undefined
}

function discards(sub: string, args: string[]): boolean {
  const dash = args.indexOf('--')
  const paths = dash >= 0 ? args.slice(dash + 1) : args.filter(w => !w.startsWith('-'))
  if (!paths.some(p => WHOLE_TREE.has(p))) return false
  if (sub === 'checkout') return true
  const staged = args.some(w => w === '--staged' || short(w, 'S'))
  const worktree = args.some(w => w === '--worktree' || short(w, 'W'))
  return worktree || !staged
}

function moved(where: Where, path: string | undefined): Where {
  if (!path || path.includes(Q) || path.startsWith('~') || path === '-') return { steps: where.steps, unknown: true }
  return { steps: [...where.steps, path], unknown: where.unknown }
}

function probes(input: string): Probe[] {
  const found: Probe[] = []
  for (const frame of scan(input)) {
    let where: Where = { steps: [], unknown: false }
    for (const seg of frame.segs) {
      const w = words(seg)
      const name = w[0]?.replace(/^.*\//, '')
      if (name === 'cd') where = moved(where, w[1])
      if (name !== 'git') continue
      let here = where
      let i = 1
      while (w[i]?.startsWith('-')) {
        const opt = w[i].split('=')[0]
        if (opt === '-C') here = moved(here, w[i + 1])
        i += GIT_OPT_WITH_ARG.has(opt) && !w[i].includes('=') ? 2 : 1
      }
      const sub = w[i]
      const args = w.slice(i + 1)
      if (sub === 'branch' && branchDeletesForce(args)) found.push({ kind: 'branch' })
      if (sub === 'push') {
        const p = pushProbe(args, here)
        if (p) found.push(p)
      }
      if ((sub === 'checkout' || sub === 'restore') && discards(sub, args)) found.push({ kind: 'discard', where: here })
    }
  }
  return found
}

export const register: Register = on => {
  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    const found = probes(e.command)
    if (!found.length) return next(e)
    let base: string | undefined
    const dir = async (where: Where) => {
      base ??= await $.session.cwd()
      return where.steps.reduce((d, s) => (s.startsWith('/') ? s : `${d}/${s}`), base)
    }
    for (const p of found) {
      if (p.kind === 'branch') return { deny: DENY.branch }
      if (p.kind === 'push') {
        if (!p.current || p.current.unknown) return { deny: DENY.push }
        const r = await $.process.run(['git', 'symbolic-ref', '--short', '-q', 'HEAD'], { cwd: await dir(p.current) })
        if (r.exitCode === 0 && MAIN.has(r.stdout.trim())) return { deny: DENY.push }
      }
      if (p.kind === 'discard') {
        if (p.where.unknown) return { deny: DENY.discard }
        const r = await $.process.run(['git', 'status', '--porcelain', '--untracked-files=no'], { cwd: await dir(p.where) })
        if (r.exitCode !== 0) throw new Error(`git status exited ${r.exitCode}`)
        if (r.stdout.trim()) return { deny: DENY.discard }
      }
    }
    return next(e)
  }).catch(($, e, next) =>
    next.called ? next(e) : { deny: `${MOD}: could not check this command (${next.error.message}). ${FAIL_WAY_OUT}` },
  )
}
