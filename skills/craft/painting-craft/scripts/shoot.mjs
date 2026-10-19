// Screenshot a page the way the user sees it: several viewports, a scroll position, optional repeats for moving parts.
// Playwright resolves from the current directory, so run this from a folder where `npm i playwright` has been done.
// usage: node shoot.mjs --url http://127.0.0.1:8765/portfolio.html --out shots/city [--size 1600x1000 --size 390x844]
//        [--section '#games' --at 0.5 | --y 2400] [--wait 5000] [--dpr 2] [--repeat 3 --every 700]
import { createRequire } from 'node:module';
const { chromium } = createRequire(process.cwd() + '/')('playwright');

const args = process.argv.slice(2), opt = { size: [] };
for (let i = 0; i < args.length; i += 2) { const k = args[i].replace(/^--/, ''), v = args[i + 1]; k === 'size' ? opt.size.push(v) : (opt[k] = v); }
if (!opt.url || !opt.out) { console.error('need --url and --out'); process.exit(2); }
const sizes = opt.size.length ? opt.size : ['1600x1000', '390x844'];

const browser = await chromium.launch();
for (const size of sizes) {
  const [W, H] = size.split('x').map(Number);
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: +(opt.dpr || 2), reducedMotion: 'no-preference' });
  page.on('pageerror', (e) => console.log(`[${size}] PAGEERROR ${e.message}`));
  page.on('console', (m) => m.type() === 'error' && console.log(`[${size}] console.error ${m.text()}`));
  await page.goto(opt.url, { waitUntil: 'networkidle' });
  // --at is a fraction of the section's scrollable span: 0 is its first screen, 1 its last (sticky scrollytelling).
  await page.evaluate(({ section, at, y }) => {
    if (section) { const s = document.querySelector(section); if (!s) throw new Error(`no ${section}`); scrollTo({ top: s.getBoundingClientRect().top + scrollY + +(at || 0) * Math.max(0, s.offsetHeight - innerHeight), behavior: 'auto' }); }
    else if (y) scrollTo({ top: +y, behavior: 'auto' });
  }, opt);
  await page.waitForTimeout(+(opt.wait || 5000));
  const n = +(opt.repeat || 1);
  for (let i = 0; i < n; i++) {
    const path = `${opt.out}-${size}${n > 1 ? `-${i}` : ''}.png`;
    await page.screenshot({ path });
    console.log(`[${size}] wrote ${path}`);
    if (i < n - 1) await page.waitForTimeout(+(opt.every || 700));
  }
  await page.close();
}
await browser.close();
