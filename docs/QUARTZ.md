# How SierraVault is built & hosted

This is a maintainer's reference for the machinery behind [sierravault.net](https://sierravault.net) — how the site is built, why the build does the odd things it does, and how it's deployed. If you just want to add or edit content, you don't need any of this; edit the Markdown under `vault/` and push. This document is for the person who has to touch the build.

## Overview

SierraVault runs on **Quartz v5** — specifically the [quartz-community](https://github.com/quartz-community) fork, whose plugins are fetched from GitHub at build time. Unlike the old setup, **nothing is cloned from an external Quartz repo**: the vault content, the Quartz framework, the build script, and the deploy config all live in **this one repository**. The site was migrated off **Obsidian Publish**; `src/worker.js` exists to keep the old Obsidian Publish URLs working.

The live site is hosted on **Cloudflare Workers** and **auto-deploys on every push to `main`** (Cloudflare Workers Build runs the same `build.sh` you run locally). A **self-hosted mirror** at [mirror.sierravault.net](https://mirror.sierravault.net) rebuilds from the same repo on a homelab box.

Key files:

| File | Role |
|------|------|
| `vault/` | The source content (Obsidian vault). Never modified by the build. |
| `quartz/` | The Quartz v5 framework (theme + local overrides). |
| `quartz.config.yaml` | Quartz configuration: theme, plugins, link resolution. |
| `build.sh` | The whole build pipeline (vault → `public/`). |
| `sanitize-frontmatter.mjs` | Cleans bad YAML frontmatter before the build. |
| `prefix-year.mjs` | Prepends release years to game titles for nav ordering. |
| `generate-redirect-stubs.mjs` | Emits redirect stubs for ambiguous wikilinks. |
| `src/worker.js` | Cloudflare Worker: redirects old Obsidian Publish URLs. |
| `wrangler.jsonc` | Cloudflare Workers config (Worker + static-asset binding). |
| `mirror-rebuild.sh` | Cron rebuild for the self-hosted mirror. |

## Local build

```bash
npm ci
./build.sh          # emits ./public
```

`build.sh` produces the full static site in `./public` — the exact bytes Cloudflare serves.

For a live-reloading local preview while editing:

```bash
npx quartz build --serve
```

Note that `--serve` runs a plain Quartz build; it does **not** run the `build.sh` pipeline, so the year-prefixing, the Welcome→index rewrite, the dash-collapsing pass, and the redirect stubs won't be present in the preview. For a faithful check of the deployed output, run `./build.sh` and serve `public/` with any static file server.

## The `build.sh` pipeline

`build.sh` is the source of truth for how the site is produced. Each step exists to work around a specific Quartz behavior; the comments below explain the *why*, not just the *what*.

### 1. Copy `vault/` into `content/`

```bash
rm -rf content; mkdir content; cp -R "$VAULT_SRC"/. content/; rm -rf content/.obsidian
```

Quartz builds from `content/`. The vault is copied there (Obsidian settings stripped) so the source vault is never mutated. `content/` is gitignored — it's a disposable build artifact.

Because `content/` is gitignored, two Quartz behaviors have to be neutralized so the copied content is actually processed: **globby's gitignore handling** and **`build.ts`'s `gitIgnoredMatcher`** would otherwise skip everything under `content/`. Those are patched out (see `quartz/` overrides) so the gitignored build copy still gets built.

### 2. `sanitize-frontmatter.mjs`

```bash
node sanitize-frontmatter.mjs content/ quarantine
```

Dedupes and quarantines bad YAML frontmatter before the build. Malformed or duplicate-keyed frontmatter can crash the parse or silently drop pages; anything unfixable is moved to `quarantine/` so the build proceeds cleanly rather than failing on one bad file.

### 3. `prefix-year.mjs`

```bash
node prefix-year.mjs content
```

Prepends each game's `release_year` to its `title` (`"King's Quest"` → `"1984 - King's Quest"`). **Why:** the explorer nav is built client-side from an index that doesn't carry `release_year`, so it can't sort or label by year on its own. Baking the year into the title is the only way to get the nav to display games chronologically. This runs on the `content/` copy only — the source `vault/` titles are untouched.

### 4. Build `Welcome.md` as `content/index.md`

The script rewrites `content/Welcome.md` into `content/index.md`, adding `aliases: [Welcome, welcome]` to its frontmatter (and fixing the logo path + stamping a "last synced" footer).

**Why not just copy the homepage to `index.html`?** Quartz's graph view resolves the *current node* from the URL. A byte-copied homepage has no corresponding root node in the graph, so `/` rendered an **empty graph** (and OG previews had nothing to resolve against). Building Welcome *as* the real index gives `/` a first-class page node, which fixes both the graph and the OG image previews.

The `aliases: [Welcome, welcome]` keep the old identifiers working: `[[Welcome]]` wikilinks still resolve, and the old `/welcome` URL 301-redirects to `/` (via the `alias-redirects` plugin).

### 5. Install plugins, then patch `folder-page`

```bash
npx quartz plugin install     # v5: fetch remote plugins to .quartz/
perl -i -pe 's/const sorter = sort \?\?/.../' .quartz/plugins/folder-page/dist/index.js ...
```

`quartz plugin install` fetches the quartz-community plugins into `.quartz/`. The `perl` patch then edits `folder-page`'s compiled output so its `sort` option **also accepts a string**. Quartz's schema expects `sort` to be a raw function, but the config is YAML, so the release-year sort is passed as a *string* (see `quartz.config.yaml` → `folder-page.options.sort`). The patch makes the plugin `eval` a string sorter, so game listing pages come out in chronological (release-year) order.

### 6. `npx quartz build`

The actual Quartz build, emitting HTML into `public/`.

### 7. Collapse dash-runs in emitted links

```bash
find public -name '*.html' -type f -print0 \
  | xargs -0 perl -i -pe 's/((?:href|data-slug)=")([^"]*)"/.../ge'
```

**Why this exists** — game filenames contain `" - "` (e.g. `1984 - King's Quest - Quest for the Crown.md`). Quartz's `slugify` turns each `" - "` into `"---"`. For cleaner URLs, the local override in `quartz/util/path.ts` collapses those dash-runs down to a single `-` when generating **page slugs**. But the `crawl-links` plugin resolves link **targets** using the *uncollapsed* slugify — so the emitted `href`/`data-slug` values point at the long `---` form while the pages actually live at the collapsed `-` form. Result: internal links and hover popovers would 404.

This post-build pass collapses `-{2,}` runs inside `href` and `data-slug` attributes so the emitted links match where the pages really are. It's safe because no real page slug or asset filename contains `--`.

### 8. `generate-redirect-stubs.mjs`

```bash
node generate-redirect-stubs.mjs
```

Some entities exist in **more than one folder** — e.g. Dynamix appears under both `developers/` and `publishers/`. A `[[Dynamix]]` wikilink is then ambiguous and can resolve to a bare `/dynamix` that doesn't exist as a page, 404ing. This script walks `public/`, finds every internal link that lands on a missing page, and if a real page with that basename exists elsewhere, writes a small meta-refresh + canonical **redirect stub** at the broken location pointing to the canonical page (preferring developer > publisher > designer > series > games > …).

## `markdownLinkResolution: absolute`

In `quartz.config.yaml`, the `crawl-links` plugin is configured with `markdownLinkResolution: absolute`. The default, `shortest`, emitted **bare slugs** that 404'd when the same basename existed across folders. `absolute` resolves links using full paths from the site root, which avoids the cross-folder collisions. (The redirect stubs above clean up the residual ambiguous cases.)

## `src/worker.js` — the edge redirector

Old links posted before the migration (from **Obsidian Publish**) use **capitalized top-level folders** and `+` for spaces, e.g.:

```
/Games/King's+Quest/1984+-+King's+Quest+-+Quest+for+the+Crown
```

Quartz slugs are lowercase and single-dashed:

```
/games/king's-quest/1984-king's-quest-quest-for-the-crown
```

The Worker guards on a leading capital letter (`/^\/[A-Z]/`). If matched, it lowercases the path, converts `&` → `-and-`, `+` → `-` (preserving literal `+`), collapses dash-runs, and **301-redirects** to the new slug. **New (already-lowercase) URLs don't match the guard**, so they fall straight through to the static assets via the `ASSETS` binding.

`wrangler.jsonc` wires this up: `main` is `src/worker.js`, and the `assets` block binds the built `./public` directory as `ASSETS` with `not_found_handling: "404-page"`. So the Worker runs on every request, redirects the legacy URLs, and serves the static site for everything else.

## Deploy (Cloudflare Workers)

Deployment is automatic. **Cloudflare Workers Build** is configured to run:

```bash
npm ci && ./build.sh
npx wrangler deploy
```

Pushing to **`main`** triggers a build and deploy — no manual step. `wrangler deploy` uploads both the Worker (`src/worker.js`) and the static assets (`./public`).

## Self-hosted mirror (mirror.sierravault.net)

A secondary mirror runs on a homelab box, served by **Caddy** from the built `public/` directory. Setup is just: clone the repo on the box, `npm ci`, `./build.sh`, and point Caddy at `public/`.

`mirror-rebuild.sh` keeps it current. It runs from the repo checkout on a cron (every 5 minutes):

```
*/5 * * * * /var/www/mirror.sierravault.net/mirror-rebuild.sh
```

Each run fetches `origin/main` and **exits immediately if HEAD already matches** — so it only rebuilds when the repo actually changed. On a change it does `git reset --hard origin/main`, `npm ci`, `./build.sh`, and `chown`s the output to `www-data`, logging to `rebuild.log`. It's the same `build.sh` pipeline as production, so the mirror is byte-for-byte equivalent to the Cloudflare site.

---

*This is an unofficial fan archive. All trademarks belong to their respective owners. Quartz is by [Jacky Zhao](https://quartz.jzhao.xyz/); this site uses the [quartz-community](https://github.com/quartz-community) v5 fork.*
