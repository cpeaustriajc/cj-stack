#!/usr/bin/env bash
set -euo pipefail
git init -q -b main . && git config user.email e@x && git config user.name e
commit() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q "${@:2}"; }

mkdir -p app/pages .claude/skills/run-shop .claude/skills/verify/references/features
touch app/pages/__init__.py
printf 'def render():\n    return "<h1>Cart</h1><p>Your cart is empty</p>"\n' > app/pages/cart.py
printf 'def render():\n    return "<h1>Settings</h1><label>Display name</label><input name=display_name>"\n' > app/pages/settings.py
cat > app/routes.py <<'EOF'
from pages import cart, settings

ROUTES = {
    "/cart": cart.render,
    "/settings": settings.render,
}
EOF
cat > app/server.py <<'EOF'
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from routes import ROUTES


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        page = ROUTES.get(self.path)
        body = (page() if page else "<h1>Not found</h1>").encode()
        self.send_response(200 if page else 404)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(body)


server = HTTPServer(("127.0.0.1", int(sys.argv[1]) if len(sys.argv) > 1 else 0), Handler)
print(f"listening on {server.server_address[1]}", flush=True)
server.serve_forever()
EOF

cat > .claude/skills/run-shop/SKILL.md <<'EOF'
---
name: run-shop
description: Launch and drive the shop app. Use to start it, open a page or stop it.
---

# Run shop

- Launch: `python3 app/server.py 0 > .run.log 2>&1 & echo $!`. Keep the PID.
- Ready: `.run.log` prints `listening on <port>`. Use that port.
- Drive: `curl -s -w '\n%{http_code}\n' http://127.0.0.1:<port><path>`.
- Stop: `kill <PID>`.
EOF

cat > .claude/skills/verify/SKILL.md <<'EOF'
---
name: verify
description: >
  Verify the current change by driving the real app. Use before commit and before a PR. Prints
  one result line per feature: VERIFIED, NOT VERIFIED or BLOCKED.
---

# Verify

## Launch

Use the project's run skill `run-shop`. Wait for `listening on <port>`. Time out after 10 seconds.

## Select

Read `references/features/README.md`. Run the **Check** of each feature whose **Code** line
matches a changed path.

## Drive

Run each check with `set -o pipefail` and read the exit code.

## Cleanup

Stop the PID that Launch printed.

## Result line format

`<feature>: VERIFIED | NOT VERIFIED | BLOCKED  cmd: <re-run command>  evidence: <path>`
EOF
cat > .claude/skills/verify/references/features/README.md <<'EOF'
# Features

- [cart.md](cart.md): the cart page
- [settings.md](settings.md): the settings page
EOF
cat > .claude/skills/verify/references/features/cart.md <<'EOF'
# Cart

The cart page lists what the user will buy.

- **How a user gets there:** open `/cart`.
- **Code:** app/pages/cart.py, app/routes.py
- **Tests:** none yet
- **Check:** `curl -s http://127.0.0.1:<port>/cart` returns 200 and shows "Your cart is empty".
EOF
cat > .claude/skills/verify/references/features/settings.md <<'EOF'
# Settings

The settings page lets the user change their display name.

- **How a user gets there:** open `/settings`.
- **Code:** app/pages/settings.py, app/routes.py
- **Tests:** none yet
- **Check:** `curl -s http://127.0.0.1:<port>/settings` returns 200 and shows a "Display name" field.
EOF
printf '.run.log\n__pycache__/\n' > .gitignore
git add . && commit "2026-09-20T10:00:00" -m "init: shop with cart and settings, verify skill"
commit "2026-10-03T10:00:00" --allow-empty -m "verify: weekly audit, clean (cart and settings VERIFIED)"

cat > app/routes.py <<'EOF'
from pages import cart, settings

ROUTES = {
    "/cart": cart.render,
    "/account/settings": settings.render,
}
EOF
git add . && commit "2026-10-09T10:00:00" -m "account: move settings under /account"

printf 'def render():\n    return "<h1>Order history</h1><p>No orders yet</p>"\n' > app/pages/orders.py
cat > app/routes.py <<'EOF'
from pages import cart, orders, settings

ROUTES = {
    "/cart": cart.render,
    "/account/settings": settings.render,
    "/orders": orders.render,
}
EOF
git add . && commit "2026-10-14T10:00:00" -m "orders: add the order history page"
