---
type: llm
---

The diff removes the unknown-coupon guard in `src/cart.js` `applyCoupon`. `findCoupon` in
`src/coupons.js` returns `undefined` for a code that is not in `COUPONS`, so
`applyCoupon(cart, 'NOPE')` throws a TypeError on `coupon.percent`.

Pass only if all hold:

1. The report has a group titled "Act on" (those words; "Blocking" or "Must fix" do not count),
   and every finding in the report is labelled with one of these proof levels, by name:
   stated, pointed at the line, walked through, run.
2. The "Act on" group names this defect, labelled walked through or run.
3. The report shows the path or the repro behind it: an unknown code, `findCoupon` returning
   `undefined`, and the read of `coupon.percent` that throws.
