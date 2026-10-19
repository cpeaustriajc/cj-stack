const DAY = 86_400_000
const MIN_ELAPSED = 12 * 3_600_000
const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

export function formatTime(ms: number): string {
  const d = new Date(ms)
  const h = d.getHours()
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${WEEKDAYS[d.getDay()]} ${h % 12 || 12}:${mm} ${h < 12 ? 'AM' : 'PM'}`
}

export function weeklyStatus(used: number, resetsAt: string | undefined, now: number): string | undefined {
  const resetMs = resetsAt === undefined ? Number.NaN : Date.parse(resetsAt)
  if (Number.isNaN(resetMs) || resetMs <= now) return undefined

  const head = `Week ${Math.round(used)}%`
  const resets = `${head} · resets ${formatTime(resetMs)}`
  const start = resetMs - 7 * DAY
  const elapsed = now - start
  if (used >= 100 || used === 0 || elapsed < MIN_ELAPSED) return resets

  const perDay = Math.round((100 - used) / ((resetMs - now) / DAY))
  const outAt = start + (elapsed * 100) / used
  return outAt >= resetMs
    ? `${head} · lasts to ${formatTime(resetMs)} · ${perDay}%/day left`
    : `${head} · out ~${formatTime(outAt)} · ${perDay}%/day left`
}
