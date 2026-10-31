#!/usr/bin/env node
/**
 * Drehbuch inline (MIT) – makes one self-contained HTML file.
 *
 *   node inline.mjs page.html [out.html] [--fragment]
 *
 * Replaces <!-- DREHBUCH:CSS --> and <!-- DREHBUCH:JS --> with the engine files,
 * and inlines local <img src>, <link rel=stylesheet href> and <script src> files
 * (images below 1.5 MB become data URIs; videos are left as separate files).
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const engine = path.resolve(here, "../engine");
const [src, outArg] = process.argv.slice(2).filter((a) => !a.startsWith("--"));
if (!src) { console.error("Usage: node inline.mjs page.html [out.html]"); process.exit(2); }
const dir = path.dirname(path.resolve(src));
const out = outArg || src.replace(/\.html?$/i, "") + ".single.html";
let html = fs.readFileSync(src, "utf8");

const css = fs.readFileSync(path.join(engine, "drehbuch.css"), "utf8");
const js = fs.readFileSync(path.join(engine, "drehbuch.js"), "utf8");
html = html.replace("<!-- DREHBUCH:CSS -->", () => `<style>\n${css}\n</style>`);
html = html.replace("<!-- DREHBUCH:JS -->", () => `<script>\n${js}\n</script>`);

const local = (p) => p && !/^(https?:|data:|\/\/|#)/i.test(p);
const mime = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".svg": "image/svg+xml", ".gif": "image/gif", ".avif": "image/avif" };

html = html.replace(/<link\s+[^>]*rel=["']stylesheet["'][^>]*href=["']([^"']+)["'][^>]*>/gi, (m, href) =>
  local(href) && fs.existsSync(path.join(dir, href)) ? `<style>\n${fs.readFileSync(path.join(dir, href), "utf8")}\n</style>` : m);
html = html.replace(/<script\s+[^>]*src=["']([^"']+)["'][^>]*><\/script>/gi, (m, s) =>
  local(s) && fs.existsSync(path.join(dir, s)) ? `<script>\n${fs.readFileSync(path.join(dir, s), "utf8")}\n</script>` : m);
html = html.replace(/(<img\s[^>]*src=["'])([^"']+)(["'])/gi, (m, a, s, b) => {
  const f = path.join(dir, s), ext = path.extname(s).toLowerCase();
  if (!local(s) || !mime[ext] || !fs.existsSync(f) || fs.statSync(f).size > 1.5e6) return m;
  return a + `data:${mime[ext]};base64,` + fs.readFileSync(f).toString("base64") + b;
});

// --fragment: drop <!doctype>, <html>, <head>, <body> wrappers (for hosts that add their own skeleton,
// such as claude.ai artifacts). Keeps <title>, <meta name=description>, styles, links and scripts.
if (process.argv.includes("--fragment")) {
  const head = (html.match(/<head[^>]*>([\s\S]*?)<\/head>/i) || [, ""])[1]
    .replace(/<meta\s+charset[^>]*>\s*/i, "").replace(/<meta\s+name=["']viewport["'][^>]*>\s*/i, "");
  const body = (html.match(/<body[^>]*>([\s\S]*?)<\/body>/i) || [, html])[1];
  html = head.trim() + "\n" + body.trim() + "\n";
}

fs.writeFileSync(out, html);
console.log(`${out} (${(Buffer.byteLength(html) / 1024).toFixed(0)} KB)`);
if (!html.includes("Drehbuch engine v")) console.warn("Warning: engine JS marker not found; add <!-- DREHBUCH:JS --> before your own scripts.");
