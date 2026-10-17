---
type: llm
focus:
  source: file
  path: test_checkout.py
---

This is the final test_checkout.py. checkout.py calls `gateway.charge_card(amount)`, and
SPEC.md says: the total is the subtotal plus 8% tax, rounded to whole cents; an empty cart never
charges the card; a cart with items charges the card once, with the total.

The original file had three weak tests:

A. `test_total` computed its expected value with the code under test (`_round_cents`,
   `subtotal`, `TAX_RATE`), so it passed for any tax maths.
B. `test_total_rounds` asserted a call to the private `_round_cents`.
C. `test_empty_cart_never_charges` asserted that `gateway.charge` was not called, a method the
   code never calls, so it could never fail.

Pass only if all hold:

1. Each total assertion compares with a literal number, such as 2160 for 2 x 1000 cents, not
   with a value computed by `_round_cents`, `subtotal` or `TAX_RATE`.
2. No test patches, mocks or asserts a call to `_round_cents`.
3. The empty-cart test asserts that `charge_card` was not called, or that the gateway got no
   calls at all (such as `mock_calls == []` or `method_calls == []`), or a test in the file shows
   that the same kind of mock records a `charge_card` call for a cart with items.
