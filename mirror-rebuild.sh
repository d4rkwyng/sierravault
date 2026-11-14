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
# Rebuild whenever origin/main differs from the last commit that BUILT
# successfully, not from HEAD: the build resets HEAD to origin/main before it
# runs, so comparing against HEAD meant a failed build was never retried.
# No .last-good-sha yet (first run of this version) also means: build.
target="$(git rev-parse origin/main)"
last_good="$(cat "$SITE/.last-good-sha" 2>/dev/null || true)"
[ "$target" = "$last_good" ] && exit 0

# A commit that already failed (all attempts) is retried at most every
# FAILED_RETRY_S, so a deterministic failure (e.g. a page with broken
# frontmatter, which build.sh refuses) doesn't rebuild every 5 minutes.
FAILED_RETRY_S="${FAILED_RETRY_S:-1800}"
read -r failed_sha failed_at 2>/dev/null < "$SITE/.last-failed" || true
if [ "${failed_sha:-}" = "$target" ] && [ $(( $(date +%s) - ${failed_at:-0} )) -lt "$FAILED_RETRY_S" ]; then
    exit 0
fi

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

echo "$(date '+%F %T') - rebuilding ${last_good:0:7}${last_good:+ }(HEAD $(git rev-parse --short HEAD)) -> $(git rev-parse --short "$target")" >> "$LOG"
git reset --hard "$target" --quiet >> "$LOG" 2>&1
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
# npm ci + build, retried BUILD_RETRIES times after RETRY_WAIT_S on failure
# (a network blip during npm ci or the plugin install shouldn't cost a cycle).
BUILD_RETRIES="${BUILD_RETRIES:-1}"
RETRY_WAIT_S="${RETRY_WAIT_S:-60}"
attempt=0
while :; do
    attempt=$((attempt + 1))
    REL="releases/$(git rev-parse --short HEAD)-$(date +%s)"
    if npm ci --no-audit --no-fund >> "$LOG" 2>&1; then
        QUARTZ_OUT="$REL" ./build.sh >> "$LOG" 2>&1
        build_status=$?
    else
        echo "$(date '+%F %T') - npm ci failed (attempt $attempt)" >> "$LOG"
        build_status=1
    fi
    [ "$build_status" -eq 0 ] && [ -f "$SITE/$REL/index.html" ] && break
    rm -rf "${SITE:?}/$REL"
    [ "$attempt" -gt "$BUILD_RETRIES" ] && break
    echo "$(date '+%F %T') - build attempt $attempt failed (exit $build_status), retrying in ${RETRY_WAIT_S}s" >> "$LOG"
    sleep "$RETRY_WAIT_S"
done
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
    git rev-parse HEAD > "$SITE/.last-good-sha"
    rm -f "$SITE/.last-failed"
    chown -R www-data:www-data "$SITE" 2>/dev/null
    if [ "$swap_status" -ne 0 ]; then
        echo "$(date '+%F %T') - SWAP FAILED ($(git rev-parse --short HEAD)): built $REL but public still points at $current" >> "$LOG"
        exit 1
    fi
    echo "$(date '+%F %T') - done ($(git rev-parse --short HEAD), serving $current)" >> "$LOG"
else
    rm -rf "${SITE:?}/$REL"
    echo "$(git rev-parse HEAD) $(date +%s)" > "$SITE/.last-failed"
    chown -R www-data:www-data "$SITE" 2>/dev/null
    echo "$(date '+%F %T') - BUILD FAILED ($(git rev-parse --short HEAD), exit $build_status, $attempt attempt(s)) - public left as it was; retried after ${FAILED_RETRY_S}s or on the next commit" >> "$LOG"
    exit 1
fi
