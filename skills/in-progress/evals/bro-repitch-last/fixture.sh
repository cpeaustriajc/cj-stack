#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/holds src/copies
cat > GLOSSARY.md <<'MD'
# Glossary

- **Copy**: one physical book that the library owns. A title can have many copies.
- **Hold**: a member's place in the queue for a title. A hold is *ready* when a copy waits for that member at their branch.
- **Pickup window**: the days a ready hold waits on the shelf before it lapses. It is 7 days.
- **Lapse**: a ready hold that nobody picked up in its pickup window. The copy goes to the next hold in the queue.
- **In transit**: a copy on the van between two branches. It is not on any shelf.
- **Sweep**: the nightly job that lapses ready holds whose pickup window has ended.
- **Chain lapse**: one lapse that hands an in-transit copy to the next hold, which then lapses too, and so on down the queue.
MD
cat > src/holds/sweep.js <<'JS'
const holds = require('./holds-store');
const copies = require('../copies/copies-store');
const PICKUP_WINDOW_DAYS = 7;
async function sweep(now) {
  for (const hold of await holds.ready()) {
    const copy = await copies.get(hold.copy_id);
    if (copy.state === 'transit') continue;
    if (now - hold.ready_at < PICKUP_WINDOW_DAYS * 86400000) continue;
    await holds.lapse(hold.id);
    await holds.passToNext(hold.title_id, copy.id, now);
  }
}
module.exports = { sweep };
JS
cat > src/holds/holds-store.js <<'JS'
const db = require('../db');
async function ready() { return db.all("SELECT * FROM holds WHERE state = 'ready'"); }
async function lapse(id) { return db.run("UPDATE holds SET state = 'lapsed' WHERE id = ?", id); }
async function passToNext(titleId, copyId, now) {
  return db.run("UPDATE holds SET state = 'ready', copy_id = ?, ready_at = ? WHERE id = (SELECT id FROM holds WHERE title_id = ? AND state = 'queued' ORDER BY placed_at LIMIT 1)", copyId, now, titleId);
}
module.exports = { ready, lapse, passToNext };
JS
cat > src/copies/copies-store.js <<'JS'
const db = require('../db');
async function get(id) { return db.get('SELECT * FROM copies WHERE id = ?', id); }
async function arrive(id, branchId) { return db.run("UPDATE copies SET state = 'shelf', branch_id = ? WHERE id = ?", branchId, id); }
module.exports = { get, arrive };
JS
cat > CLAUDE.md <<'MD'
# shelf

Library holds service. Use the terms in GLOSSARY.md. `npm test` runs the tests.
MD
git init -q && git add -A && git -c user.email=f@x -c user.name=f commit -qm "shelf: holds and copies"
