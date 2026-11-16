// Rendert transparente Overlay-PNGs (Hook-Banner oben + End-Karte) für die Kurz-Clips.
// Nutzung: node overlay.mjs jobs.json   (jobs: [{out, kind: "hook"|"end", l1, l2}])
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const dir = path.dirname(new URL(import.meta.url).pathname);
const V = path.join(dir, '..', 'french-basics', 'vendor');
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const b64 = f => fs.readFileSync(path.join(V, f)).toString('base64');
const css = `@font-face{font-family:Lucky;src:url(data:font/woff2;base64,${b64('luckiest-guy.woff2')}) format('woff2')}
@font-face{font-family:Fredoka;font-weight:700;src:url(data:font/woff2;base64,${b64('fredoka-700.woff2')}) format('woff2')}
html,body{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden}
.hook{position:absolute;left:40px;right:40px;top:36px;height:262px;background:#fff;border:10px solid #1d2b53;border-radius:50px;
 box-shadow:0 14px 0 rgba(29,43,83,.3);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 30px;box-sizing:border-box}
.l1{font-family:Lucky;color:#1d2b53;line-height:1.05}
.l2{font-family:Fredoka;font-weight:700;color:#e63946;font-size:46px;margin-top:10px}
.end{position:absolute;inset:0;background:rgba(29,43,83,.82);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.e1{font-family:Lucky;font-size:120px;color:#ffd60a;-webkit-text-stroke:14px #1d2b53;paint-order:stroke fill;line-height:1}
.e2{font-family:Lucky;font-size:80px;color:#fff;margin-top:30px}
.e3{font-family:Fredoka;font-weight:700;font-size:56px;color:#fff;margin-top:30px;opacity:.9}`;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
for (const j of jobs) {
  const body = j.kind === 'hook'
    ? `<div class="hook"><div class="l1" id="l1">${j.l1}</div><div class="l2">${j.l2 || ''}</div></div>`
    : `<div class="end"><div class="e1">${j.l1}</div><div class="e2">@LEARNWITHCOCO</div><div class="e3">${j.l2 || ''}</div></div>`;
  await page.setContent(`<html><head><style>${css}</style></head><body>${body}</body></html>`);
  await page.evaluate(async () => { await document.fonts.load('70px Lucky'); await document.fonts.load('700 40px Fredoka'); await document.fonts.ready; });
  if (j.kind === 'hook') await page.evaluate(() => { // Schrift an Platz anpassen
    const el = document.getElementById('l1'); let fs = 76; el.style.fontSize = fs + 'px';
    while ((el.scrollHeight > 160 || el.scrollWidth > 940) && fs > 40) { fs -= 2; el.style.fontSize = fs + 'px'; }
  });
  await page.screenshot({ path: j.out, omitBackground: true });
}
await browser.close();
console.log('overlays:', jobs.length);
