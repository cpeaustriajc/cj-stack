import { expect, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On } from 'claude-code'

const LINEAR = 'mcp__linear-server__'
const DOC = 'c089f90f-4944-4052-9616-e8fdc66839f3'
const SURFACES = ['terminal', 'desktop'] as const

const engineSaw: string[] = []

let mounts = 0

function engine(on: On) {
  on('session.surfaces', () => ({ value: ['terminal'] }) as never)
  on('ui.render', { component: 'AskUserQuestion' }, ($, e) => {
    engineSaw.push((e.props.questions as { question: string }[])[0].question)
    return { type: 'engine', ref: 0 } as never
  })
}

type Drawn = { text: string; props: { color?: string; bold?: boolean } }[]

function gate($: Engine, on: On, surface: (typeof SURFACES)[number], answer = 'Leave it') {
  const seen: { asked: string; texts: Drawn }[] = []
  on('mcp.call', () => ({ value: { content: [{ type: 'text', text: '{"title":"Decision: Cart"}' }], isError: false } }) as never)
  on('tool.call', async (_, e) => {
    if (e.tool !== 'AskUserQuestion') return { result: 'ok' } as never
    const questions = (e as { questions: { question: string }[] }).questions
    const drawn = await $.ui.mount({
      plugin: 'work-pane', surface, component: 'AskUserQuestion', requestId: `q${++mounts}`,
      props: { tool: 'AskUserQuestion', questions } as never,
    })
    seen.push({ asked: questions[0].question, texts: (await drawn.findAll({ type: 'Text' })) as Drawn })
    return { result: { questions, answers: { [engineSaw.at(-1)!]: answer } } } as never
  })
  return seen
}

const swap = {
  tool: `${LINEAR}save_document`, id: DOC,
  patch: [{ op: 'replace', old_string: 'CJ asked to remove the cart button when the user is not signed in; the header gates both carts.', new_string: 'CJ asked to remove the cart button when the user is not signed in. On both desktop and mobile.' }],
}

for (const surface of SURFACES) {
  test(`${surface}: removed rows draw red and added rows draw green`, async ($, on) => {
    engine(on)
    const seen = gate($, on, surface)
    await $.tool.call(swap as never)
    const { texts } = seen[0]
    const color = (start: string) => texts.find(t => t.text.startsWith(start))?.props.color
    expect(color('  − CJ')).toBe('red')
    expect(color('  + CJ')).toBe('green')
  })

  test(`${surface}: the dialog gets the question exactly as asked, so a typed note comes back`, async ($, on) => {
    engine(on)
    const seen = gate($, on, surface, 'remove the locked-decisions reference')
    const out = await $.tool.call(swap as never)
    expect(engineSaw.at(-1)).toBe(seen[0].asked)
    expect(seen[0].asked).toBe('Update document "Decision: Cart" — apply this change?')
    expect(out.deny).toMatch(/Their note: remove the locked-decisions reference/)
  })

  test(`${surface}: an approval comes back too`, async ($, on) => {
    engine(on)
    gate($, on, surface, 'Update document "Decision: Cart"')
    const out = await $.tool.call(swap as never)
    expect(out.deny).toBe(undefined)
  })

  test(`${surface}: a delete shows its warning in yellow`, async ($, on) => {
    engine(on)
    const seen = gate($, on, surface)
    await $.tool.call({ tool: `${LINEAR}delete_comment`, id: 'c1' } as never)
    expect(seen[0].texts.find(t => t.text.startsWith('⚠'))?.props.color).toBe('yellow')
  })

  test(`${surface}: another dialog is left alone`, async ($, on) => {
    engine(on)
    const drawn = await $.ui.mount({
      plugin: 'work-pane', surface, component: 'AskUserQuestion', requestId: `q${++mounts}`,
      props: { tool: 'AskUserQuestion', questions: [{ question: 'Pick one?', header: 'Linear', multiSelect: false, options: [{ label: 'A', description: '' }, { label: 'B', description: '' }] }] } as never,
    })
    expect(((await drawn.findAll({ type: 'Text' })) as Drawn).length).toBe(0)
  })
}

function world(on: On, lookup: 'title' | 'error' | 'throw' | 'garbage' | 'hang') {
  const asked: { question: string; options: string[] }[] = []
  const looked: string[] = []
  on('session.surfaces', () => ({ value: ['terminal'] }) as never)
  on('mcp.call', ($, e) => {
    looked.push(`${e.server}/${e.tool}/${String(e.args.id)}`)
    if (lookup === 'throw') throw new Error('offline')
    if (lookup === 'hang') return new Promise(() => {}) as never
    const text = lookup === 'garbage' ? 'not json' : JSON.stringify({ id: DOC, title: 'Decision: Cart' })
    return { value: { content: [{ type: 'text', text }], isError: lookup === 'error' } } as never
  })
  on('tool.call', ($, e) => {
    if (e.tool === 'AskUserQuestion') {
      const q = (e as { questions: { question: string; options: { label: string }[] }[] }).questions[0]
      asked.push({ question: q.question, options: q.options.map(o => o.label) })
      return { result: { questions: (e as { questions: unknown[] }).questions, answers: { [q.question]: 'Leave it' } } } as never
    }
    return { result: 'ok' } as never
  })
  return { asked, looked }
}

const edit = { tool: `${LINEAR}save_document`, id: DOC, patch: [{ op: 'append', text: 'x' }] }

test('a document edit names the document by its title', async ($, on) => {
  const w = world(on, 'title')
  const out = await $.tool.call(edit as never)
  expect(w.looked).toEqual([`linear-server/get_document/${DOC}`])
  expect(w.asked[0].question.split('\n')[0].replace(/ — apply this change\?$/, '')).toBe('Update document "Decision: Cart"')
  expect(w.asked[0].options[0]).toBe('Update document "Decision: Cart"')
  expect(out.deny).toMatch(/Decision: Cart/)
})

for (const lookup of ['error', 'throw', 'garbage', 'hang'] as const) {
  test(`a failed title lookup (${lookup}) falls back to the short id`, async ($, on) => {
    if (lookup === 'hang') on('clock.sleep', () => ({ value: undefined }) as never)
    const w = world(on, lookup)
    await $.tool.call(edit as never)
    expect(w.asked[0].question.split('\n')[0].replace(/ — apply this change\?$/, '')).toBe('Update document c089f90f…')
  })
}

test('a new document makes no lookup', async ($, on) => {
  const w = world(on, 'title')
  await $.tool.call({ tool: `${LINEAR}save_document`, title: 'New', project: 'P' } as never)
  expect(w.looked).toEqual([])
})

test('a long title gives a short button without a cut-off phrase', async ($, on) => {
  on('session.surfaces', () => ({ value: ['terminal'] }) as never)
  on('mcp.call', () => ({ value: { content: [{ type: 'text', text: JSON.stringify({ title: 'Decision: Checkout for Afternic and other partners' }) }], isError: false } }) as never)
  const labels: string[] = []
  on('tool.call', ($, e) => {
    const q = (e as { questions?: { question: string; options: { label: string }[] }[] }).questions?.[0]
    if (!q) return { result: 'ok' } as never
    labels.push(q.options[0].label)
    return { result: { questions: [q], answers: { [q.question]: 'Leave it' } } } as never
  })
  await $.tool.call(edit as never)
  expect(labels[0].length).toBeLessThanOrEqual(40)
  expect(labels[0]).toMatch(/^Update document "Decision: Checkout for.*…$/)
})
