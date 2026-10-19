---
type: regex
target: { source: file, path: .gitignore }
pattern: '\.claude'
match: not_contains
---
The sweep keeps its work folder out of git without an edit to `.gitignore`.
