#!/usr/bin/env node
// Sanitize markdown frontmatter before Quartz build.
// - Dedupes duplicate top-level YAML keys (keeps the last value)
// - Quarantines files whose frontmatter is still unparseable
// Always exits 0 so the build proceeds.

import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';

const contentDir = process.argv[2];
const quarantineDir = process.argv[3];

if (!contentDir || !quarantineDir) {
  console.error('usage: sanitize-frontmatter.mjs <content-dir> <quarantine-dir>');
  process.exit(2);
}

const FM_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/;
let fixed = 0, quarantined = 0;

function dedupeFrontmatter(fm) {
  const lines = fm.split('\n');
  const lastIndex = new Map();
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^([A-Za-z_][A-Za-z0-9_-]*)\s*:/);
    if (!m) continue;
    const key = m[1];
    if (lastIndex.has(key)) lines[lastIndex.get(key)] = null;
    lastIndex.set(key, i);
  }
  return lines.filter(l => l !== null).join('\n');
}

function walk(dir, base) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) { walk(full, base); continue; }
    if (!entry.name.endsWith('.md')) continue;

    const text = fs.readFileSync(full, 'utf8');
    const m = text.match(FM_RE);
    if (!m) continue;

    const original = m[1];
    try {
      yaml.load(original);
      continue;
    } catch (e) {
      const cleaned = dedupeFrontmatter(original);
      try {
        yaml.load(cleaned);
        const rest = text.slice(m[0].length);
        fs.writeFileSync(full, `---\n${cleaned}\n---\n${rest}`);
        console.log(`FIXED  ${path.relative(base, full)}: ${e.message.split('\n')[0]}`);
        fixed++;
      } catch (e2) {
        const rel = path.relative(base, full);
        const dest = path.join(quarantineDir, rel);
        fs.mkdirSync(path.dirname(dest), { recursive: true });
        fs.renameSync(full, dest);
        console.log(`QUARANTINED ${rel}: ${e2.message.split('\n')[0]}`);
        quarantined++;
      }
    }
  }
}

fs.mkdirSync(quarantineDir, { recursive: true });
for (const entry of fs.readdirSync(quarantineDir, { withFileTypes: true })) {
  fs.rmSync(path.join(quarantineDir, entry.name), { recursive: true, force: true });
}

walk(contentDir, contentDir);
console.log(`sanitize: fixed=${fixed} quarantined=${quarantined}`);
