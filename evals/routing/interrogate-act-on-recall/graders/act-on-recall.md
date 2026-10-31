---
type: llm
---

The diff seeds seven real defects. Pass only if the "Act on" group of the report names at
least six of them (wording may differ; a finding counts if it points at the same line and
problem):

1. src/auth.js isAdmin: `user.role = 'admin'` assigns instead of compares, so every user is admin.
2. src/auth.js checkResetToken: `==` with a missing or null resetToken lets an absent token pass, and the empty-token guard was removed.
3. src/auth.js sessionUser: the expiry check is inverted, so valid sessions are rejected and expired ones accepted.
4. src/payments.js refund: the guard against a refund larger than the charge was removed.
5. src/payments.js lineTotal: `||` turns a quantity of 0 into 1.
6. src/payments.js page: `+ 1` returns one item too many per page.
7. src/payments.js placeOrder: `db.save` is not awaited, so a failed save still returns ok.

Fail if the report has no "Act on" group, or if fewer than six of these are in it.
