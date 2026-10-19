#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/http src/notes src/users src/mail src/events worker web
cat > package.json <<'JSON'
{ "name": "jot", "private": true, "main": "src/server.js", "scripts": { "worker": "node worker/reminder-worker.js" } }
JSON
cat > src/server.js <<'JS'
const http = require('node:http');
const { route } = require('./http/router');
http.createServer(route).listen(3000);
JS
cat > src/http/router.js <<'JS'
const { saveNote } = require('../notes/save');
const users = require('../users/users-store');
async function route(req, res) {
  if (req.method === 'PUT' && req.url.startsWith('/notes/')) {
    const body = JSON.parse(await read(req));
    const result = await saveNote(req.url.slice(7), body, req.headers['x-user']);
    return res.writeHead(result.status).end(JSON.stringify(result.body ?? {}));
  }
  if (req.method === 'PATCH' && req.url === '/me/settings') {
    const body = JSON.parse(await read(req));
    const user = await users.get(req.headers['x-user']);
    user.emailOptOut = Boolean(body.emailOptOut);
    await users.put(user);
    return res.writeHead(204).end();
  }
  res.writeHead(404).end();
}
function read(req) {
  return new Promise((ok) => { let s = ''; req.on('data', (c) => (s += c)); req.on('end', () => ok(s)); });
}
module.exports = { route };
JS
cat > src/notes/save.js <<'JS'
const store = require('./notes-store');
const bus = require('../events/bus');
async function saveNote(id, body, userId) {
  if (typeof body.title !== 'string' || !body.title.trim()) return { status: 422, body: { error: 'title' } };
  const note = { id, owner: userId, title: body.title, text: body.text ?? '', remindAt: body.remindAt ?? null, updatedAt: Date.now() };
  await store.put(note);
  bus.publish('note.saved', note);
  return { status: 200, body: note };
}
module.exports = { saveNote };
JS
cat > src/notes/notes-store.js <<'JS'
const fs = require('node:fs/promises');
const FILE = 'data/notes.json';
async function all() { try { return JSON.parse(await fs.readFile(FILE, 'utf8')); } catch { return {}; } }
async function put(note) { const n = await all(); n[note.id] = note; await fs.mkdir('data', { recursive: true }); await fs.writeFile(FILE, JSON.stringify(n)); }
async function dueReminders(now) { return Object.values(await all()).filter((n) => n.remindAt && n.remindAt <= now && !n.reminded); }
async function markReminded(id) { const n = await all(); n[id].reminded = true; await fs.writeFile(FILE, JSON.stringify(n)); }
module.exports = { all, put, dueReminders, markReminded };
JS
cat > src/users/users-store.js <<'JS'
const fs = require('node:fs/promises');
const FILE = 'data/users.json';
async function all() { try { return JSON.parse(await fs.readFile(FILE, 'utf8')); } catch { return {}; } }
async function get(id) { return (await all())[id]; }
async function put(user) { const u = await all(); u[user.id] = user; await fs.mkdir('data', { recursive: true }); await fs.writeFile(FILE, JSON.stringify(u)); }
module.exports = { all, get, put };
JS
cat > src/mail/mailer.js <<'JS'
const fs = require('node:fs/promises');
async function send(to, subject, html) {
  await fs.mkdir('outbox', { recursive: true });
  await fs.writeFile(`outbox/${Date.now()}-${to}.html`, `<h1>${subject}</h1>${html}`);
}
module.exports = { send };
JS
cat > src/mail/templates.js <<'JS'
function reminder(note) { return { subject: `Reminder: ${note.title}`, html: `<p>${note.text}</p>` }; }
module.exports = { reminder };
JS
cat > src/events/bus.js <<'JS'
const handlers = {};
function on(name, fn) { (handlers[name] ??= []).push(fn); }
function publish(name, payload) { for (const fn of handlers[name] ?? []) fn(payload); }
module.exports = { on, publish };
JS
cat > worker/reminder-worker.js <<'JS'
const notes = require('../src/notes/notes-store');
const users = require('../src/users/users-store');
const mailer = require('../src/mail/mailer');
const templates = require('../src/mail/templates');
async function tick() {
  for (const note of await notes.dueReminders(Date.now())) {
    const user = await users.get(note.owner);
    if (user.emailOptOut) continue;
    const { subject, html } = templates.reminder(note);
    await mailer.send(user.email, subject, html);
    await notes.markReminded(note.id);
  }
}
setInterval(tick, 60_000);
JS
cat > web/settings.js <<'JS'
export function renderSettings(user, root) {
  root.innerHTML = `<label><input type="checkbox" id="optout" ${user.emailOptOut ? 'checked' : ''}> Stop all emails</label>`;
  root.querySelector('#optout').addEventListener('change', (e) =>
    fetch('/me/settings', { method: 'PATCH', headers: { 'x-user': user.id }, body: JSON.stringify({ emailOptOut: e.target.checked }) }));
}
JS
cat > README.md <<'MD'
# jot

Notes with reminders. `node src/server.js` runs the API; `npm run worker` sends reminder emails.
Email opt-out is one flag on the user (`emailOptOut`), set from `web/settings.js`.
MD
git init -q && git add -A && git -c user.email=f@x -c user.name=f commit -qm fixture
