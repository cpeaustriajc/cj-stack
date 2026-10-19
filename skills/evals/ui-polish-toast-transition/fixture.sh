#!/usr/bin/env bash
set -euo pipefail
cat > index.html <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Sync</title>
  <link rel="stylesheet" href="toast.css">
</head>
<body>
  <button id="sync">Sync now</button>
  <ol class="toasts" aria-live="polite"></ol>
  <script type="module" src="toast.js"></script>
</body>
</html>
HTML
cat > toast.css <<'CSS'
:root {
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
}

.toasts {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 356px;
  margin: 0;
  padding: 0;
  list-style: none;
}

/* Each toast sits at its stack slot through --offset. A new toast changes every
   older toast's offset, so a toast still entering is retargeted mid-motion: the
   transition picks up from where it is on screen. */
.toast {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 100%;
  padding: 14px 16px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 4px 12px rgb(0 0 0 / 0.08);
  transform: translateY(var(--offset, 0px));
  opacity: 1;
  transition:
    transform 400ms var(--ease-out),
    opacity 400ms var(--ease-out);
  touch-action: pan-y;
}

@starting-style {
  .toast {
    transform: translateY(100%);
    opacity: 0;
  }
}

.toast[data-leaving] {
  transform: translateY(100%);
  opacity: 0;
  transition:
    transform 200ms var(--ease-out),
    opacity 200ms var(--ease-out);
}

/* While a finger drags the toast, it tracks 1:1 with no transition. */
.toast[data-dragging] {
  transform: translate(var(--drag-x, 0px), var(--offset, 0px));
  transition: none;
}

/* Swipe release: dismiss to the right, or snap back. */
.toast[data-swiped] {
  transform: translate(110%, var(--offset, 0px));
  opacity: 0;
  transition:
    transform 200ms var(--ease-out),
    opacity 200ms var(--ease-out);
}

.toast[data-snapping] {
  transform: translateY(var(--offset, 0px));
  transition: transform 200ms var(--ease-out);
}

@media (prefers-reduced-motion: reduce) {
  .toast,
  .toast[data-leaving],
  .toast[data-swiped],
  .toast[data-snapping] {
    transition: opacity 200ms var(--ease-out);
  }
  @starting-style {
    .toast { transform: translateY(var(--offset, 0px)); opacity: 0; }
  }
}
CSS
cat > toast.js <<'JS'
const list = document.querySelector('.toasts');
const GAP = 12;

function layout() {
  let y = 0;
  for (const el of [...list.children].reverse()) {
    if (el.dataset.leaving !== undefined || el.dataset.swiped !== undefined) continue;
    el.style.setProperty('--offset', `${-y}px`);
    y += el.offsetHeight + GAP;
  }
}

export function toast(text, ms = 4000) {
  const el = document.createElement('li');
  el.className = 'toast';
  el.textContent = text;
  list.append(el);
  layout();
  swipe(el);
  el.timer = setTimeout(() => leave(el), ms);
}

function leave(el, attr = 'leaving') {
  clearTimeout(el.timer);
  el.dataset[attr] = '';
  layout();
  el.addEventListener('transitionend', () => el.remove(), { once: true });
}

function swipe(el) {
  let startX = 0;
  let pointer = null;
  el.addEventListener('pointerdown', (e) => {
    if (pointer !== null) return; // a second finger is ignored
    pointer = e.pointerId;
    startX = e.clientX;
    el.setPointerCapture(e.pointerId);
  });
  el.addEventListener('pointermove', (e) => {
    if (e.pointerId !== pointer) return;
    const dx = Math.max(0, e.clientX - startX);
    if (dx < 10 && el.dataset.dragging === undefined) return;
    el.dataset.dragging = '';
    el.style.setProperty('--drag-x', `${dx}px`);
  });
  el.addEventListener('pointerup', (e) => {
    if (e.pointerId !== pointer) return;
    pointer = null;
    const dx = Math.max(0, e.clientX - startX);
    delete el.dataset.dragging;
    if (dx > el.offsetWidth / 2) return leave(el, 'swiped');
    el.dataset.snapping = '';
    el.addEventListener('transitionend', () => delete el.dataset.snapping, { once: true });
  });
}

document.querySelector('#sync').addEventListener('click', () => {
  for (const name of ['Inbox', 'Calendar', 'Contacts']) toast(`${name} synced`);
});
JS
git init -q && git add -A && git -c user.email=f@x -c user.name=f commit -qm fixture
