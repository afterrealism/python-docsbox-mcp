// Read build/index.html, inline any external <link rel="stylesheet">, and
// strip module preload / script tags so the result is a single self-contained
// HTML file ready to be baked into the binary. Also copies sibling SEO/LLM
// assets (robots.txt, sitemap.xml, llms.txt, llms-full.txt) next to the
// emitted HTML so the Python wheel can ship them as package resources.
import { readFile, writeFile, copyFile } from 'node:fs/promises';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const buildDir = resolve(__dirname, 'build');
const inputPath = join(buildDir, 'index.html');
const outputPath = process.argv[2]
  ? resolve(process.argv[2])
  : join(buildDir, 'index.standalone.html');
const outputDir = dirname(outputPath);
const SEO_ASSETS = ['robots.txt', 'sitemap.xml', 'llms.txt', 'llms-full.txt'];

let html = await readFile(inputPath, 'utf-8');

// Inline <link rel="stylesheet" href="..."> tags.
const linkRe = /<link\s+[^>]*rel=["']stylesheet["'][^>]*>/g;
const hrefRe = /href=["']([^"']+)["']/;
const links = html.match(linkRe) ?? [];
for (const tag of links) {
  const href = tag.match(hrefRe)?.[1];
  if (!href) continue;
  const cleanHref = href.split('?')[0].split('#')[0];
  const cssPath = join(buildDir, cleanHref.replace(/^\/+/, ''));
  try {
    const css = await readFile(cssPath, 'utf-8');
    html = html.replace(tag, `<style>${css}</style>`);
  } catch {
    // Leave tag in place if we cannot resolve it.
  }
}

// Drop modulepreload / script-src tags that point at chunked JS we no longer
// ship, csr=false means no hydration needed.
html = html.replace(/<link\s+[^>]*rel=["']modulepreload["'][^>]*>\s*/g, '');
html = html.replace(/<script[^>]*\bsrc=["'][^"']*\/_app\/[^"']+["'][^>]*>\s*<\/script>\s*/g, '');
html = html.replace(/<script[^>]*\btype=["']module["'][^>]*>[\s\S]*?<\/script>\s*/g, '');

await writeFile(outputPath, html, 'utf-8');
console.log(`wrote ${outputPath} (${html.length} bytes)`);

// Copy SEO / LLM assets so the wheel can ship them as package resources.
for (const name of SEO_ASSETS) {
  const src = join(buildDir, name);
  const dst = join(outputDir, name);
  try {
    await copyFile(src, dst);
    console.log(`copied ${name} -> ${dst}`);
  } catch (err) {
    console.warn(`skipped ${name}: ${err.message}`);
  }
}
