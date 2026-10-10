import { expect, test } from 'claude-code/testing'
import { modeSuggestions } from './suggest'

const names = (rows: { text: string }[]) => rows.map(r => r.text)

test('/mode with a space lists all four modes in order', () => {
  expect(names(modeSuggestions('/mode ', 6, 'audit'))).toEqual(['audit', 'no-pr', 'chat', 'off'])
})

test('a partial mode name lists only the modes it starts', () => {
  expect(names(modeSuggestions('/mode n', 7, 'off'))).toEqual(['no-pr'])
  expect(names(modeSuggestions('/mode c', 7, 'off'))).toEqual(['chat'])
})

test('a partial name that starts no mode lists nothing', () => {
  expect(modeSuggestions('/mode x', 7, 'off')).toEqual([])
})

test('the current mode is marked on its dim line', () => {
  const rows = modeSuggestions('/mode ', 6, 'chat')
  expect(rows.map(r => r.description)).toEqual([
    'read and report only',
    'no pull requests',
    'answer here, no PR or push (on)',
    'lift the current mode',
  ])
})

test('with no mode on, the off row says so instead of being marked on', () => {
  const rows = modeSuggestions('/mode o', 7, 'off')
  expect(rows.map(r => r.description)).toEqual(['no mode is on'])
})

test('a finished mode name with arguments after it lists nothing', () => {
  expect(modeSuggestions('/mode audit extra', 17, 'off')).toEqual([])
})

test('a caret before the end of the draft lists nothing', () => {
  expect(modeSuggestions('/mode n', 6, 'off')).toEqual([])
})

test('other drafts list nothing', () => {
  expect(modeSuggestions('/help ', 6, 'off')).toEqual([])
  expect(modeSuggestions('/mode', 5, 'off')).toEqual([])
  expect(modeSuggestions('say /mode ', 11, 'off')).toEqual([])
})
