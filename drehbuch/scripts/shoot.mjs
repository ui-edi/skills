#!/usr/bin/env node
/**
 * Drehbuch verify (MIT) – scrolls a page step by step and photographs every position.
 *
 *   node shoot.mjs <page.html | http://url> [--out shots] [--step 0.5] [--width 1440 --height 900]
 *                  [--mobile] [--reduced] [--max 80]
 *
 * --mobile   = 390x844, touch, device scale 2
 * --reduced  = prefers-reduced-motion: reduce
 * --step     = scroll distance per shot in viewport heights (default 0.5)
 *
 * Writes <out>/NN.png for every position, <out>/sheet.png (contact sheet) and <out>/report.json.
 * Reports: dead scroll (two consecutive positions that look identical), horizontal overflow,
 * console errors, failed requests, images that did not load, elements cut off at the right edge.
 * Local only: it opens the page you give it and nothing else.
 */
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import crypto from "node:crypto";

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); }
catch { try { ({ chromium } = require("playwright-core")); } catch { console.error("Playwright not found. Run: npm i playwright"); process.exit(2); } }

const argv = process.argv.slice(2);
const flag = (n) => argv.includes(n);
const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 && argv[i + 1] ? argv[i + 1] : d; };
const valued = new Set(["--out", "--step", "--width", "--height", "--max"]);
const target = argv.find((a, i) => !a.startsWith("--") && !valued.has(argv[i - 1]));
if (!target) { console.error("Usage: node shoot.mjs <page.html|url> [--out dir] [--mobile] [--reduced]"); process.exit(2); }

const mobile = flag("--mobile"), reduced = flag("--reduced");
const width = +opt("--width", mobile ? 390 : 1440), height = +opt("--height", mobile ? 844 : 900);
const step = +opt("--step", 0.5), max = +opt("--max", 80);
const out = path.resolve(opt("--out", `shots-${mobile ? "mobile" : "desktop"}${reduced ? "-reduced" : ""}`));
const url = /^https?:|^file:/.test(target) ? target : pathToFileURL(path.resolve(target)).href;
fs.mkdirSync(out, { recursive: true });

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width, height }, deviceScaleFactor: mobile ? 2 : 1, isMobile: mobile, hasTouch: mobile,
  reducedMotion: reduced ? "reduce" : "no-preference",
});
const page = await ctx.newPage();
const errors = [], failed = [];
page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
page.on("pageerror", (e) => errors.push(String(e)));
page.on("requestfailed", (r) => failed.push(r.url()));

await page.goto(url, { waitUntil: "networkidle" }).catch(() => page.goto(url));
await page.waitForTimeout(800);

const total = await page.evaluate(() => document.documentElement.scrollHeight);
const positions = [];
for (let y = 0; y <= total - height + 1 && positions.length < max; y += Math.round(height * step)) positions.push(y);
if (positions[positions.length - 1] < total - height) positions.push(total - height);

const shots = [];
let prevHash = null;
const dead = [];
for (let i = 0; i < positions.length; i++) {
  const y = positions[i];
  await page.evaluate((yy) => window.scrollTo(0, yy), y);
  await page.waitForTimeout(reduced ? 150 : 900);
  const file = path.join(out, String(i).padStart(2, "0") + ".png");
  const buf = await page.screenshot({ path: file });
  const hash = crypto.createHash("md5").update(buf).digest("hex");
  if (prevHash === hash) dead.push({ from: positions[i - 1], to: y });
  prevHash = hash;
  shots.push({ file: path.basename(file), y });
}

const layout = await page.evaluate(() => {
  const vw = document.documentElement.clientWidth;
  const overflowX = document.documentElement.scrollWidth > vw + 1;
  const cut = [];
  document.querySelectorAll("h1,h2,h3,p,a,button,li").forEach((el) => {
    const r = el.getBoundingClientRect();
    if (r.width && r.right > vw + 2 && getComputedStyle(el).position !== "fixed") cut.push((el.textContent || "").trim().slice(0, 40));
  });
  const brokenImgs = [...document.images].filter((im) => im.complete && im.naturalWidth === 0).map((im) => im.src.slice(0, 80));
  return { overflowX, cut: cut.slice(0, 10), brokenImgs };
});

// Contact sheet: all shots in a grid, rendered by the same browser.
const cols = mobile ? 6 : 4;
const thumbW = mobile ? 180 : 340;
const sheetHtml = `<html><body style="margin:0;background:#111;font:12px system-ui;color:#ccc">
<div style="display:grid;grid-template-columns:repeat(${cols},${thumbW}px);gap:8px;padding:8px">
${shots.map((s) => `<figure style="margin:0"><img src="${pathToFileURL(path.join(out, s.file)).href}" style="width:${thumbW}px;display:block;border:1px solid #333"><figcaption>${s.file} · y=${s.y}</figcaption></figure>`).join("")}
</div></body></html>`;
const sheetPath = path.join(out, "sheet.html");
fs.writeFileSync(sheetPath, sheetHtml);
const sheetPage = await browser.newPage({ viewport: { width: cols * (thumbW + 8) + 8, height: 600 } });
await sheetPage.goto(pathToFileURL(sheetPath).href);
await sheetPage.waitForTimeout(300);
await sheetPage.screenshot({ path: path.join(out, "sheet.png"), fullPage: true });

const report = { url, viewport: `${width}x${height}`, reduced, pageHeight: total, shots: shots.length, deadScroll: dead, layout, consoleErrors: errors, failedRequests: failed };
fs.writeFileSync(path.join(out, "report.json"), JSON.stringify(report, null, 2));
await browser.close();

const problems = [];
if (dead.length) problems.push(`${dead.length} dead-scroll step(s): nothing changed between ${dead.map((d) => d.from + "→" + d.to).join(", ")}`);
if (layout.overflowX) problems.push("horizontal overflow: page is wider than the viewport");
if (layout.cut.length) problems.push("cut off at right edge: " + layout.cut.join(" | "));
if (layout.brokenImgs.length) problems.push("images not loaded: " + layout.brokenImgs.join(", "));
if (errors.length) problems.push("console errors: " + errors.slice(0, 5).join(" | "));
if (failed.length) problems.push("failed requests: " + failed.slice(0, 5).join(", "));
console.log(`${shots.length} shots → ${out}/sheet.png`);
console.log(problems.length ? "PROBLEMS:\n- " + problems.join("\n- ") : "No automatic problems found. Now look at sheet.png yourself.");
