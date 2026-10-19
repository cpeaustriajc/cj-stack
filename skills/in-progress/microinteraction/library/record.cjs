// Records one demo page into frames, a curve plot and the samples behind them.
// Usage: node record.cjs <demo.html> <out dir>
// The demo plays its motion when window.play() runs. Its [data-measure] element names
// the value to plot (x, y, w, h or o for opacity), the duration and the easing. Every animation is paused and
// seeked frame by frame, so a frame shows the exact value at its time.
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');

const FPS = 50;
const PRE_MS = 300;
const HOLD_MS = 900;
const SHEET_FRAMES = 12;
const W = 480;
const H = 270;

function bezier(x1, y1, x2, y2) {
  const at = (a, b, t) => 3 * a * t * (1 - t) ** 2 + 3 * b * t ** 2 * (1 - t) + t ** 3;
  return (x) => {
    let lo = 0, hi = 1;
    for (let i = 0; i < 40; i++) {
      const mid = (lo + hi) / 2;
      if (at(x1, x2, mid) < x) lo = mid; else hi = mid;
    }
    return at(y1, y2, (lo + hi) / 2);
  };
}

const KEYWORDS = {
  linear: [0, 0, 1, 1],
  ease: [0.25, 0.1, 0.25, 1],
  'ease-in': [0.42, 0, 1, 1],
  'ease-out': [0, 0, 0.58, 1],
  'ease-in-out': [0.42, 0, 0.58, 1],
};

function curve(easing) {
  const m = easing.match(/cubic-bezier\(([^)]*)\)/);
  const p = m ? m[1].split(',').map(Number) : KEYWORDS[easing.trim()];
  if (!p) throw new Error(`unknown easing: ${easing}`);
  return bezier(...p);
}

function plotSvg(samples, planned, title) {
  const pw = 480, ph = 200, l = 44, r = 16, t = 28, b = 30;
  const end = samples[samples.length - 1].t;
  const x = (ms) => l + (ms / end) * (pw - l - r);
  const lo = Math.min(0, ...samples.map((s) => s.p));
  const hi = Math.max(1, ...samples.map((s) => s.p));
  const y = (p) => t + (1 - (p - lo) / (hi - lo)) * (ph - t - b);
  const line = planned.map((s, i) => `${i ? 'L' : 'M'}${x(s.t).toFixed(1)},${y(s.p).toFixed(1)}`).join('');
  const dots = samples.map((s) => `<circle cx="${x(s.t).toFixed(1)}" cy="${y(s.p).toFixed(1)}" r="2.5"/>`).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${pw}" height="${ph}" font-family="sans-serif" font-size="11">
<rect width="100%" height="100%" fill="#fff"/>
<text x="${l}" y="17" font-size="12" fill="#111">${title}</text>
<line x1="${l}" y1="${y(0)}" x2="${pw - r}" y2="${y(0)}" stroke="#ccc"/>
<line x1="${l}" y1="${y(1)}" x2="${pw - r}" y2="${y(1)}" stroke="#ccc" stroke-dasharray="3 3"/>
<text x="${l - 6}" y="${y(0) + 4}" text-anchor="end" fill="#666">0</text>
<text x="${l - 6}" y="${y(1) + 4}" text-anchor="end" fill="#666">1</text>
<text x="${l}" y="${ph - 10}" fill="#666">0 ms</text>
<text x="${pw - r}" y="${ph - 10}" text-anchor="end" fill="#666">${Math.round(end)} ms</text>
<text x="${pw / 2}" y="${ph - 10}" text-anchor="middle" fill="#666">line: planned curve · dots: measured progress</text>
<path d="${line}" fill="none" stroke="#2563eb" stroke-width="2"/>
<g fill="#dc2626">${dots}</g>
</svg>`;
}

async function main() {
  const [demo, out] = process.argv.slice(2);
  fs.mkdirSync(path.join(out, 'frames'), { recursive: true });
  fs.mkdirSync(path.join(out, 'sheet'), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(demo));
  await page.evaluate(() => document.fonts.ready);
  const spec = await page.evaluate(() => {
    const s = document.querySelector('[data-measure]');
    return { duration: Number(s.dataset.duration), easing: s.dataset.easing, key: s.dataset.measure, title: document.title };
  });

  const measure = () => page.evaluate(() => {
    const el = document.querySelector('[data-measure]');
    const r = el.getBoundingClientRect();
    return { x: r.x, y: r.y, w: r.width, h: r.height, o: Number(getComputedStyle(el).opacity) };
  });
  // A transition seeked to its very end finishes and leaves getAnimations(), so seeks use
  // the references kept at play() and stop just short of the end.
  const seek = (ms) => page.evaluate((ms) => {
    for (const a of window.__anims) a.currentTime = Math.min(ms, a.effect.getTiming().duration - 0.01);
  }, ms);

  let n = 0;
  const shot = () => page.screenshot({ path: path.join(out, 'frames', `${String(n++).padStart(4, '0')}.png`) });

  const before = await measure();
  for (let ms = 0; ms < PRE_MS; ms += 1000 / FPS) await shot();
  await page.evaluate(() => {
    window.play();
    window.__anims = document.getAnimations();
    for (const a of window.__anims) a.pause();
  });
  await seek(spec.duration);
  const after = await measure();
  const key = spec.key;
  const span = after[key] - before[key];

  const samples = [];
  const step = 1000 / FPS;
  for (let ms = 0; ms <= spec.duration + 0.01; ms += step) {
    await seek(ms);
    samples.push({ t: ms, p: ((await measure())[key] - before[key]) / span });
    await shot();
  }
  for (let ms = 0; ms < HOLD_MS; ms += step) await shot();

  for (let i = 0; i < SHEET_FRAMES; i++) {
    const ms = (spec.duration * i) / (SHEET_FRAMES - 1);
    await seek(ms);
    await page.evaluate((label) => {
      const tag = document.createElement('div');
      tag.id = 'sheet-label';
      tag.textContent = label;
      tag.style.cssText = 'position:fixed;left:8px;top:6px;font:600 22px/1 sans-serif;color:#111;background:#fff;padding:3px 6px;border-radius:4px;z-index:9999';
      document.body.append(tag);
    }, `${Math.round(ms)} ms`);
    await page.screenshot({ path: path.join(out, 'sheet', `${String(i).padStart(2, '0')}.png`) });
    await page.evaluate(() => document.getElementById('sheet-label').remove());
  }

  const fn = curve(spec.easing);
  const planned = Array.from({ length: 101 }, (_, i) => ({ t: (spec.duration * i) / 100, p: fn(i / 100) }));
  const names = { x: 'left edge', y: 'top edge', w: 'width', h: 'height', o: 'opacity' };
  const title = `${spec.title}: ${names[key]} over ${spec.duration} ms, ${spec.easing}`;
  await page.setViewportSize({ width: 480, height: 200 });
  await page.setContent(plotSvg(samples, planned, title));
  await page.screenshot({ path: path.join(out, 'plot.png') });
  fs.writeFileSync(path.join(out, 'samples.json'), JSON.stringify({ ...spec, measured: key, samples }, null, 1));
  await browser.close();
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
