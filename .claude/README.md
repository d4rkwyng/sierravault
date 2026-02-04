# .claude/ Directory

Claude Code configuration and instructions for Sierra Vault.

## Structure

```
.claude/
├── README.md                 # This file
├── settings.local.json       # Claude Code settings
├── instructions/             # Detailed guides (read on demand)
│   ├── pipeline.md          # Pipeline stages, scripts, crawling
│   ├── page-format.md       # Page templates, sections, formatting
│   └── citations.md         # Sources, verification, scoring
├── commands/                 # Custom commands
│   └── batch.md             # Batch game entry mode
└── skills/                   # Custom skills
    └── batch.md             # Batch processing skill
```

## How It Works

1. **Root `CLAUDE.md`** - Auto-loaded every session. Contains core rules and quality standards.

2. **`internal/MEMORY.md`** - Read first every session. Contains current project state, statistics, and pending tasks.

3. **`instructions/`** - Read these when doing specific tasks:
   - Working on pipeline/research → `pipeline.md`
   - Generating or editing pages → `page-format.md`
   - Citation work or scoring issues → `citations.md`

## Key Locations

| What | Where |
|------|-------|
| Project instructions | `/CLAUDE.md` |
| Session state | `/internal/MEMORY.md` |
| Decisions & context | `/internal/MEMORY_ARCHIVE.md` |
| Research data | `/internal/research/` |
| Scripts | `/internal/*.py` |
| Game pages | `/Games/` |
