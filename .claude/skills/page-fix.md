---
name: page-fix
description: Score a single SierraVault game page, identify issues, and fix them to reach 100%. Mines research dossiers from the Assets folder for new citations; falls back to web search when no dossier exists.
---

# /page-fix

Repair one SierraVault game page to 100%. Operates on a single page at a time so each commit is reviewable.

## RULE #0 — REAL REFERENCES ONLY (absolute, non-negotiable)

**Never cite a reference unless the source actually exists AND actually contains the claim it is attached to.**

A URL existing in the research dossier is NOT sufficient. The crawler frequently catches navigation shells, 404 pages, and robots-blocked URLs that contain no real content. **Before adding ANY citation to a page, complete step 3a (content verification)** — read the dossier file's `source_significance`, `full_text` length, `extracted_facts`, and `key_quotes`. If `source_significance` says "navigation page only" / "no actual content" — REJECT the source.

For **superlatives** ("best-selling of all time", "first ever") and **numeric specifics** ("16 tables", "$5M budget") — grep `full_text` for the exact phrase or number before citing. If it isn't there, find a source that does support it or weaken the claim. Conservative phrasing over confident phrasing, always.

**A passing score at 100% does NOT mean citations are factually correct.** The scorer validates structure (ref count, no dup URLs); it does not validate truth. Real-reference verification is your job, not the scorer's.

If you cannot find a real source that contains the claim, **stop and ask the user** — do not fabricate, do not propagate the vault's existing claim into a new citation, do not soften the standard.

## Database-trust exception

Established database sites (MobyGames, Wikipedia, PCGamingWiki, IGDB, LaunchBox, Sierra Chest, GameFAQs, Giant Bomb, MyAbandonware) can be cited without per-page WebFetch verification when the claim is plausibly within the database's coverage scope. These sites have editorial review and stable URL schemes, and they frequently use JS-rendered SPAs that the crawler doesn't execute — producing thin `full_text` in the dossier despite having real content at the URL. Empty `source_significance` is the crawler's silence, not a content verdict.

**When you can apply database-trust:**
- Citing a MobyGames `/credits/` subpage for development credits
- Citing a MobyGames `/reviews/` subpage for aggregate reviewer scores
- Citing a Wikipedia game-overview article for genre/year/platform metadata
- Citing a PCGamingWiki entry for system requirements / compatibility notes
- Citing a LaunchBox/IGDB/GameFAQs entry for preservation / database metadata
- Citing Sierra Chest for Sierra-history metadata (box scans, manuals, etc.)

**When you must NOT apply database-trust (verify content first):**
- Dossier explicitly flagged `source_significance` as content-empty/navigation-only/404
- The citation supports a verbatim quoted phrase — grep `full_text` for the exact quote
- The citation supports a specific numeric claim (sales figures, table counts, dollar amounts, exact dates)
- The source is primary-tier (interview, official statement, magazine scan, blog) and the dossier extraction is thin — fetch the URL instead

## Autonomy authorization

Once step 3a content-verification passes for every candidate ref AND the planned edits are either structural fixes or corroborating citations (not factual changes to prose), proceed with edits without further user confirmation. Continue to stop and ask when: (a) any verification fails, (b) a claim must be softened or corrected, (c) a structural fix would change content meaning, (d) a source is primary-tier rather than database-tier and the dossier extraction is thin, (e) the page is `CXL-` or `TBD-` prefixed (different threshold and rules).

## Invocation

`/page-fix <path-or-slug>`

- `/page-fix vault/Games/3D Ultra/1995 - 3-D Ultra Pinball.md` — explicit path
- `/page-fix 3-D Ultra Pinball` — fuzzy filename match
- `/page-fix` (no arg) — pick the lowest-scoring page from `vault_report.json`

## Hard paths

- Vault root: `/Users/woodd/GitHub/sierravault/vault`
- Scorer: `/Users/woodd/Library/Mobile Documents/com~apple~CloudDocs/Assets/sierravault/scripts/ACTIVE/consistency_check.py`
- Research dossiers: `/Users/woodd/Library/Mobile Documents/com~apple~CloudDocs/Assets/sierravault/Research/games/<slug>/`
- Cached report: `/Users/woodd/GitHub/sierravault/vault_report.json`

The scorer requires `--vault /Users/woodd/GitHub/sierravault/vault/Games` (its built-in default points to a stale path).

## Procedure

### 1. Locate the page
- Explicit path → use as-is.
- Slug → `find /Users/woodd/GitHub/sierravault/vault/Games -iname "*<slug>*.md"`. If multiple hits, ask the user.
- No arg → `python3 -c "import json; r=json.load(open('vault_report.json')); print(r['pages'][0]['filename'], r['pages'][0]['series'])"`, then build the full path.

### 2. Score the page
```bash
SCRIPT="/Users/woodd/Library/Mobile Documents/com~apple~CloudDocs/Assets/sierravault/scripts/ACTIVE/consistency_check.py"
python3 "$SCRIPT" \
  --vault /Users/woodd/GitHub/sierravault/vault/Games \
  --file "<absolute-page-path>"
```
Capture: score, threshold, ref_count, the full issue list with severity + points lost.

### 3. Find the research dossier
The slug is the filename with year stripped, lowercased, non-alphanum → hyphens:
- `1995 - 3-D Ultra Pinball.md` → `3-d-ultra-pinball`
- `1989 - Space Quest III - The Pirates of Pestulon.md` → `space-quest-iii-the-pirates-of-pestulon`

Check `Assets/Research/games/<slug>/`. Useful files inside:
- `_consolidated.json` — merged dossier (best starting point)
- `_urls.json` — every URL the crawler found
- `mobygames.json`, `mobygames_com_*.json` — credits, platforms, voice cast
- `archive_org_*.json` — magazine scans
- `en_wikipedia_org_*.json` — overview text + sources
- Per-site files: `gamespot_com_*.json`, `ign_com_*.json`, `hardcoregaming101_net_*.json`, `pricecharting_com_*.json`, `myabandonware_com_*.json`, etc.
- `llm_claude.json`, `llm_openai.json` — model-generated dossiers (use as pointers, not facts)
- `kagi_fastgpt.json` — Kagi LLM dossier (same — treat as pointer)

If the slug folder doesn't exist, fall back to:
1. Brave / WebSearch for `<exact game title>` site:mobygames.com, site:archive.org, site:gamespot.com
2. The source hierarchy in `.claude/instructions/citations.md`

### 3a. Content-verify each candidate source (MANDATORY — do not skip)

The crawler-found URL existing in the dossier is **not enough** to cite it. The crawler sometimes catches navigation shells with no real content (e.g., `hardcoregaming101_net_*.json` for series-overview pages routinely come back as nav-only). Before attaching ANY source inline, read its dossier JSON and check three fields:

1. **`source_significance`** — the dossier's own assessment of the page. **REJECT** the source if this says:
   - "Website navigation page only — contains no actual content"
   - "Site header, navigation menu, and promotional content … No game-specific information"
   - "Page not found" / "404" / "robots.txt blocked"
   - Anything indicating the crawler did not retrieve substantive content
2. **`extracted_facts`** — structured data (release_dates, developers, sales_data, ratings, etc.). Confirm the field you want to cite has a non-null value. Empty arrays/nulls everywhere = the page didn't have the content.
3. **`key_quotes`** — verbatim quotes with attribution. For prose claims that include a quotation, the exact quote should appear here, attributed to the same speaker the vault page names.

Also check **`full_text`**: a real article will have multi-thousand-character text; a nav shell typically has 500-1500 chars of headers/menu junk. If `full_text` is short and `extracted_facts` is mostly empty, treat the source as unusable.

**For superlative or specific claims** (e.g., "best-selling of all time", "first ever", "the only X", numeric counts like "16 tables"), grep `full_text` for the exact phrase before citing. If the phrase isn't there, either soften the claim or find a different source. Wikipedia and similar tertiary sources frequently support a weaker version of the claim — cite that version, don't inflate.

**Quick verification one-liner:**
```bash
python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
print('significance:', d.get('source_significance','—'))
print('full_text len:', len(d.get('full_text','')))
print('extracted_facts head:', json.dumps(d.get('extracted_facts',{}))[:300])
print('key_quotes head:', json.dumps(d.get('key_quotes',[]))[:400])
" "<dossier-file.json>"
```
Run this for every candidate ref before adding it inline.

### 4. Categorize issues and plan fixes

| Issue category | Action |
|---|---|
| `References: Reference count N below target of 20` | Mine the dossier for sources not yet cited; add to prose + numbered list. Each new ref must support a specific factual claim — never dump bare URLs. |
| `References: Duplicate reference URL(s) — consolidate into one citation: ['<url>']` | Find both refs in the page, pick the higher-numbered one to remove, renumber any later refs, and update inline `[^ref-N]` markers. |
| `Structure: Missing ### <Heading>` | Insert section using the snippet from `.claude/instructions/page-format.md`. |
| `Series Continuity: N unresolved See Also link(s): ['Name']` | The bracketed page does not exist. Either (a) point to a real existing page, or (b) remove the broken `[[…]]`. Ask the user if it's ambiguous (e.g., `[[Bibliography]]` — is there a planned page?). |
| `Game Info: Game Info callout missing **<Field>:**` | Look up the value in YAML or the dossier; add the field to the callout, preserving canonical field order from `page-format.md`. |
| `Structure: Page mentions version numbers but has no ### Version History` | Add a Version History table under `## Development`. |
| `YAML: YAML <field> may not match Game Info callout` | Read both, decide which is correct (dossier wins), update the other. |
| `References: Reception section has no numeric scores` | Replace vague praise with cited specific scores: `4/5 stars`, `87/100`, etc. |
| `Game Info: Citations inside Game Info callout` | Move heavy citations from callout to prose; leave only one ref per field. |

### 5. Apply citation fixes correctly

When adding a reference:
1. Write the prose claim with `[^ref-N]` inline.
2. Add the citation under `## References` as `[^ref-N]: Author/Publication. "Title." Date. URL`.
3. Use the next available ref number — never reuse, never skip.

When consolidating duplicates:
1. Read the page, find both `[^ref-A]` and `[^ref-B]` definitions sharing the same URL.
2. Keep the lower-numbered one (less downstream renumbering).
3. Replace all `[^ref-B]` inline markers with `[^ref-A]`.
4. Delete the `[^ref-B]:` line.
5. If there are refs `[^ref-C]`, `[^ref-D]`, ... after B, decide whether to renumber. The scorer doesn't require contiguous numbering — gaps are fine. Only renumber if you want clean output.

### 6. Wiki-link rules (CLAUDE.md #5 and #6)
- Outside tables: `[[Target|Alias]]` is fine.
- Inside ANY table cell (including callout-wrapped `> | … |` tables): MUST be `[[Target\|Alias]]` with escaped pipe.
- Never put wiki links in YAML.
- Wiki-link target uses basename only, never folder paths.

Before committing, sanity-check:
```bash
grep -n -E '^>?\s*\|.*\[\[[^\\]+\|' "<page-path>"
```
Any hit needs the escape.

### 7. Re-score
Re-run step 2. Repeat the fix loop until score = 100% (or threshold for `CXL-`/`TBD-` pages, where 90% is the ceiling).

### 8. Update timestamp
Change the line
```
<small style="color: gray">Last updated: YYYY-MM-DD</small>
```
to today's date. Also update `last_updated:` in YAML if present.

### 9. Verify no regression
Run the full vault scorer to confirm overall numbers haven't dropped:
```bash
cd /Users/woodd/GitHub/sierravault && python3 run_consistency.py 2>&1 | tail -10
```
The summary should still show 507/507 passing and avg ≥ previous.

### 10. Report
```
Page: <filename>
Series: <series>
Before: <score>% (refs: <n>) — <n_errors> errors, <n_warnings> warnings
After:  <score>% (refs: <n>) — <n_errors> errors, <n_warnings> warnings
Added refs: [ref-N: source, ref-M: source, ...]
Fixed: <list of structural fixes>
Pending: <anything that needed user input or couldn't be resolved>
```

## Constraints

- **URL existence is NOT sufficient justification.** A URL appearing in the dossier means the crawler saw it; it does NOT mean the page contains content supporting your claim. Always content-verify per step 3a.
- **Never invent facts.** Every new reference must be sourceable from the dossier (with verified content) or a verified web search. If the dossier is empty and web search returns nothing, flag for the user — don't fabricate.
- **No promotional language or unverifiable superlatives.** "Best-selling," "groundbreaking," "first-ever," "of all time" — these need a source that says exactly that. If only a weaker version is supported ("sold more than half a million copies"), use the weaker version.
- **Numeric specifics need exact-phrase grep.** "16 tables," "$5 million budget," "1997 release" — find the number in `full_text` before citing. If sources disagree on the number, use the more authoritative source and note the discrepancy.
- **Conservative claims over confident ones** when sources disagree.
- **Wiki links in tables MUST escape the pipe.** This is in CLAUDE.md rules 5 and 6 and the validator catches it.
- **YAML stays plain text.** No `[[...]]` anywhere in frontmatter.
- **15-ref floor, 20-ref target.** Below 15 is a structural failure; 15-19 is a warning (-5 points per missing); 20+ is clean.

## Failure modes to watch for

These were caught in pilots and represent the easy mistakes:

1. **Navigation-shell crawl** — Some `*.json` dossier files contain only site headers/menus with no article content. The `source_significance` field flags this. Always read it.
2. **Pre-existing content errors** — If the vault page already says "X" and the dossier says "Y", neither is automatically right. Read the source the original claim was based on if you can; otherwise prefer the more authoritative source. Do not silently propagate the vault's existing value.
3. **Citation laundering** — Don't reassign an inline `[^ref-N]` marker to a new source unless the new source actually supports the claim. The citation must justify the prose, not the other way around.
4. **Dossier metadata vs source content** — `_consolidated.json` aggregates facts but attributes them to specific source IDs. Reading the consolidated file is not the same as reading the source. Drill into the actual `<source_id>.json` to see what that source actually said.

## When to stop and ask

- The lowest-scoring page is already at 100% → vault is clean, report and stop.
- A required section is missing and the dossier + web search have no material → ask before fabricating.
- A `[[broken-link]]` could be either "create the target page" or "remove the link" → ask.
- Score drops on re-check → roll back the edit, report what went wrong.
- The page is `CXL-` or `TBD-` prefixed — different rules apply, threshold is 90% not 100%, and Story Summary may be skipped. Confirm with the user before doing structural work on those.

## Pilot order

If running through a backlog, work from `vault_report.json` lowest score first. As of 2026-05-27 the bottom of the list is:
1. 3D Ultra / 1995 - 3-D Ultra Pinball (90.8% — dup URL + low refs)
2. Hoyle / 2000 - Hoyle Slots and Video Poker (93.6%)
3. 3D Ultra / 2000 - 3-D Ultra Pinball - Thrill Ride (95.3%)
4. 3D Ultra / 2006 - 3D Ultra MiniGolf Adventures (95.3%)
5. 3D Ultra / 2010 - 3-D Ultra MiniGolf Adventures 2 (95.3%)

Note the 3D Ultra cluster — fixing them together with a shared dossier-mining pass is faster than one at a time.
