# Pipeline Instructions

Six-stage pipeline for research and page generation.

## Pipeline Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. DISCOVER │ →  │ 2. CRAWL    │ →  │ 3. ENRICH   │ →  │ 4. GENERATE │ →  │ 5. SCORE    │ →  │ 6. PUBLISH  │
│ discover_   │    │ crawl_      │    │ enrich_     │    │ Claude/     │    │ Dual-model  │    │ Copy to     │
│ urls.py     │    │ sources.py  │    │ research.py │    │ manual      │    │ validation  │    │ Games/      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     ↓                   ↓                   ↓                   ↓                   ↓                   ↓
 _urls.json         *.json files        extracted_facts     /tmp/*.md           scores ≥90%         Games/*.md
 50-100 URLs        30+ sources         key_quotes          20+ refs            both models
```

## Automated Pipeline

```bash
source .venv/bin/activate

# Default: Discover → Crawl → Enrich (stops before generation)
python3 pipeline.py "Space Quest III"

# Discovery only
python3 pipeline.py "Space Quest III" --discover

# Through crawling
python3 pipeline.py "Space Quest III" --crawl

# Full pipeline including generation
python3 pipeline.py "Space Quest III" --generate

# Auto-publish if scores pass
python3 pipeline.py "Space Quest III" --auto-publish

# Batch process
python3 pipeline.py --batch games.txt --workers 16

# Status
python3 pipeline.py --status
python3 pipeline.py --next 10
```

The pipeline **stops before generation by default** for research quality review.

---

## Stage 1: URL Discovery

```bash
python3 discover_urls.py "Space Quest III" --series "Space Quest"
```

**Sources checked:**
1. Wikipedia article + external references
2. Web search on priority domains
3. Template URLs (MobyGames, GOG, Steam, PCGamingWiki)
4. Series-specific wikis

**Output:** `research/{game-slug}/_urls.json`

**Target:** 50-100 discovered URLs per game

---

## Stage 2: Parallel Crawling

```bash
python3 crawl_sources.py "Space Quest III" --workers 16
```

**Features:**
- 16 parallel workers by default
- Domain intelligence from `domains.json`
- Auto-skip blocked domains (IGN, Eurogamer, Kotaku)
- Content validation (wrong content, 404s, blocks)

**Output:** One JSON per source in `research/{game-slug}/`

**Quality gate:** 30+ good sources (>2KB) required before enrichment

---

## Stage 3: Enrichment

```bash
python3 enrich_research.py {game-slug}
```

Uses Claude API to extract from each source's `full_text`:
- Release dates, developers, publishers, designers
- Review scores with publication, reviewer, date
- Voice cast, composers, credits
- Technical specs, version info
- Awards, sales data, trivia, key quotes

**Quality gate:** 80%+ sources must have `extracted_facts` before generation

---

## Stage 3.5: LLM Data Gathering (Optional)

```bash
# Claude + GPT-4o
python3 query_llms_for_games.py "game-slug"

# Kagi FastGPT (sourced answers)
python3 query_kagi_for_games.py "game-slug"

# Batch flagship games
python3 query_llms_for_games.py --flagship
```

**Output:** `llm_claude.json`, `llm_openai.json`, `kagi_fastgpt.json`

**Use after enrichment, before generation**, especially for flagship games.

---

## Stage 4: Page Generation

**Manual generation preferred** - Claude reads research and writes interactively.

```
"Generate a page for Space Quest III from research/space-quest-iii/"
```

**Process:**
1. Count research files: `ls research/game-name/*.json | wc -l`
2. Read files in batches (5-10 at a time)
3. Use Task tool with subagent_type=Explore for 50+ files
4. Synthesize unique facts with citations
5. Verify against research before finishing

**Automated (lower quality):**
```bash
python3 generate_page_from_research.py space-quest-iii -o /tmp/sq3.md
```

### Post-Generation Verification (REQUIRED)

After generating, verify no facts were missed:
1. Read ALL research JSON files
2. Extract key facts, verify they appear in page
3. Add missing content with citations
4. Re-run scoring

---

## Stage 5: Scoring

```bash
# Structural scoring
python3 score_page.py /tmp/sq3.md

# LLM accuracy scoring
python3 score_page_llm.py /tmp/sq3.md --model both
```

**Pass criteria:**
- `score_page.py`: 95%+
- `score_page_llm.py`: Both Claude AND GPT ≥90%

**Scoring breakdown:**
| Category | Points |
|----------|--------|
| References | 25 |
| Accuracy | 25 |
| Completeness | 25 |
| Formatting | 25 |

---

## Stage 6: Publishing

```bash
cp /tmp/sq3.md "Games/Space Quest/1989 - Space Quest III - The Pirates of Pestulon.md"
python3 validate_links.py
python3 add_timestamps.py
git add "Games/Space Quest/*.md" && git commit -m "Add Space Quest III"
```

---

## Key Scripts

| Script | Purpose |
|--------|---------|
| `pipeline.py` | Main orchestrator |
| `discover_urls.py` | URL discovery |
| `crawl_sources.py` | Parallel crawler (16 workers) |
| `crawl_with_render.py` | Crawler with render=true for protected sites |
| `enrich_research.py` | LLM fact extraction |
| `enrich_parallel.py` | Parallel enrichment (50 workers) |
| `query_llms_for_games.py` | Claude + GPT-4o queries |
| `query_kagi_for_games.py` | Kagi FastGPT queries |
| `generate_page_from_research.py` | Automated generation |
| `score_page.py` | Structural scoring |
| `score_page_llm.py` | LLM accuracy scoring |
| `completion_tracker.py` | Progress tracking |
| `validate_links.py` | Wiki link validation |
| `add_timestamps.py` | Update timestamps |

---

## Research Folder Structure

```
research/
  space-quest-iii/
    _urls.json            # URL discovery + status
    _manifest.json        # Pipeline status
    mobygames.json        # Content + extracted_facts
    wikipedia.json
    pcgamingwiki.json
    ... (30+ files)
```

**Each source JSON:**
- `url`, `domain`, `fetch_date`, `fetch_status`
- `full_text` - Complete extracted text (up to 50KB)
- `extracted_facts` - Structured data from LLM
- `key_quotes` - Quotable passages

---

## Domain Intelligence

`domains.json` tracks crawl methods per domain:

```json
{
  "mobygames.com": {"method": "playwright", "success_rate": 0.85},
  "www.ign.com": {"method": "skip", "success_rate": 0.05},
  "en.wikipedia.org": {"method": "httpx", "success_rate": 0.95}
}
```

**Methods:**
- `httpx` - Simple HTTP (fast, most sites)
- `playwright` - Browser rendering (JS-heavy sites)
- `skip` - Known blocked

---

## Handling Blocked Sources

1. Check `domains.json` - may already be marked skip
2. Try Wayback Machine: `web.archive.org/web/*/original-url`
3. Add manually with `fetch_status: "manual"`
4. Use alternative sources

### ScraperAPI Render Mode

For JS-heavy/bot-protected sites:

```bash
python3 crawl_with_render.py "game-slug"
```

**Sites requiring render=true:**
- `wiki.scummvm.org` - Anubis bot protection
- `sciwiki.sierrahelp.com` - JS-heavy
- `agiwiki.sierrahelp.com` - JS-heavy

**Note:** 25 credits per request (vs 1 standard)

---

## Batch Operations

### Expand Research (Brave Search)
```bash
python3 expand_all_games.py "game-slug"      # Single game
python3 expand_all_games.py --low            # Games with <30 sources
python3 expand_all_games.py --all            # All games
```

### Completion Tracking
```bash
python3 completion_tracker.py --refresh      # Full status
python3 completion_tracker.py --list         # Games needing work
python3 completion_tracker.py --next 10      # Next priorities
```

---

## Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional: browser-rendered crawling
pip install playwright && playwright install chromium

# API keys in .env (copy from .env.example)
cp .env.example .env
# Then edit .env with your actual keys
echo 'export SCRAPER_API_KEY="..."' >> .env
echo 'export KAGI_API_KEY="..."' >> .env
source .env
```
