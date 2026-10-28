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

# Debounce: the vault gets bursts of commits (40-67 a day). If the newest commit is
# under DEBOUNCE_S old, wait for the next cron run so a burst builds once, unless
# the mirror is already MAX_STALE_S behind (then build anyway).
DEBOUNCE_S="${DEBOUNCE_S:-240}"
MAX_STALE_S="${MAX_STALE_S:-1800}"
now=$(date +%s)
newest=$(git log -1 --format=%ct origin/main)
last_build=$(cat "$SITE/.last-build" 2>/dev/null || echo 0)
if [ $((now - newest)) -lt "$DEBOUNCE_S" ] && [ $((now - last_build)) -lt "$MAX_STALE_S" ]; then
    exit 0
fi

echo "$(date '+%F %T') - rebuilding $(git rev-parse --short HEAD) -> $(git rev-parse --short origin/main)" >> "$LOG"
git reset --hard origin/main --quiet >> "$LOG" 2>&1
npm ci --no-audit --no-fund >> "$LOG" 2>&1 || { echo "$(date '+%F %T') - npm ci failed, skipping build" >> "$LOG"; exit 1; }
# Build into a fresh release dir, never into what is being served: Quartz empties its
# output dir before emitting ~2,900 files, which 404'd the mirror for about a minute on
# every rebuild (Uptime Kuma flapped 35x from 2026-10-27). public is a symlink to the
# current release (Caddy serves /var/www/mirror.sierravault.net/public by path); after a
# successful build it is repointed with one rename(2) of a new symlink over it, so there
# is no moment without a site. The last KEEP_RELEASES releases are kept.
MV="${MV:-mv}"   # GNU mv (-T); tests on macOS pass MV=gmv
KEEP_RELEASES="${KEEP_RELEASES:-2}"
mkdir -p "$SITE/releases"
rm -rf "$SITE/public.new" "$SITE/public.old" "$SITE/public.tmp"   # leftovers of older versions
REL="releases/$(git rev-parse --short HEAD)-$(date +%s)"
QUARTZ_OUT="$REL" ./build.sh >> "$LOG" 2>&1
build_status=$?
if [ "$build_status" -eq 0 ] && [ -f "$SITE/$REL/index.html" ]; then
    chown -R www-data:www-data "$SITE/$REL" 2>/dev/null
    # One-time migration: a real public/ dir (before this version) becomes a release, so
    # the symlink can replace it. Only this first swap has a sub-millisecond gap.
    if [ -d "$SITE/public" ] && [ ! -L "$SITE/public" ]; then
        $MV "$SITE/public" "$SITE/releases/legacy-$(date +%s)"
    fi
    ln -sfn "$REL" "$SITE/public.tmp" && $MV -T "$SITE/public.tmp" "$SITE/public"
    swap_status=$?
    # Prune: keep the newest KEEP_RELEASES (by mtime), never the one being served.
    current="$(readlink "$SITE/public")"
    ls -1dt "$SITE"/releases/*/ 2>/dev/null | tail -n +$((KEEP_RELEASES + 1)) | while read -r old; do
        [ "releases/$(basename "$old")" = "$current" ] || rm -rf "$old"
    done
    date +%s > "$SITE/.last-build"
    chown -R www-data:www-data "$SITE" 2>/dev/null
    if [ "$swap_status" -ne 0 ]; then
        echo "$(date '+%F %T') - SWAP FAILED ($(git rev-parse --short HEAD)): built $REL but public still points at $current" >> "$LOG"
        exit 1
    fi
    echo "$(date '+%F %T') - done ($(git rev-parse --short HEAD), serving $current)" >> "$LOG"
else
    rm -rf "${SITE:?}/$REL"
    chown -R www-data:www-data "$SITE" 2>/dev/null
    echo "$(date '+%F %T') - BUILD FAILED ($(git rev-parse --short HEAD), exit $build_status) - public left as it was" >> "$LOG"
    exit 1
fi
