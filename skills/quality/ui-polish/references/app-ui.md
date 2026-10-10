# App UI rules

For dashboards, admin, settings and other dense screens. Check each rule against the change. A row in the report names the rule it breaks.

**Spacing and depth**
- One spacing base, 4 or 8px, with multiples only. Flag off-grid values such as 14px.
- One depth strategy per product, borders or shadows, and not both on the same surface.
- Density is decided up front, for example a named control height of 32px dense or 40px roomy, and applied everywhere.

**Radius**
- A small, medium and large scale: inputs and buttons, cards, modals.
- Nested radius is concentric: outer radius = inner radius + padding.
- A child's radius is never larger than its parent's.

**Shadows**
- Layered, and tinted rather than pure black.
- One light direction across the product.
- Offset and blur grow with elevation.
- A layered shadow is never animated.
- In dark mode, use a faint light ring instead of a shadow.

**Colour**
- Colour signals state. Grey carries structure.

**Numbers**
- `tabular-nums` on numbers that change or sit in columns.
- Dates, numbers and currency go through `Intl`.
- Non-breaking spaces in "10 MB" and "⌘ K".

**Text**
- `text-wrap: balance` on headings and `pretty` on paragraphs.
- `…` instead of `...`.
- Flex children that truncate carry `min-width: 0`.
- Button labels are specific: "Save changes", not "Continue".

**Images and lists**
- Images have width and height, so nothing shifts as they load.
- A faint inner outline separates an image from its background.
- Lists over about 50 items are virtualized.

Sources: https://vercel.com/design/guidelines, https://jakub.kr/writing/details-that-make-interfaces-feel-better, https://www.joshwcomeau.com/css/designing-shadows/, https://github.com/Dammyjay93/interface-design
