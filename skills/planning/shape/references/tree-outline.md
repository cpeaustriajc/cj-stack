# Tree outline

`scripts/check_tree.py` checks the plan as a tracker-neutral outline, never the tracker itself.
Read the tree back after writing and save it as JSON in a scratch file. Include only the levels
the run touched: a `shape` run may omit `product` when the project stands alone, and a `tickets`
run includes its project and that project's items.

```json
{
  "product": {
    "name": "Domain marketplace",
    "status": "Confirmed",
    "worth_it": "build: buyers abandon at register today; about three weeks to a first version",
    "features": [
      { "id": "F1", "title": "Buy a domain", "project": "Checkout" },
      { "id": "F2", "title": "Sell a domain", "project": null, "deferred": true }
    ]
  },
  "projects": [
    {
      "name": "Checkout",
      "feature": "F1",
      "spec_status": "Confirmed",
      "out_of_scope": ["Payment plans"],
      "open_questions": [],
      "requirements": [
        { "id": "R1", "text": "A logged-out visitor clicks Buy and lands on register with the domain still in the cart." },
        { "id": "R2", "text": "...", "dropped": true }
      ],
      "items": [
        {
          "id": "MP-12",
          "title": "Logged-out buyer keeps the cart through register",
          "kind": "build",
          "requirements": ["R1"],
          "you_see": "The register page with the domain listed in the cart.",
          "done_when": 3,
          "chars": 1180,
          "blocked_by": []
        }
      ]
    }
  ]
}
```

- `status` and `spec_status`: `Draft` or `Confirmed`.
- `project`: the project's name, or `null` while the feature waits its turn (listed as not yet
  shaped); `deferred: true` marks a feature or requirement consciously left out of this round.
- `kind`: `build`, `bug`, `chore` or `prototype`. A prototype item may sit under a Draft spec and
  cites no requirement.
- `done_when`: the number of Done When checks; `chars`: the whole body's length. The check
  subtracts the quoted lines of the cited requirements, computed from their `text`, before it
  compares against 1,500.

Run it as `top-down.md` says; add `--launch` when the project is entering Launch, so a
requirement with no item fails instead of being listed as not yet sliced.
