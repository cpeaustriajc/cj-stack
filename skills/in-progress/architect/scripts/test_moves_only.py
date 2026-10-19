#!/usr/bin/env python3
"""Re-runnable check of moves_only.py: each case builds a tiny repo, makes one change and asserts the verdict."""
import os
import subprocess
import sys
import tempfile

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "moves_only.py")

BASE = {
    "src/routes/goals.tsx": (
        'import { a } from "../lib/a";\n'
        'import {\n'
        '  b,\n'
        '  c,\n'
        '} from "../lib/bc";\n'
        "\n"
        "export function Page() {\n"
        "  return <Card x={a(b, c)} />;\n"
        "}\n"
        "\n"
        "function Card({ x }) {\n"
        "  return <div>{x}</div>;\n"
        "}\n"
    ),
    "src/lib/a.ts": 'import { z } from "./z";\nexport const a = (b, c) => z(b) + c;\n',
    "src/lib/bc.ts": "export const b = 1;\nexport const c = 2;\n",
    "src/lib/z.ts": "export const z = (n) => n * 2;\n",
    "app/tool.py": "from app.util import helper\n\n\ndef run():\n    return helper()\n",
    "app/util.py": "def helper():\n    return 1\n",
    "app/routes.py": '@app.route("/a")\ndef f():\n    return 1\n\n\n@app.route("/b")\ndef g():\n    return 2\n',
    "notes.txt": "keep me\n",
}

passed = failed = 0


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def write(root, files):
    for path, text in files.items():
        full = os.path.join(root, path)
        if text is None:
            os.remove(full)
            continue
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)


def repo():
    root = tempfile.mkdtemp()
    sh(root, "git", "init", "-q")
    write(root, BASE)
    sh(root, "git", "add", "-A")
    sh(root, "git", "-c", "user.email=t@x", "-c", "user.name=t", "commit", "-qm", "base")
    return root


def case(name, change, want_ok, want_text=None, staged=False):
    """change(root) edits the repo; the case commits it (or only stages it) and runs the check."""
    global passed, failed
    root = repo()
    change(root)
    sh(root, "git", "add", "-A")
    if staged:
        run = sh(root, sys.executable, "-I", SCRIPT, "HEAD")
    else:
        sh(root, "git", "-c", "user.email=t@x", "-c", "user.name=t", "commit", "-qm", "change")
        run = sh(root, sys.executable, "-I", SCRIPT, "HEAD~1", "HEAD")
    text = run.stdout + run.stderr
    ok = (run.returncode == 0) == want_ok and (want_text is None or want_text in text)
    if ok:
        passed += 1
        print(f"✔ {name}")
    else:
        failed += 1
        print(f"✘ {name}: exit {run.returncode}\n{text}")


def git_mv(src, dst):
    def change(root):
        os.makedirs(os.path.dirname(os.path.join(root, dst)), exist_ok=True)
        sh(root, "git", "mv", src, dst)
    return change


def edit(path, old, new):
    def change(root):
        full = os.path.join(root, path)
        with open(full) as f:
            text = f.read()
        assert old in text, f"{old!r} not in {path}"
        with open(full, "w") as f:
            f.write(text.replace(old, new))
    return change


def both(*changes):
    def change(root):
        for c in changes:
            c(root)
    return change


def extract_card(root):
    """Cut Card out of the route into its own file, export it, import it back."""
    write(root, {
        "src/routes/goals.tsx": (
            'import { a } from "../lib/a";\n'
            'import {\n'
            '  b,\n'
            '  c,\n'
            '} from "../lib/bc";\n'
            'import { Card } from "../features/goals/card";\n'
            "\n"
            "export function Page() {\n"
            "  return <Card x={a(b, c)} />;\n"
            "}\n"
        ),
        "src/features/goals/card.tsx": "export function Card({ x }) {\n  return <div>{x}</div>;\n}\n",
    })


# A move that compiles unchanged passes.
case("a pure git mv passes", git_mv("src/lib/z.ts", "src/util/z.ts"), True)
case("a moved file whose import path changed passes",
     both(git_mv("src/lib/a.ts", "src/core/a.ts"), edit("src/core/a.ts", '"./z"', '"../lib/z"'),
          edit("src/routes/goals.tsx", '"../lib/a"', '"../core/a"')), True)
case("a declaration cut into a new file with export and import passes", extract_card, True)
case("a name added inside a multi-line import passes",
     edit("src/routes/goals.tsx", "  c,\n", "  c,\n  d,\n"), True)
case("a re-export line passes", edit("src/lib/bc.ts", "export const c = 2;\n",
                                     'export const c = 2;\nexport { z } from "./z";\n'), True)
case("a python import that changed passes",
     both(git_mv("app/util.py", "app/lib/util.py"), edit("app/tool.py", "app.util", "app.lib.util")), True)
case("whole declarations reordered inside one file pass",
     edit("src/lib/bc.ts", "export const b = 1;\nexport const c = 2;\n", "export const c = 2;\nexport const b = 1;\n"), True)
case("a moved file with a non-ASCII name passes", git_mv("src/lib/z.ts", "src/lib/zé.ts"), True)
case("blank lines added or removed pass", edit("src/routes/goals.tsx", "}\n\nfunction", "}\n\n\n\nfunction"), True)
case("the staged index is checked when no head is given", extract_card, True, staged=True)
case("a pass names the count of moved lines", extract_card, True, "moves only")

# Anything else is a logic edit and fails, naming the line.
case("a body line changed in a moved file fails",
     both(git_mv("src/lib/z.ts", "src/util/z.ts"), edit("src/util/z.ts", "n * 2", "n * 3")),
     False, "n * 3")
case("a renamed identifier fails", edit("src/routes/goals.tsx", "function Card", "function GoalCard"),
     False, "GoalCard")
case("an added comment fails", edit("src/lib/bc.ts", "export const b", "// one\nexport const b"),
     False, "// one")
case("a deleted line fails", edit("src/lib/bc.ts", "export const c = 2;\n", ""), False, "const c = 2")
case("a copied, not moved, declaration fails",
     lambda root: write(root, {"src/features/goals/card.tsx": "export function Card({ x }) {\n  return <div>{x}</div>;\n}\n"}),
     False, "Card")
case("a changed line in a non-code file fails", edit("notes.txt", "keep me", "keep you"), False, "keep you")
case("a dynamic import() line is not an import statement",
     edit("src/lib/z.ts", "export const z = (n) => n * 2;\n",
          'export const z = (n) => n * 2;\nconst lazy = () => import("./a");\n'),
     False, 'import("./a")')
case("a line that starts with the word import but is code fails",
     edit("src/lib/z.ts", "export const z = (n) => n * 2;\n",
          "export const z = (n) => n * 2;\nimportant();\n"), False, "important()")
case("a route path string changed by the move fails",
     edit("src/routes/goals.tsx", "export function Page() {", 'export const id = "/goals";\nexport function Page() {'),
     False, '"/goals"')


case("a statement moved from one function into another fails",
     edit("src/routes/goals.tsx",
          "  return <Card x={a(b, c)} />;\n}\n\nfunction Card({ x }) {\n  return <div>{x}</div>;\n}\n",
          "  return <Card x={a(b, c)} />;\n  return <div>{x}</div>;\n}\n\nfunction Card({ x }) {\n}\n"),
     False, "function Card")
case("a python line dedented out of its function fails",
     edit("app/util.py", "def helper():\n    return 1\n", "def helper():\nreturn 1\n"), False, "def helper()")
case("a changed line after an export list is not hidden",
     edit("src/lib/bc.ts", "export const c = 2;\n", "export const c = 2;\nexport { b as bb };\nfromEntries(1);\n"),
     False, "fromEntries(1)")
case("decorators swapped between two functions fail",
     edit("app/routes.py", '"/a")\ndef f():\n    return 1\n\n\n@app.route("/b")',
          '"/b")\ndef f():\n    return 1\n\n\n@app.route("/a")'), False, '@app.route("/b")')
case("a python import added inside a function body fails",
     edit("app/tool.py", "def run():\n", "def run():\n    import os\n"), False, "def run()")
case("code after an import on the same line fails",
     edit("src/routes/goals.tsx", 'from "../lib/a";\n', 'from "../lib/a"; boom();\n'), False, "boom();")
case("code after a python import on the same line fails",
     edit("app/tool.py", "import helper\n", "import helper; boom()\n"), False, "boom()")
case("a reindented line fails", edit("src/lib/z.ts", "export const z", "  export const z"), False, "export const z")


def swap_inside():
    """Base holds f(); the change swaps two of its statements."""
    global passed, failed
    root = repo()
    write(root, {"src/lib/swap.js": "export function f(a) {\n  const t = a.x;\n  a.x = 0;\n  return t;\n}\n"})
    sh(root, "git", "add", "-A")
    sh(root, "git", "-c", "user.email=t@x", "-c", "user.name=t", "commit", "-qm", "f")
    write(root, {"src/lib/swap.js": "export function f(a) {\n  a.x = 0;\n  const t = a.x;\n  return t;\n}\n"})
    sh(root, "git", "add", "-A")
    sh(root, "git", "-c", "user.email=t@x", "-c", "user.name=t", "commit", "-qm", "swap")
    run = sh(root, sys.executable, "-I", SCRIPT, "HEAD~1", "HEAD")
    if run.returncode == 1 and "function f(a)" in run.stdout:
        passed += 1
        print("✔ two statements swapped inside a function fail, naming the declaration")
    else:
        failed += 1
        print(f"✘ two statements swapped inside a function fail: exit {run.returncode}\n{run.stdout}{run.stderr}")


def empty_index():
    global passed, failed
    root = repo()
    run = sh(root, sys.executable, "-I", SCRIPT, "HEAD")
    if run.returncode == 2 and "nothing" in run.stdout:
        passed += 1
        print("✔ an empty staged index exits 2")
    else:
        failed += 1
        print(f"✘ an empty staged index exits 2: exit {run.returncode}\n{run.stdout}{run.stderr}")


swap_inside()
empty_index()


def bad_ref():
    global passed, failed
    root = repo()
    run = sh(root, sys.executable, "-I", SCRIPT, "no-such-ref", "HEAD")
    if run.returncode == 2 and "no-such-ref" in run.stdout + run.stderr:
        passed += 1
        print("✔ an unknown ref exits 2 and names it")
    else:
        failed += 1
        print(f"✘ an unknown ref exits 2 and names it: exit {run.returncode}\n{run.stdout}{run.stderr}")


bad_ref()

print(f"{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
