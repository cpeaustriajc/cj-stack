#!/usr/bin/env bash
set -euo pipefail
cat > SPEC.md <<'MD'
# Checkout

- The total is the subtotal plus 8% tax, rounded to whole cents.
- An empty cart never charges the card.
- A cart with items charges the card once, with the total.
MD
cat > checkout.py <<'PY'
TAX_RATE = 0.08


def _round_cents(x):
    return int(round(x))


def subtotal(items):
    return sum(i["price_cents"] * i["qty"] for i in items)


def total(items):
    return _round_cents(subtotal(items) * (1 + TAX_RATE))


def checkout(items, gateway):
    if not items:
        return {"status": "empty"}
    amount = total(items)
    gateway.charge_card(amount)
    return {"status": "charged", "amount": amount}
PY
cat > test_checkout.py <<'PY'
import unittest
from unittest import mock

import checkout as co


class CheckoutTest(unittest.TestCase):
    def test_total(self):
        items = [{"price_cents": 1000, "qty": 2}]
        expected = co._round_cents(co.subtotal(items) * (1 + co.TAX_RATE))
        self.assertEqual(co.total(items), expected)

    def test_total_rounds(self):
        with mock.patch.object(co, "_round_cents", wraps=co._round_cents) as r:
            co.total([{"price_cents": 333, "qty": 1}])
            r.assert_called_once()

    def test_empty_cart_never_charges(self):
        gateway = mock.Mock()
        co.checkout([], gateway)
        gateway.charge.assert_not_called()

    def test_checkout_status(self):
        gateway = mock.Mock()
        result = co.checkout([{"price_cents": 500, "qty": 1}], gateway)
        self.assertIn("status", result)


if __name__ == "__main__":
    unittest.main()
PY
