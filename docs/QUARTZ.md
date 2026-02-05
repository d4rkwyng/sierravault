# Hosting SierraVault with Quartz

[Quartz](https://quartz.jzhao.xyz/) is a static site generator for Markdown files with built-in support for Obsidian features like wiki-links and backlinks. This guide explains how to self-host a mirror of SierraVault using Quartz.

## Quick Start

```bash
# Clone Quartz
git clone https://github.com/jackyzha0/quartz.git
cd quartz

# Install dependencies
npm install

# Clone SierraVault into content/
rm -rf content
git clone https://github.com/d4rkwyng/sierravault.git repo
cp -r repo/vault content

# Build the site
npx quartz build

# Preview locally
npx quartz build --serve
```

The site will be available at `http://localhost:8080`.

## Configuration

Edit `quartz.config.ts`:

```typescript
const config: QuartzConfig = {
  configuration: {
    pageTitle: "SierraVault",
    pageTitleSuffix: "",
    enableSPA: true,
    enablePopovers: true,
    baseUrl: "your-domain.com",
    // Only .obsidian needs exclusion - vault/ contains only publishable content
    ignorePatterns: [".obsidian"],
    defaultDateType: "modified",
    theme: {
      // ... your theme settings
    },
  },
}
```

> **Note:** Since the restructure, only the `vault/` folder is synced to content. Files like `README.md`, `CLAUDE.md`, `.github/`, etc. remain at the repo root and don't need to be excluded.

## Favicon Setup

SierraVault includes favicons in `vault/Images/favicon/`. To use them:

1. Copy favicon files to Quartz's `quartz/static/` folder:
```bash
cp content/Images/favicon/* quartz/static/
```

2. Or reference them in your HTML head (edit `quartz/components/Head.tsx`):
```tsx
<link rel="icon" type="image/x-icon" href="/static/favicon.ico" />
<link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png" />
<link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png" />
```

Available favicon sizes:
- `favicon.ico`
- `favicon-16x16.png`
- `favicon-32x32.png`
- `favicon-192x192.png`
- `favicon-256x256.png`
- `favicon-512x512.png`

## Auto-Update Script

To keep your mirror in sync with the main repo:

```bash
#!/bin/bash
# /path/to/auto-rebuild.sh

SITE_DIR="/var/www/your-quartz-site"
REPO_DIR="$SITE_DIR/repo"
CONTENT_DIR="$SITE_DIR/content"

# Pull latest changes
cd "$REPO_DIR"
git fetch origin main --quiet
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    # Reset to match remote (this is a read-only build copy)
    git reset --hard origin/main --quiet

    # Sync vault/ to content/ (exclude .obsidian settings)
    rsync -a --delete --exclude='.obsidian' "$REPO_DIR/vault/" "$CONTENT_DIR/"

    # Copy favicons to static folder
    cp "$CONTENT_DIR/Images/favicon/"* "$SITE_DIR/quartz/static/" 2>/dev/null

    # Rebuild
    cd "$SITE_DIR"
    rm -rf .quartz-cache public
    npx quartz build

    # Fix index (Welcome.html is the homepage)
    cd "$SITE_DIR/public" && ln -sf Welcome.html index.html
fi
```

Add to crontab (runs every 5 minutes):
```bash
*/5 * * * * /path/to/auto-rebuild.sh
```

## Repository Structure

After the 2026 restructure:

```
sierravault/
├── vault/                    # ← Sync THIS folder to content/
│   ├── Games/
│   ├── Designers/
│   ├── Images/
│   │   ├── favicon/          # Favicon files
│   │   └── logo/             # Logo files
│   ├── Welcome.md            # Homepage
│   └── ...
├── scripts/                  # Scoring tools (not published)
├── templates/                # Page templates (not published)
├── CLAUDE.md                 # AI instructions (not published)
└── README.md                 # Repo readme (not published)
```

Only `vault/` contains publishable content. Everything else stays at the repo root.

## Deployment Options

- **Static hosting:** Netlify, Vercel, GitHub Pages, Cloudflare Pages
- **Self-hosted:** Nginx, Apache, Caddy serving the `public/` folder
- **Docker:** See [Quartz documentation](https://quartz.jzhao.xyz/hosting) for containerized deployment

## Resources

- [Quartz Documentation](https://quartz.jzhao.xyz/)
- [SierraVault Main Site](https://sierravault.net)
- [Quartz Mirror](https://quartz.sierravault.net)

---

*This is an unofficial fan archive. All trademarks belong to their respective owners.*
