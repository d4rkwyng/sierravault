# Citations & Quality Guide

Citation standards, source hierarchy, and common scoring issues.

## Citation Verification Process

When updating citations, **never assume** a source contains specific facts. Always verify.

### Verification Steps

1. **Fetch each source** using Playwright (MobyGames, TV Tropes) or WebFetch
2. **Document what facts** each source actually contains
3. **Only cite sources** for information they verifiably contain
4. **Add new references** when discovering sources with useful data
5. **Fix incorrect attributions** immediately

---

## Source Hierarchy

Prefer sources in this order:

| Priority | Type | Examples | Best For |
|----------|------|----------|----------|
| 1 | Official | guysfromandromeda.com, Sierra press releases | Developer quotes |
| 2 | Databases | MobyGames, IMDB | Credits, platforms, voice cast |
| 3 | Fan wikis | SpaceQuest.net, Sierra Fandom | Plot, easter eggs, trivia |
| 4 | Technical | ScummVM Wiki, PCGamingWiki, Sierra Help | Specs, bugs, patches |
| 5 | Reviews | Adventure Gamers, TV Tropes, magazines | Reception, pop culture |
| 6 | Archives | Archive.org magazine scans, SEC filings | Original reviews, sales |
| 7 | General | Wikipedia | Use sparingly, trace to originals |

### SpaceQuest.net Subpages
Rich source with dedicated pages:
- `/eastereggs/` - Hidden content
- `/spoofref/` - Pop culture references
- `/cheatdebug/` - Debug commands
- `/funfacts/` - Development trivia
- `/cameos/` - Character appearances
- `/plotinconsis/` - Continuity errors
- `/cancelled/` - Cut content

### Adventure Gamers
Requires Playwright (blocks WebFetch):
```python
from playwright.sync_api import sync_playwright
# https://adventuregamers.com/games/[game-slug]
```

---

## Common Citation Mistakes

1. **Assuming MobyGames has everything** - Has credits/platforms, may lack plot
2. **Citing fan wikis for biographical info** - Verify against official sources
3. **Swapping Wikipedia without checking** - Replacement must contain same facts
4. **Citing developer quotes without source** - Track down actual interview

---

## Hallucination Prevention

Automated generators retired due to hallucinations:

**Examples caught:**
- King's Quest III: Invented "Time magazine #50" ranking
- King's Quest 2015: Made-up village name "Itch-two-wey"
- King's Quest V: Dubious "best-selling computer game in history"

**Prevention:**
1. Manual generation with fact-checking against research
2. Dual-model scoring catches different perspectives
3. Exceptional claims require web search verification
4. Conservative language over superlatives

---

## Common Scoring Issues

Based on LLM feedback across 47+ pages:

### 1. Wiki Links to Non-Existent Pages
**Problem:** Wiki links when no page exists.
**Exception:** Designers, Developers, Publishers are OK (future pages).
**Fix:** Verify target exists for series/game links:
```bash
find Games -name "*.md" | grep -i "game name"
```

### 2. Missing Section Headers
**Problem:** Content exists but lacks `## Legacy` or `## Reception` headers.
**Fix:** Always include:
- `## Reception` with `### Contemporary Reviews` and `### Modern Assessment`
- `## Legacy` as standalone section

### 3. Missing Specific Review Scores
**Problem:** "Computer Gaming World praised the game" without actual score.
**Fix:** Include the score:
- Good: "CGW gave it 4/5 stars[^ref-1]"
- Bad: "CGW praised the game[^ref-1]"

### 4. YAML Frontmatter Inconsistencies
**Problem:** YAML says `designer: null` but text mentions Bill Davis.
**Fix:** Ensure YAML matches content:
```yaml
designer:
  - "Bill Davis"
```

### 5. Broken Reference URLs
**Problem:** Archived pages, old announcements, defunct sites.
**Fix:**
- Prefer stable URLs (Wikipedia, MobyGames, GOG)
- Use Wayback Machine for archived content
- Verify URLs are accessible

### 6. Citations Inside Game Info Callout
**Problem:** Heavy citations in callout cause formatting issues.
**Fix:** Keep callout citations minimal; heavy citation in prose.

### 7. Wrong GOG Link
**Problem:** Link points to wrong collection (e.g., `kings_quest_4_5_6` on KQ7 page).
**Fix:** Verify link matches the game:
```bash
# Search for correct slug
site:gog.com "Game Title"
```

### 8. Missing Version History
**Problem:** Version numbers in text but no `### Version History` table.
**Fix:** Add under `## Development`:
```markdown
### Version History

| Version | Date | Platform | Notes |
|---------|------|----------|-------|
| 1.0 | Nov 1994 | DOS | Original release[^ref-1] |
```

---

## Pre-Scoring Checklist

Before running `score_page_llm.py`:

- [ ] `## Reception` has `### Contemporary Reviews` and `### Modern Assessment`
- [ ] `## Legacy` section exists with explicit header
- [ ] All wiki links point to existing pages (or remove brackets)
- [ ] YAML frontmatter matches content (especially designer)
- [ ] Review scores are specific numbers, not vague praise
- [ ] All reference URLs are functional
- [ ] GOG links verified with `site:gog.com`

---

## Wikipedia Reference Tracing

When reducing Wikipedia citations, trace to original sources:

1. Fetch Wikipedia page → extract reference URLs
2. Trace to Archive.org → many 1980s-90s magazine reviews scanned
3. Download magazine text → OCR via `_djvu.txt` suffix
4. Search for quotes → verify exact wording
5. Add as new reference with publication, date, page number

**Magazine archives on Archive.org:**
- Computer Gaming World (1980s-2000s)
- PC Magazine (1988+)
- Antic Magazine (Atari)
- Compute! Magazine
- Dragon Magazine

**Key sources to prioritize:**
- Archive.org magazine scans
- Digital Antiquarian (filfre.net)
- Google Books (PC Magazine, InfoWorld)
- Strong Museum of Play
- Sierra Newsletters on Archive.org

---

## Generation Principles

When writing pages:

1. **Only use facts from research JSON or verified sources**
2. **Flag suspicious claims** (rankings, sales, awards)
3. **Prefer conservative statements** over superlatives
4. **Include inline citations** throughout prose
5. **Minimum 15 references**

**Validation checklist:**
- [ ] All facts traceable to research JSON
- [ ] Exceptional claims verified via web search
- [ ] No promotional language or dubious superlatives
- [ ] All external links tested
- [ ] GOG links verified (not wishlist/dreamlist)
