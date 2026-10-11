#!/usr/bin/env python3
"""Re-runnable check of check_tree.py: each case bends a good tree one way and asserts on the problems."""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_tree import check  # noqa: E402

GOOD = {
    "product": {
        "status": "Confirmed",
        "worth_it": "build: shop owners lose domains monthly; two weeks to a first version",
        "features": [
            {"id": "F1", "title": "Buy", "project": "Checkout"},
            {"id": "F2", "title": "Sell", "project": None, "deferred": True},
        ],
    },
    "projects": [{
        "name": "Checkout", "feature": "F1", "spec_status": "Confirmed",
        "out_of_scope": ["Payment plans"], "open_questions": [],
        "requirements": [{"id": "R1", "text": "a"}, {"id": "R2", "text": "b"}],
        "items": [
            {"id": "A", "kind": "build", "requirements": ["R1"], "you_see": "cart", "done_when": 3, "chars": 900},
            {"id": "B", "kind": "build", "requirements": ["R2"], "you_see": "error", "done_when": 4, "chars": 1200},
        ],
    }],
}

passed = failed = 0


def case(name, bend, want, launch=False):
    global passed, failed
    tree = copy.deepcopy(GOOD)
    bend(tree)
    problems, _ = check(tree, launch)
    text = "\n".join(problems)
    ok = (not problems) if want is None else want in text
    if ok:
        passed += 1
        print(f"ok   {name}")
    else:
        failed += 1
        print(f"FAIL {name}: {problems or 'no problems'}")


P = lambda t: t["projects"][0]  # noqa: E731
I = lambda t, n=0: P(t)["items"][n]  # noqa: E731


def setp(**kw):
    return lambda t: P(t).update(kw)


def seti(**kw):
    return lambda t: I(t).update(kw)


case("a good tree passes", lambda t: None, None)
case("a feature not yet shaped is only a note",
     lambda t: t["product"]["features"][1].update(deferred=False), None)
case("a project its feature does not name fails",
     lambda t: t["product"]["features"][0].update(project="Cart"), "does not name it")
case("a Confirmed product with Worth it blank fails",
     lambda t: t["product"].update(worth_it=""), "Worth it blank")
case("a project serving no feature fails", setp(feature="F9"), "serves no feature")
case("a Confirmed spec under a Draft product fails",
     lambda t: t["product"].update(status="Draft"), "under a Draft product")
case("a project may stand alone without a product", lambda t: t.pop("product"), None)
case("an empty Out of scope on a Confirmed spec fails", setp(out_of_scope=[]), "empty Out of scope")
case("open questions on a Confirmed spec fail", setp(open_questions=["who pays?"]), "open questions")
case("a build item under a Draft spec fails",
     setp(spec_status="Draft"), "under a Draft spec")
case("a prototype item under a Draft spec passes",
     lambda t: P(t).update(spec_status="Draft", items=[{"id": "M", "kind": "prototype"}]), None)
case("an item citing nothing fails", seti(requirements=[]), "cites no requirement")
case("a chore may cite nothing", seti(kind="chore", requirements=[], you_see=""), None)
case("an item citing a missing requirement fails", seti(requirements=["R7"]), "cites R7")
case("an item citing a dropped requirement fails",
     lambda t: P(t)["requirements"][0].update(dropped=True), "R1, which was dropped")
case("a build item without a you-see line fails", seti(you_see=" "), "no 'you see'")
case("six Done When checks fail", seti(done_when=6), "split it")
case("an over-long body fails", seti(chars=1600), "1600 characters")
case("an unsliced requirement is only a note before Launch",
     lambda t: P(t)["items"].pop(), None)
case("an unsliced requirement fails at Launch",
     lambda t: P(t)["items"].pop(), "no item yet for R2", launch=True)
case("a deferred requirement passes at Launch",
     lambda t: (P(t)["items"].pop(), P(t)["requirements"][1].update(deferred=True)), None, launch=True)

print(f"{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
