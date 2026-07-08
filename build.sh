#!/usr/bin/env bash
# Build the SierraVault Quartz (v5 / community) site for Cloudflare Workers.
set -euo pipefail
VAULT_SRC="${VAULT_SRC:-vault}"

rm -rf content; mkdir content; cp -R "$VAULT_SRC"/. content/; rm -rf content/.obsidian
mkdir -p quarantine
node sanitize-frontmatter.mjs content/ quarantine

# Welcome page: absolute logo path + last-synced footer
node -e '
const fs=require("fs"), p="content/Welcome.md";
let s=fs.readFileSync(p,"utf8");
s=s.replace(/src="sg-logo-roger-graham-400x400\.webp"/g,"src=\"/static/sg-logo-roger-graham-400x400.webp\"");
s=s.replace(/\n%%GENERATED%%[\s\S]*$/,"");
const ts=new Date().toLocaleString("en-US",{timeZone:"America/Denver",dateStyle:"long",timeStyle:"short"});
s+="\n%%GENERATED%%\n\n---\n*Last synced from GitHub · "+ts+"*\n";
fs.writeFileSync(p,s);
'

npx quartz plugin install     # v5: fetch remote plugins to .quartz/
npx quartz build
cp public/welcome.html public/index.html
