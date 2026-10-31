#!/usr/bin/env bash
set -euo pipefail
git init -q -b main . && git config user.email dev@shop.test && git config user.name "Ben Ortiz"
mkdir -p src
c() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -qam "$2"; }
cat > src/sync.js <<'JS'
const BATCH_SIZE = 100;
async function syncProducts(client, products) {
  for (let i = 0; i < products.length; i += BATCH_SIZE) {
    await client.post("/v2/products/bulk", products.slice(i, i + BATCH_SIZE));
  }
}
module.exports = { syncProducts, BATCH_SIZE };
JS
git add . && c 2026-02-01T10:00:00 "sync: bulk upload products to the vendor (#8)"
sed -i.bak 's/BATCH_SIZE = 100/BATCH_SIZE = 25/' src/sync.js && rm src/sync.js.bak
c 2026-02-19T11:00:00 "sync: lower BATCH_SIZE to 25 (#12)

The vendor rejects a bulk request over 1 MB with HTTP 413. A product
with all its images is up to 38 KB, so 25 is the most that always fits.
Sync got slower (about 4x more requests); we accept that."
cat > src/config.js <<'JS'
module.exports = { BATCH_SIZE: 25 };
JS
cat > src/sync.js <<'JS'
const { BATCH_SIZE } = require("./config");
async function syncProducts(client, products) {
  for (let i = 0; i < products.length; i += BATCH_SIZE) {
    await client.post("/v2/products/bulk", products.slice(i, i + BATCH_SIZE));
  }
}
module.exports = { syncProducts };
JS
git add . && c 2026-04-03T15:00:00 "refactor: move constants to config.js (#19)"
