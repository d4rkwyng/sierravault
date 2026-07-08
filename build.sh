#!/usr/bin/env bash
# Build the SierraVault Quartz site.
# Replicates the deathstar auto-rebuild pipeline for Cloudflare Workers:
#   fetch content (vault) -> sanitize frontmatter -> fix logo path + timestamp
#   -> quartz build -> make Welcome.html the homepage (/).
# Uses only git/node/npm/cp so it runs on CF's build image and macOS alike.
set -euo pipefail

# Content lives in this same repo at ./vault (combined repo).
VAULT_SRC="${VAULT_SRC:-vault}"

# vault/ -> content/ (fresh copy of the vault's *contents*, drop Obsidian config)
rm -rf content
mkdir content
cp -R "$VAULT_SRC"/. content/
rm -rf content/.obsidian

# Dedupe/quarantine messy YAML so one bad note can't fail the build
mkdir -p quarantine
node sanitize-frontmatter.mjs content/ quarantine

# Welcome page: absolute logo path + a "last synced" footer (portable, node-only)
node -e '
const fs=require("fs"), p="content/Welcome.md";
let s=fs.readFileSync(p,"utf8");
s=s.replace(/src="sg-logo-roger-graham-400x400\.webp"/g,"src=\"/static/sg-logo-roger-graham-400x400.webp\"");
s=s.replace(/\n%%GENERATED%%[\s\S]*$/,"");
const ts=new Date().toLocaleString("en-US",{timeZone:"America/Denver",dateStyle:"long",timeStyle:"short"});
s+="\n%%GENERATED%%\n\n---\n*Last synced from GitHub · "+ts+"*\n";
fs.writeFileSync(p,s);
'

# Build
npx quartz build

# Homepage: / serves the Welcome page
cp public/Welcome.html public/index.html
