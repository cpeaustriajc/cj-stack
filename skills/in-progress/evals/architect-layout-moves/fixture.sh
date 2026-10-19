#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/routes src/features/debts src/features/home src/lib test scripts
cat > package.json <<'JSON'
{
  "name": "tally",
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
# tally

A small savings app. Each file in `src/routes/` is one screen.

- Typecheck: `node scripts/typecheck.mjs` loads every module and fails on a broken import.
- Tests: `node --test test/`.
- Lint: `node scripts/lint.mjs` runs the repo's own rules. A new rule goes in its `RULES` list.
MD
cat > scripts/typecheck.mjs <<'JS'
import { readdirSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
const files = [];
const walk = (dir) => {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p);
    else if (p.endsWith(".js")) files.push(p);
  }
};
walk("src");
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
const RULES = [
  {
    name: "no-console",
    files: "src",
    check: (text) => (/console\.log\(/.test(text) ? "console.log in app code" : null),
  },
];
const list = (dir) => readdirSync(dir, { recursive: true }).filter((n) => n.endsWith(".js")).map((n) => join(dir, n));
let bad = 0;
for (const rule of RULES) {
  for (const file of list(rule.files)) {
    const problem = rule.check(readFileSync(file, "utf8"), file);
    if (problem) {
      bad += 1;
      console.log(`${file}: ${rule.name}: ${problem}`);
    }
  }
}
console.log(`lint: ${RULES.length} rule(s), ${bad} problem(s)`);
process.exit(bad ? 1 : 0);
JS
cat > src/lib/money.js <<'JS'
export function money(cents, currency) {
  return `${currency} ${(cents / 100).toFixed(2)}`;
}
JS
cat > src/lib/store.js <<'JS'
const goals = new Map();
export const store = {
  list: () => [...goals.values()],
  get: (id) => goals.get(id),
  put: (goal) => goals.set(goal.id, goal),
  remove: (id) => goals.delete(id),
};
JS
cat > src/features/debts/page.js <<'JS'
import { money } from "../../lib/money.js";
export function DebtsPage({ debts }) {
  return debts.map((d) => `${d.name}: ${money(d.cents, d.currency)}`).join("\n");
}
JS
cat > src/features/home/page.js <<'JS'
export function HomePage({ name }) {
  return `Hello, ${name}`;
}
JS
cat > src/routes/debts.js <<'JS'
import { DebtsPage } from "../features/debts/page.js";
export const route = { path: "/debts", title: "Debts" };
export function Page(props) {
  return DebtsPage(props);
}
JS
cat > src/routes/home.js <<'JS'
import { HomePage } from "../features/home/page.js";
export const route = { path: "/home", title: "Home" };
export function Page(props) {
  return HomePage(props);
}
JS
cat > src/routes/goals.js <<'JS'
import { money } from "../lib/money.js";
import { store } from "../lib/store.js";

export const route = { path: "/goals", title: "Goals" };

const DAY = 24 * 60 * 60 * 1000;

export function progress(goal) {
  if (goal.targetCents <= 0) return 0;
  const saved = goal.contributions.reduce((sum, c) => sum + c.cents, 0);
  return Math.min(1, saved / goal.targetCents);
}

export function savedCents(goal) {
  return goal.contributions.reduce((sum, c) => sum + c.cents, 0);
}

export function daysLeft(goal, now) {
  if (!goal.deadline) return null;
  return Math.max(0, Math.ceil((goal.deadline - now) / DAY));
}

export function monthlyNeed(goal, now) {
  const days = daysLeft(goal, now);
  if (days === null || days === 0) return null;
  const left = goal.targetCents - savedCents(goal);
  if (left <= 0) return 0;
  return Math.ceil(left / Math.max(1, days / 30));
}

function plural(n, one, many) {
  return n === 1 ? one : many;
}

export function validateGoal(input) {
  const errors = {};
  if (typeof input.name !== "string" || !input.name.trim()) errors.name = "Name the goal";
  if (!Number.isInteger(input.targetCents) || input.targetCents <= 0) errors.target = "Enter an amount above zero";
  if (input.deadline !== undefined && !Number.isFinite(input.deadline)) errors.deadline = "Pick a date";
  return errors;
}

export function validateContribution(input) {
  const errors = {};
  if (!Number.isInteger(input.cents) || input.cents === 0) errors.cents = "Enter an amount";
  return errors;
}

function GoalCard(goal, now) {
  const pct = Math.round(progress(goal) * 100);
  const days = daysLeft(goal, now);
  const need = monthlyNeed(goal, now);
  const lines = [
    `${goal.name}: ${money(savedCents(goal), goal.currency)} of ${money(goal.targetCents, goal.currency)} (${pct}%)`,
  ];
  if (days !== null) lines.push(`${days} ${plural(days, "day", "days")} left`);
  if (need) lines.push(`${money(need, goal.currency)} a month to finish on time`);
  return lines.join("\n");
}

function GoalMenu(goal) {
  return [`Edit ${goal.name}`, `Add to ${goal.name}`, `Delete ${goal.name}`].join(" | ");
}

function GoalForm(input) {
  const errors = validateGoal(input);
  const fields = ["name", "target", "deadline"].map((f) => (errors[f] ? `${f}: ${errors[f]}` : `${f}: ok`));
  return fields.join("\n");
}

function ContributionPanel(goal, input) {
  const errors = validateContribution(input);
  if (errors.cents) return `Add to ${goal.name}: ${errors.cents}`;
  return `Add ${money(input.cents, goal.currency)} to ${goal.name}`;
}

export function saveGoal(input) {
  const errors = validateGoal(input);
  if (Object.keys(errors).length) return { ok: false, errors };
  const goal = { id: input.id, name: input.name.trim(), targetCents: input.targetCents, currency: input.currency ?? "USD", deadline: input.deadline, contributions: [] };
  store.put(goal);
  return { ok: true, goal };
}

export function addContribution(goalId, input) {
  const goal = store.get(goalId);
  if (!goal) return { ok: false, errors: { goal: "This goal is gone" } };
  const errors = validateContribution(input);
  if (Object.keys(errors).length) return { ok: false, errors };
  goal.contributions.push({ cents: input.cents, at: input.at });
  store.put(goal);
  return { ok: true, goal };
}

export function Page({ now, editing, adding }) {
  const goals = store.list();
  if (!goals.length) return "No goals yet. Add one to start.";
  const parts = goals.map((g) => `${GoalCard(g, now)}\n${GoalMenu(g)}`);
  if (editing) parts.push(GoalForm(editing));
  if (adding) parts.push(ContributionPanel(store.get(adding.goalId), adding));
  return parts.join("\n\n");
}
JS
cat > test/goals.test.js <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { progress, monthlyNeed, saveGoal, addContribution, Page } from "../src/routes/goals.js";

const DAY = 24 * 60 * 60 * 1000;

test("progress never passes 100 percent", () => {
  assert.equal(progress({ targetCents: 100, contributions: [{ cents: 150 }] }), 1);
});

test("a finished goal needs nothing a month", () => {
  assert.equal(monthlyNeed({ targetCents: 100, deadline: 60 * DAY, contributions: [{ cents: 100 }] }, 0), 0);
});

test("a goal without a name is not saved", () => {
  assert.equal(saveGoal({ id: "x", name: " ", targetCents: 100 }).ok, false);
});

test("a contribution to a deleted goal says the goal is gone", () => {
  assert.equal(addContribution("missing", { cents: 5 }).errors.goal, "This goal is gone");
});

test("the goals screen lists a saved goal", () => {
  saveGoal({ id: "trip", name: "Trip", targetCents: 10000 });
  addContribution("trip", { cents: 2500 });
  assert.match(Page({ now: 0 }), /Trip: USD 25.00 of USD 100.00 \(25%\)/);
});
JS
git init -q && git add -A && git -c user.email=f@x -c user.name=f commit -qm fixture
git config user.email f@x && git config user.name f
