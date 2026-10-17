#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/http src/notes src/store src/search
cat > package.json <<'JSON'
{ "name": "jot", "private": true, "main": "src/server.js" }
JSON
cat > src/server.js <<'JS'
const http = require('node:http');
const { route } = require('./http/router');
http.createServer(route).listen(3000);
JS
cat > src/http/router.js <<'JS'
const { saveNote } = require('../notes/save');
async function route(req, res) {
  if (req.method === 'PUT' && req.url.startsWith('/notes/')) {
    const id = req.url.slice('/notes/'.length);
    const body = JSON.parse(await read(req));
    const result = await saveNote(id, body, req.headers['if-match']);
    res.writeHead(result.status, { etag: String(result.version ?? '') });
    return res.end(JSON.stringify(result.body ?? {}));
  }
  res.writeHead(404).end();
}
function read(req) {
  return new Promise((ok) => { let s = ''; req.on('data', (c) => (s += c)); req.on('end', () => ok(s)); });
}
module.exports = { route };
JS
cat > src/notes/validate.js <<'JS'
function validate(body) {
  if (typeof body.title !== 'string' || body.title.trim() === '') return 'title is required';
  if (body.title.length > 120) return 'title is longer than 120 characters';
  if (typeof body.text !== 'string') return 'text must be a string';
  return null;
}
module.exports = { validate };
JS
cat > src/notes/save.js <<'JS'
const { validate } = require('./validate');
const store = require('../store/notes-store');
const { enqueueIndex } = require('../search/indexer');
async function saveNote(id, body, ifMatch) {
  const error = validate(body);
  if (error) return { status: 422, body: { error } };
  const current = await store.get(id);
  if (current && ifMatch && Number(ifMatch) !== current.version) {
    return { status: 409, body: { error: 'note changed since you opened it' }, version: current.version };
  }
  const version = current ? current.version + 1 : 1;
  await store.put(id, { ...body, version, savedAt: Date.now() });
  enqueueIndex(id);
  return { status: current ? 200 : 201, version };
}
module.exports = { saveNote };
JS
cat > src/store/notes-store.js <<'JS'
const fs = require('node:fs/promises');
const path = require('node:path');
const DIR = path.join(__dirname, '..', '..', 'data');
async function get(id) {
  try { return JSON.parse(await fs.readFile(path.join(DIR, `${id}.json`), 'utf8')); }
  catch (e) { if (e.code === 'ENOENT') return null; throw e; }
}
async function put(id, note) {
  await fs.mkdir(DIR, { recursive: true });
  const tmp = path.join(DIR, `${id}.json.tmp`);
  await fs.writeFile(tmp, JSON.stringify(note));
  await fs.rename(tmp, path.join(DIR, `${id}.json`));
}
module.exports = { get, put };
JS
cat > src/search/indexer.js <<'JS'
const pending = new Set();
let timer = null;
function enqueueIndex(id) {
  pending.add(id);
  if (!timer) timer = setTimeout(flush, 2000);
}
function flush() {
  timer = null;
  for (const id of pending) console.log(`indexed ${id}`);
  pending.clear();
}
module.exports = { enqueueIndex };
JS
mkdir -p src/auth src/events worker web
cat > src/auth/session.js <<'JS'
const sessions = new Map();
function requireUser(req) {
  const token = (req.headers.cookie || '').match(/sid=([\w-]+)/)?.[1];
  const user = token && sessions.get(token);
  if (!user) { const e = new Error('signed out'); e.status = 401; throw e; }
  return user;
}
module.exports = { requireUser, sessions };
JS
cat > src/events/bus.js <<'JS'
const fs = require('node:fs');
const path = require('node:path');
const QUEUE = path.join(__dirname, '..', '..', 'data', 'queue.ndjson');
function publish(type, payload) {
  fs.mkdirSync(path.dirname(QUEUE), { recursive: true });
  fs.appendFileSync(QUEUE, JSON.stringify({ type, payload, at: Date.now() }) + '\n');
}
module.exports = { publish, QUEUE };
JS
cat > worker/index-worker.js <<'JS'
const fs = require('node:fs');
const { QUEUE } = require('../src/events/bus');
let offset = 0;
setInterval(() => {
  if (!fs.existsSync(QUEUE)) return;
  const lines = fs.readFileSync(QUEUE, 'utf8').split('\n').filter(Boolean);
  for (const line of lines.slice(offset)) {
    const event = JSON.parse(line);
    if (event.type === 'note.saved') reindex(event.payload.id, event.payload.version);
  }
  offset = lines.length;
}, 1000);
function reindex(id, version) { console.log(`search: note ${id} at v${version}`); }
JS
cat > web/editor.js <<'JS'
let version = null;
let saving = null;
export function onChange(id, draft) {
  clearTimeout(saving);
  saving = setTimeout(() => save(id, draft), 800);
}
async function save(id, draft) {
  const res = await fetch(`/notes/${id}`, {
    method: 'PUT',
    headers: { 'content-type': 'application/json', ...(version ? { 'if-match': String(version) } : {}) },
    body: JSON.stringify(draft),
  });
  if (res.status === 409) return showConflict();
  version = Number(res.headers.get('etag'));
}
function showConflict() { document.body.dataset.conflict = 'true'; }
JS
cat > src/notes/save.js <<'JS'
const { validate } = require('./validate');
const store = require('../store/notes-store');
const { enqueueIndex } = require('../search/indexer');
const { publish } = require('../events/bus');
async function saveNote(user, id, body, ifMatch) {
  const error = validate(body);
  if (error) return { status: 422, body: { error } };
  const current = await store.get(id);
  if (current && current.owner !== user.id) return { status: 403, body: { error: 'not your note' } };
  if (current && ifMatch && Number(ifMatch) !== current.version) {
    return { status: 409, body: { error: 'note changed since you opened it' }, version: current.version };
  }
  const version = current ? current.version + 1 : 1;
  await store.put(id, { ...body, owner: user.id, version, savedAt: Date.now() });
  enqueueIndex(id);
  publish('note.saved', { id, version });
  return { status: current ? 200 : 201, version };
}
module.exports = { saveNote };
JS
sed -i.bak "s#const { saveNote } = require('../notes/save');#const { saveNote } = require('../notes/save');\nconst { requireUser } = require('../auth/session');#; s#await saveNote(id, body, req.headers\['if-match'\])#await saveNote(requireUser(req), id, body, req.headers['if-match'])#" src/http/router.js && rm src/http/router.js.bak
git init -q -b main . && git config user.email dev@jot.test && git config user.name "Ana Reyes"
git add . && git commit -qm "jot: notes server"
