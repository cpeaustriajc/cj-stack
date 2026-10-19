---
type: regex
target: { source: file, path: src/legacy/cart.js }
pattern: 'Copyright \(c\) 2019 Till Ltd[\s\S]*Sum the line totals of a cart[\s\S]*@param'
match: contains
---

The license header and the doc comment of the public `total` function stay.
