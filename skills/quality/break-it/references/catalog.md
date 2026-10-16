# Worst-case catalog

Use this when the run seeds worst-case data. Pick the rows that match the fields the flow shows.

**Map the fields first**
- List every value the screen renders: field, where it comes from, its type, its limit, and
  whether it can be missing.
- Take each limit from the validation schema, the database column, the API type or the input's
  `maxLength`. Write "unbounded" where none exists. A front-end limit lower or higher than the
  back-end limit is a finding.
- Each test value is either realistic or the real limit. No random strings.
- Put the values in through the same seam as the demo data: fixture, mock, props or API stub.
  Never edit the markup to cause a break.

**Text**
- Names: very long and hyphenated, one or two letters, stacked diacritics, CJK with no spaces,
  RTL, emoji first, an emoji with a skin tone or ZWJ, extra spaces, missing.
- Initials and cut-offs count grapheme clusters (`Intl.Segmenter`), not `.length` or `.charAt`.
  A half emoji (`�`) is a bug.
- Unbreakable strings: a long email, a long URL, a UUID, a long file name, a long German compound.
- Markup and escapes (`<script>`, `&amp;`, `**bold**`) render as literal text.
- A newline in a one-line field, and a 2,000-character paste.

**Truncation, decided per field**
- Wrap what the user needs in full to identify an item, such as a name.
- Cut at the end only where the start carries the meaning, and give a way to see the full value.
- Cut in the middle where items differ at the end: file names, paths, hashes, emails on one domain.
- Never cut numbers, money, dates or anything the user compares.
- One rule for every field is a finding.

**Numbers**
- 0 and 1: "1 members" or "0 member" is a bug. Plurals come from `Intl.PluralRules`.
- Thousands separators, a million, a large currency total, a negative, `0.1 + 0.2`, above 100%.
- `null`, `undefined` or `NaN` shown as text.
- Another locale's separators, and a live value whose width jumps without `tabular-nums`.

**Collections**
- 0, 1, exactly one page, and one page + 1 (an empty page 2 or "40 of 40" is a bug).
- Thousands of items, one item far larger than the rest, and items with the same name.

**Time**
- Now ("0 seconds ago" is a bug), a future date, and the epoch `1970-01-01` shown as a real date.
- A time near midnight that falls on another day in UTC.
- Relative-time thresholds over days, months and years. A hand-built string where
  `Intl.RelativeTimeFormat` or `Intl.DateTimeFormat` belongs is fragile.

**Images**
- An avatar URL that returns 404 shows the fallback, not a broken-image icon.
- No avatar, a very wide or very tall image, a dark logo on dark mode, a slow image.

**States**
- Loading, an API error, partial data, every status in one list, no permission, the current user.

**Environment**
- 320px, a narrow sidebar column, 2560px wide, 200% zoom, dark mode, `dir="rtl"`, touch only.

**Afterwards**
- Keep the worst-case fixture as a regression test unless told otherwise. The toggle stays
  dev-only.

Sources: https://raw.githubusercontent.com/emilkowalski/skill/main/skills/break-ui/SKILL.md, https://raw.githubusercontent.com/emilkowalski/skill/main/skills/break-ui/CATALOG.md
