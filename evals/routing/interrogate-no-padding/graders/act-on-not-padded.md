---
type: llm
---

The diff introduces two real defects in src/payments.js:

A. `refund` uses `>=`, so a full refund (amount equal to the charge) throws. A direct
   consequence: `partialRefunds` throws on the installment that uses up the balance.
B. `partialRefunds` accepts negative amounts: a negative entry raises the running balance, so the
   total refunded can exceed the charge, and the `> 0` filter hides the negative entry.

Pass only if both hold:

1. The "Act on" group names defect A.
2. Every other "Act on" item is defect B or the direct consequence of A. Style, naming,
   readability, error-message wording alone, the new `refundedAt` field, missing tests,
   atomicity worries or pre-existing behaviour in Act on count as padding.

Fail if the report has no "Act on" group.
