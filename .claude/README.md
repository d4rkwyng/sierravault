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

> **Note:** Research data, scoring history, and project state are maintained in a separate private repository. Scripts default to `~/Library/Mobile Documents/com~apple~CloudDocs/Assets/sierravault` (iCloud Drive) unless the `SIERRAVAULT_INTERNAL` env var points somewhere else — set it on any machine (e.g. the fleet's `droid` service account) that doesn't have that iCloud Drive path.

## Key Locations

| What | Where |
|------|-------|
| Project instructions | `/CLAUDE.md` |
| Game pages | `vault/Games/` |
| Scripts | `scripts/` (Assets/ACTIVE — private repo, not in this checkout; see note above) |
| Templates | `templates/` |
| Documentation | `docs/` |
