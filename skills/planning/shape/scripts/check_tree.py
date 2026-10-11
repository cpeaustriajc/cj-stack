#!/usr/bin/env python3
"""Check a vision -> shape -> tickets plan tree, given as the outline in references/tree-outline.md.

Prints one line per problem and exits 1 if any; requirements not yet sliced are listed, not failed,
unless --launch is passed.
"""
import json
import sys

MAX_CHARS = 1500
DONE_WHEN = range(1, 6)


def check(tree, launch=False):
    problems, notes = [], []
    product = tree.get("product")
    features = {}
    if product:
        features = {f["id"]: f for f in product.get("features", [])}
        waiting = [f["id"] for f in features.values() if not f.get("project") and not f.get("deferred")]
        if waiting:
            notes.append(f"product: not yet shaped: {', '.join(waiting)}")
        named = {f.get("project") for f in features.values()}

    for p in tree.get("projects", []):
        name = p.get("name", "?")
        where = f"project {name}"
        feature = p.get("feature")
        if product:
            if feature not in features:
                problems.append(f"{where}: serves no feature of the product (feature: {feature})")
            elif name not in named:
                problems.append(f"{where}: its feature {feature} does not name it as its project")
            if product.get("status") != "Confirmed" and p.get("spec_status") == "Confirmed":
                problems.append(f"{where}: spec is Confirmed under a Draft product")

        reqs = {r["id"]: r for r in p.get("requirements", [])}
        live = {k for k, r in reqs.items() if not r.get("dropped")}
        confirmed = p.get("spec_status") == "Confirmed"
        if confirmed:
            if not live:
                problems.append(f"{where}: Confirmed spec has no requirements")
            if not p.get("out_of_scope"):
                problems.append(f"{where}: Confirmed spec has an empty Out of scope")
            if p.get("open_questions"):
                problems.append(f"{where}: Confirmed spec still has open questions")

        covered = set()
        for item in p.get("items", []):
            iid = f"{where}, item {item.get('id', '?')}"
            kind = item.get("kind", "build")
            cited = item.get("requirements", [])
            if kind == "prototype":
                continue
            if not confirmed:
                problems.append(f"{iid}: a {kind} item under a Draft spec")
            if kind != "chore" and not cited:
                problems.append(f"{iid}: cites no requirement")
            for r in cited:
                if r not in reqs:
                    problems.append(f"{iid}: cites {r}, which the spec does not have")
                elif reqs[r].get("dropped"):
                    problems.append(f"{iid}: cites {r}, which was dropped")
            covered.update(cited)
            if kind in ("build", "bug") and not str(item.get("you_see", "")).strip():
                problems.append(f"{iid}: no 'you see' line")
            if item.get("done_when") is not None and item["done_when"] not in DONE_WHEN:
                problems.append(f"{iid}: {item['done_when']} Done When checks; at most 5, so split it")
            if item.get("chars", 0) > MAX_CHARS:
                problems.append(f"{iid}: body is {item['chars']} characters; over {MAX_CHARS}, so split it")

        open_reqs = sorted(r for r in live - covered if not reqs[r].get("deferred"))
        if confirmed and open_reqs:
            line = f"{where}: no item yet for {', '.join(open_reqs)}"
            (problems if launch else notes).append(line)

    return problems, notes


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print("usage: check_tree.py <outline.json> [--launch]", file=sys.stderr)
        return 2
    with open(args[0]) as f:
        tree = json.load(f)
    problems, notes = check(tree, launch="--launch" in argv)
    for line in problems:
        print(line)
    for line in notes:
        print(f"note: {line}")
    if not problems:
        print("tree ok")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
