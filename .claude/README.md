# .claude/ Directory

Claude Code configuration and instructions for SierraVault.

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

1. **Root `CLAUDE.md`** — Auto-loaded every session. Contains core rules and quality standards.

2. **`instructions/`** — Read these when doing specific tasks:
   - Working on pipeline/research → `pipeline.md`
   - Generating or editing pages → `page-format.md`
   - Citation work or scoring issues → `citations.md`

> **Note:** Research data, scoring history, and project state are maintained in a separate private repository (`Proton Drive/Assets/sierravault`). Set `SIERRAVAULT_INTERNAL` env var to point to it, or place it alongside this repo.

## Key Locations

| What | Where |
|------|-------|
| Project instructions | `/CLAUDE.md` |
| Game pages | `vault/Games/` |
| Scripts | `scripts/` |
| Templates | `templates/` |
| Documentation | `docs/` |
