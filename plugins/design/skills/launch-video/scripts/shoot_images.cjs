// usage: node shoot_images.cjs PAGE.html OUT_DIR '{"youtube-thumb":[1280,720],"link-preview":[1200,630]}'
// Opens PAGE.html?v=<variant> at each size and saves OUT_DIR/<variant>-<w>x<h>.png. Needs playwright
// (set PLAYWRIGHT_PATH to its module path if it is not resolvable from here).
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
const path = require("node:path");
const [page, outDir, sizesJson] = process.argv.slice(2);
if (!page || !outDir || !sizesJson) { console.log("usage: node shoot_images.cjs PAGE.html OUT_DIR '{\"variant\":[w,h]}'"); process.exit(1); }
const sizes = JSON.parse(sizesJson);
(async () => {
  const b = await chromium.launch(); let i = 0;
  for (const [v, [w, h]] of Object.entries(sizes)) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto(`file://${path.resolve(page)}?v=${v}`);
    await p.evaluate(() => document.fonts.ready);
    const out = path.join(outDir, `${v}-${w}x${h}.png`);
    await p.screenshot({ path: out }); await p.close();
    console.log(`[${++i}/${Object.keys(sizes).length}] ✔ ${out}`);
  }
  await b.close();
})();
