#!/usr/bin/env bash
# Build the SierraVault Quartz (v5 / community) site for Cloudflare Workers.
set -euo pipefail
VAULT_SRC="${VAULT_SRC:-vault}"

rm -rf content; mkdir content; cp -R "$VAULT_SRC"/. content/; rm -rf content/.obsidian
mkdir -p quarantine
node sanitize-frontmatter.mjs content/ quarantine

# Prepend the release year to game titles so the nav shows/sorts by year
node prefix-year.mjs content

# Make the Welcome page the real site index so "/" is a first-class page (graph
# view + OG previews resolve against the root node). Keep aliases so [[Welcome]]
# links and the old /welcome URL still resolve. Also: absolute logo path +
# last-synced footer.
node -e '
const fs=require("fs"), src="content/Welcome.md", dst="content/index.md";
let s=fs.readFileSync(src,"utf8");
s=s.replace(/src="sg-logo-roger-graham-400x400\.webp"/g,"src=\"/static/sg-logo-roger-graham-400x400.webp\"");
s=s.replace(/\n%%GENERATED%%[\s\S]*$/,"");
if(/^---\n/.test(s)) s=s.replace(/^(---\n[\s\S]*?\n)---\n/, (m,fm)=> /\naliases:/.test(fm) ? m : fm+"aliases: [Welcome, welcome]\n---\n");
else s="---\naliases: [Welcome, welcome]\n---\n"+s;
const ts=new Date().toLocaleString("en-US",{timeZone:"America/Denver",dateStyle:"long",timeStyle:"short"});
s+="\n%%GENERATED%%\n\n---\n*Last synced from GitHub · "+ts+"*\n";
fs.writeFileSync(dst,s); fs.unlinkSync(src);
'

npx quartz plugin install     # v5: fetch remote plugins to .quartz/

# folder-page's `sort` option is a raw fn; let it also accept a string (our
# config passes a release-year sort so game listings are in chronological order)
perl -i -pe 's/const sorter = sort \?\?/const sorter = (typeof sort==="string"?(0,eval)("("+sort+")"):sort) ??/' .quartz/plugins/folder-page/dist/index.js .quartz/plugins/folder-page/src/components/PageList.tsx

npx quartz build

# crawl-links resolves internal link targets with the *uncollapsed* slugify, but
# pages live at collapsed slugs (see quartz/util/path.ts). Collapse dash-runs
# inside href/data-slug attributes so internal links + hover popovers resolve
# instead of 404ing. Safe: no page slug or asset filename contains "--".
find public -name '*.html' -type f -print0 \
  | xargs -0 perl -i -pe 's/((?:href|data-slug)=")([^"]*)"/my($a,$b)=($1,$2);$b=~s{-{2,}}{-}g;$a.$b.chr(34)/ge'

# ambiguous wikilinks (entity in >1 folder) resolve to a bare /slug that 404s;
# emit redirect stubs to the canonical page
node generate-redirect-stubs.mjs

# graph edges: remap contentIndex link targets to real (collapsed, full-path) slugs
node fix-graph-links.mjs
