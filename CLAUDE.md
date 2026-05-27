# CLAUDE.md

Project instructions for SierraVault.

## Project Overview

An Obsidian vault documenting Sierra games history with **507 game entries** (74 series folders) from 1980-2025. Content includes Sierra On-Line titles, acquired studios (Dynamix, Impressions, Coktel Vision), fan continuations, and spiritual successors.

Published via Obsidian Publish with AI-assisted workflows, automated validation, and human editorial review.

## Repository Structure

```
sierravault/
├── vault/              # Obsidian vault (published content)
│   ├── Games/          # 507 game entries
│   ├── Designers/      # Designer biographies
│   ├── Developers/     # Studio profiles
│   ├── Publishers/     # Publisher histories
│   ├── Series/         # Series overview pages
│   ├── Guides/         # How-to guides
│   ├── Technology/     # Engine documentation
│   ├── Reference/      # Timelines, indexes
│   └── Images/         # Logos, favicons
├── scripts/            # Validation and scoring tools
├── templates/          # Page templates
├── docs/               # Documentation
│   ├── STYLE_GUIDE.md
│   ├── INCLUSION_CRITERIA.md
│   └── QUARTZ.md
└── .claude/            # Task-specific instructions
```

> **Note:** Research data, scoring history, and internal tooling are in a separate private repository.

## Quality Standards

### Score Thresholds
| Category | Minimum |
|----------|---------|
| Core/Flagship (KQ, SQ, QFG, PQ, LSL, GK, Laura Bow) | 95% |
| All other games | 90% |
| Fan games, cancelled games | 90% (more leeway) |

### Reference Requirements
- **Minimum 15 references** per page (target 20+)
- All facts traceable to research sources
- No hallucinated or unverifiable claims
- Dual-model scoring required (Claude + GPT)

## Critical Rules

**RULE #0 — REAL REFERENCES ONLY (absolute, non-negotiable).** Never cite a reference unless the source actually exists AND actually contains the claim it is attached to. A URL existing in the research dossier (`Assets/Research/games/<slug>/*.json`) is NOT sufficient — the crawler frequently catches navigation shells, 404 pages, and robots-blocked URLs that contain no real content. Before citing any source, read the dossier file's `source_significance`, `full_text` length, `extracted_facts`, and `key_quotes`. If `source_significance` says "navigation page only" or "no actual content", REJECT the source. For superlatives, specific numbers, or named entities, grep `full_text` for the exact phrase before citing. If the source doesn't support the claim verbatim, either find a source that does or weaken the claim. A page passing the consistency check at 100% does NOT mean its citations are factually correct — the scorer validates structure, not truth. See `~/.claude/projects/-Users-woodd-GitHub-sierravault/memory/feedback_real_references_only.md` for full protocol.

1. **Never publish without dual scoring** - both structural AND LLM scoring must pass
2. **Never trust GOG links without verification** - use Brave Search: `site:gog.com "Game Title"`
3. **Never add wiki links to YAML** - plain text only
4. **Never include folder paths in wiki links** - basename only (`[[Roberta Williams]]`)
5. **Wiki link alias separator depends on context — get this right or links break in BOTH Obsidian AND Quartz:**
   - **Outside tables** (prose, bullet lists, callout body, headings): use plain `|` — `[[Target|Alias]]`
   - **Inside ANY markdown table cell** (including callout-wrapped tables `> | ... |`): use ESCAPED pipe — `[[Target\|Alias]]`. The `\` is required because the table parser otherwise treats the `|` inside the link as a column separator, splitting the link mid-target. Both Obsidian and Quartz behave this way.
   - This applies equally to:
     - Plain markdown tables (`| Header | ... |`)
     - Callout-wrapped tables (`> | Header | ... |`) — these LOOK like callouts but the table parser still runs, so the same escape rule applies.
   - Tables ARE allowed and encouraged for structured navigation (Series timelines, recent-releases lists, Site Index, Designer credits, etc.) — just escape the pipe.
6. **No bare `[[X|Y]]` (unescaped pipe) inside table cells.** This is the same rule as #5 stated as a checklist item. Run `grep -n -E '^>?\s*\|.*\[\[[^\\]+\|' vault/**/*.md` (or the vault-health script) before committing — any hit needs the `\|` escape.
7. **Always run link validation before committing**
8. **Minimum 15 references per page**
9. **Both LLM models must score >=90%** for publication
10. **Always update timestamps when editing pages**

## Instruction Files

For detailed guidance on specific tasks:

| Task | File |
|------|------|
| Page templates, sections, formatting | `.claude/instructions/page-format.md` |
| Citations, sources, scoring issues | `.claude/instructions/citations.md` |
| Pipeline and research workflow | `.claude/instructions/pipeline.md` |

## Quick Commands

```bash
# Activate environment
source .venv/bin/activate

# Score a page (structural)
python scripts/score_page.py "vault/Games/King's Quest/1990 - King's Quest V.md"

# Score with LLM (requires API keys)
python scripts/score_page_llm.py "vault/Games/Space Quest/1991 - Space Quest IV.md" --model both

# Validate wiki links
python scripts/validate_links.py

# Add timestamps
python scripts/add_timestamps.py
```

## Page Structure

Every game page needs:

1. **Frontmatter** - YAML metadata (title, year, developer, platforms)
2. **Overview** - 2-3 paragraphs with citations
3. **Story Summary** - Plot without major spoilers
4. **Gameplay** - Interface, mechanics, puzzles
5. **Reception** - Contemporary and modern reviews with scores
6. **Development** - Team, budget, technical achievements
7. **Legacy** - Impact, sequels, remakes
8. **Downloads** - Purchase links (GOG, Steam)
9. **Series Continuity** - Links to previous/next in series
10. **References** - 15-40+ numbered citations

## Scoring Process

1. Run structural scoring: `python scripts/score_page.py <path>`
2. Run LLM scoring: `python scripts/score_page_llm.py <path> --model both`
3. Fix any issues flagged
4. Re-score until ≥90% (≥95% for flagships)
5. Submit for human review

## Common Issues

| Issue | Fix |
|-------|-----|
| Duplicate reference URLs | Consolidate to single citation |
| Low citation count | Add more sources from research |
| Broken wiki links | Check filename spelling/case |
| Missing sections | Add required sections per template |
| YAML wiki links | Convert to plain text |

## Links

- **Live Site:** [sierravault.net](https://sierravault.net)
- **Quartz Mirror:** [quartz.sierravault.net](https://quartz.sierravault.net)
- **Style Guide:** [docs/STYLE_GUIDE.md](docs/STYLE_GUIDE.md)
