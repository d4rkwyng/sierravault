#!/bin/bash
# Rebuild the self-hosted SierraVault mirror (mirror.sierravault.net) when the
# GitHub repo changes. Runs from wherever the repo is checked out.
#   cron: */5 * * * * /var/www/mirror.sierravault.net/mirror-rebuild.sh
set -uo pipefail

SITE="$(cd "$(dirname "$0")" && pwd)"
LOG="$SITE/rebuild.log"
cd "$SITE" || exit 1

# one rebuild at a time — a build takes longer than the 5-min cron interval
# under load, and overlapping runs share content/ and public/
exec 200>"$SITE/.rebuild.lock"
flock -n 200 || exit 0

git fetch origin main --quiet 2>/dev/null || exit 0
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] && exit 0

echo "$(date '+%F %T') - rebuilding $(git rev-parse --short HEAD) -> $(git rev-parse --short origin/main)" >> "$LOG"
git reset --hard origin/main --quiet >> "$LOG" 2>&1
npm ci --no-audit --no-fund >> "$LOG" 2>&1 || { echo "$(date '+%F %T') - npm ci failed, skipping build" >> "$LOG"; exit 1; }
./build.sh >> "$LOG" 2>&1
chown -R www-data:www-data "$SITE" 2>/dev/null
echo "$(date '+%F %T') - done ($(git rev-parse --short HEAD))" >> "$LOG"
