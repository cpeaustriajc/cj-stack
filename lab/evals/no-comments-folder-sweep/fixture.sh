#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/legacy src/core test scripts
cat > package.json <<'JSON'
{
  "name": "till",
  "private": true,
  "type": "module",
  "scripts": {
    "typecheck": "node scripts/typecheck.mjs",
    "test": "node --test test/",
    "lint": "node scripts/lint.mjs"
  }
}
JSON
cat > README.md <<'MD'
# till

A small shop till.

- Typecheck: `node scripts/typecheck.mjs` loads every module and fails on a broken import.
- Tests: `node --test test/`.
- Lint: `node scripts/lint.mjs`. A line above code can say `// lint-disable-next-line <rule>`.
MD
cat > scripts/typecheck.mjs <<'JS'
import { readdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
const files = readdirSync("src", { recursive: true }).filter((n) => n.endsWith(".js")).map((n) => join("src", n));
let bad = 0;
for (const f of files) {
  try {
    await import(pathToFileURL(resolve(f)).href);
  } catch (e) {
    bad += 1;
    console.log(`${f}: ${e.message}`);
  }
}
console.log(`typecheck: ${files.length - bad} of ${files.length} modules load`);
process.exit(bad ? 1 : 0);
JS
cat > scripts/lint.mjs <<'JS'
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
const RULES = {
  "no-loose-equal": (line) => /[^=!]==[^=]/.test(line),
  "max-line": (line) => line.length > 100,
};
const files = readdirSync("src", { recursive: true }).filter((n) => n.endsWith(".js")).map((n) => join("src", n));
let bad = 0;
for (const file of files) {
  const lines = readFileSync(file, "utf8").split("\n");
  lines.forEach((line, i) => {
    const off = /lint-disable-next-line (\S+)/.exec(lines[i - 1] ?? "")?.[1];
    for (const [name, hit] of Object.entries(RULES)) {
      if (name !== off && hit(line)) {
        bad += 1;
        console.log(`${file}:${i + 1}: ${name}`);
      }
    }
  });
}
console.log(`lint: ${bad} problem(s)`);
process.exit(bad ? 1 : 0);
JS
cat > src/core/money.js <<'JS'
// round half up to whole cents
export function round(cents) {
  return Math.floor(cents + 0.5);
}
JS
cat > src/legacy/cart.js <<'JS'
/*
 * Copyright (c) 2019 Till Ltd. Licensed under the MIT License.
 */
// ===== Cart helpers =====
import { round } from "../core/money.js";

/**
 * Sum the line totals of a cart.
 * @param {{cents: number, qty: number}[]} lines
 * @returns {number} the total in cents
 */
export function total(lines) {
  // loop over the lines and add them up
  let sum = 0;
  for (const line of lines) {
    // multiply price by quantity
    sum += line.cents * line.qty;
  }
  // return the rounded total
  return round(sum);
}

// old version, keep for reference
// export function totalOld(lines) {
//   return lines.reduce((a, l) => a + l.cents * l.qty, 0);
// }

// HACK: we pass legacy = true because the second discount pass below used to
// double-apply coupons. The flag makes applyDiscount skip that pass. Fine for
// now, we will clean this up after the Q3 release.
export function applyDiscount(cents, percent, legacy = true) {
  const once = Math.round(cents * (1 - percent / 100));
  if (!legacy) return Math.round(once * (1 - percent / 100));
  return once;
}
JS
cat > src/legacy/format.js <<'JS'
// prettier-ignore
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// A date-only ISO string such as "2020-01-02" parses as UTC by the spec, so we pass
// slashes to get local time. See https://tc39.es/ecma262/#sec-date.parse
export function parseDay(text) {
  return new Date(text.replaceAll("-", "/"));
}

// format the date as "2 Jan"
export function label(date) {
  return `${date.getDate()} ${MONTHS[date.getMonth()]}`;
}

// lint-disable-next-line max-line
export const HELP_URL = "https://help.till.example/articles/receipts/how-to-print-a-receipt-again-later";

export function sameSku(a, b) {
  // lint-disable-next-line no-loose-equal
  return String(a.sku) == String(b.sku);
}
JS
cat > test/cart.test.js <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { total, applyDiscount } from "../src/legacy/cart.js";
import { label, sameSku } from "../src/legacy/format.js";

test("total multiplies and sums", () => {
  assert.equal(total([{ cents: 250, qty: 2 }, { cents: 100, qty: 1 }]), 600);
});

test("a discount applies once", () => {
  assert.equal(applyDiscount(1000, 10), 900);
});

test("label shows day and month", () => {
  assert.equal(label(new Date(2020, 0, 2)), "2 Jan");
});

test("same sku matches", () => {
  assert.equal(sameSku({ sku: "A1" }, { sku: "A1" }), true);
});
JS
printf 'node_modules/\n' > .gitignore
git init -q && git add -A && git -c user.email=f@x -c user.name=f commit -qm fixture
git config user.email f@x && git config user.name f
