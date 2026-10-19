#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/goals src/ui
cat > package.json <<'JSON'
{ "name": "acme-lite", "private": true, "type": "module", "scripts": { "dev": "vite" } }
JSON
cat > index.html <<'HTML'
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Goals</title><link rel="stylesheet" href="src/ui/app.css"></head>
<body><main id="app"></main><script type="module" src="src/goals/page.js"></script></body>
</html>
HTML
cat > src/ui/app.css <<'CSS'
:root { --radius: 10px; --line: #e4e4e7; --ink: #18181b; --muted: #71717a; --accent: #4f46e5; }
body { margin: 0; font: 15px/1.5 system-ui, sans-serif; color: var(--ink); background: #fafafa; }
main { max-width: 640px; margin: 48px auto; padding: 0 16px; }
h1 { font-size: 22px; margin: 0 0 16px; }
.add { display: flex; gap: 8px; margin-bottom: 20px; }
.add input { flex: 1; padding: 10px 12px; border: 1px solid var(--line); border-radius: var(--radius); font: inherit; }
.btn { padding: 10px 14px; border: 0; border-radius: var(--radius); background: var(--accent); color: #fff; font: inherit; cursor: pointer; }
.goals { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.goal { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 12px; padding: 12px 14px; background: #fff; border: 1px solid var(--line); border-radius: var(--radius); }
.goal.done .title { color: var(--muted); text-decoration: line-through; }
.goal .delete { border: 0; background: none; color: var(--muted); cursor: pointer; }
.progress { height: 6px; margin: 4px 0 0; border-radius: 3px; background: var(--line); overflow: hidden; }
.progress > span { display: block; height: 100%; background: var(--accent); }
.summary { display: flex; justify-content: space-between; margin: 24px 0 8px; color: var(--muted); }
.empty { padding: 40px 0; text-align: center; color: var(--muted); }
.complete { padding: 16px; border-radius: var(--radius); background: #ecfdf5; color: #065f46; text-align: center; }
.menu { position: absolute; right: 0; top: 28px; padding: 4px; background: #fff; border: 1px solid var(--line); border-radius: 8px; box-shadow: 0 8px 24px rgb(0 0 0 / 0.08); }
.menu[hidden] { display: none; }
CSS
cat > src/goals/store.js <<'JS'
const KEY = 'goals';
export const load = () => JSON.parse(localStorage.getItem(KEY) ?? '[]');
export const save = (goals) => localStorage.setItem(KEY, JSON.stringify(goals));
JS
cat > src/goals/page.js <<'JS'
import { load, save } from './store.js';

let goals = load();
const app = document.querySelector('#app');

function render() {
  const done = goals.filter((g) => g.done).length;
  const pct = goals.length ? Math.round((done / goals.length) * 100) : 0;
  app.innerHTML = `
    <h1>Goals this week</h1>
    <form class="add"><input name="title" placeholder="Add a goal" autocomplete="off"><button class="btn">Add</button></form>
    ${goals.length === 0 ? '<p class="empty">No goals yet. Add one to start your week.</p>' : ''}
    <ul class="goals">
      ${goals.map((g, i) => `
        <li class="goal ${g.done ? 'done' : ''}" data-i="${i}">
          <input type="checkbox" ${g.done ? 'checked' : ''} aria-label="Done">
          <span class="title">${g.title}</span>
          <span style="position:relative">
            <button class="delete" aria-label="More">⋯</button>
            <div class="menu" hidden><button class="btn remove">Delete</button></div>
          </span>
        </li>`).join('')}
    </ul>
    <div class="summary"><span>${done} of ${goals.length} done</span><span>${pct}%</span></div>
    <div class="progress"><span style="width:${pct}%"></span></div>
    ${goals.length > 0 && done === goals.length ? '<p class="complete">Every goal done this week.</p>' : ''}
  `;
}

app.addEventListener('submit', (e) => {
  e.preventDefault();
  const title = new FormData(e.target).get('title').trim();
  if (!title) return;
  goals.push({ title, done: false });
  save(goals);
  render();
});

app.addEventListener('change', (e) => {
  const i = e.target.closest('.goal')?.dataset.i;
  if (i === undefined) return;
  goals[i].done = e.target.checked;
  save(goals);
  render();
});

app.addEventListener('click', (e) => {
  const item = e.target.closest('.goal');
  if (e.target.matches('.delete')) item.querySelector('.menu').hidden = !item.querySelector('.menu').hidden;
  if (e.target.matches('.remove')) { goals.splice(item.dataset.i, 1); save(goals); render(); }
});

// j / k move focus between goals; x toggles the focused goal.
document.addEventListener('keydown', (e) => {
  const items = [...document.querySelectorAll('.goal input')];
  const at = items.indexOf(document.activeElement);
  if (e.key === 'j') items[Math.min(at + 1, items.length - 1)]?.focus();
  if (e.key === 'k') items[Math.max(at - 1, 0)]?.focus();
  if (e.key === 'x' && at >= 0) items[at].click();
});

render();
JS
cat > README.md <<'MD'
# acme-lite

A weekly goals page. `src/goals/page.js` renders it; goals live in localStorage. People open it a
few times a day to add goals and tick them off; power users move with j and k and tick with x.
MD
git init -q && git add -A && git -c user.email=f@x -c user.name=f commit -qm fixture
