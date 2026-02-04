# Page Format Guide

Templates and formatting standards for game pages.

## File Naming

`YEAR - Full Game Title.md`

Examples:
- `1984 - King's Quest - Quest for the Crown.md`
- `1989 - Space Quest III - The Pirates of Pestulon.md`

---

## Section Order

1. YAML frontmatter
2. `# Title`
3. `<small style="color: gray">Last updated: DATE</small>`
4. `## Overview`
5. `> [!info]- Game Info` (collapsible callout)
6. `## Story Summary`
7. `## Gameplay`
   - `### Interface and Controls`
   - `### Structure and Progression`
   - `### Puzzles and Mechanics`
8. `## Reception`
   - `### Contemporary Reviews`
   - `### Modern Assessment`
9. `## Development`
   - `### Origins` / `### Production`
   - `### Voice Cast` (table format, if applicable)
   - `### Technical Achievements`
   - `### Version History` (table format)
10. `## Legacy`
    - `### Collections` (if applicable)
11. `## Downloads`
    - `**Purchase / Digital Stores**`
    - `**Download / Preservation**`
    - `**Manuals & Extras**`
12. `## Series Continuity` (if applicable)
13. `## References`

---

## YAML Frontmatter

```yaml
---
title: "Game Title"
release_year: 1989
developer: "Sierra On-Line"
designer:
  - "Designer Name"
publisher: "Sierra On-Line"
genre: "Adventure"
platforms: ["MS-DOS", "Amiga"]
series: "Series Name"
engine: "SCI0"
protagonist: "Character Name"
sierra_lineage: "Core Sierra"
last_updated: "2025-12-10"
---
```

**Rules:**
- Plain text only (NO wiki links)
- Use `null` for unknown fields
- `last_updated` is auto-generated

### Engine by Year
- Pre-1988: AGI
- 1988: Transition (AGI or SCI)
- 1989-1991: SCI0/SCI1
- 1992-1993: SCI1.1
- 1994-1996: SCI2/SCI32
- 1997+: Custom or specified

---

## Game Info Callout

Appears after Overview paragraph. **Fields in this exact order:**

```markdown
> [!info]- Game Info
> **Developer:** Studio Name[^ref-1]
> **Designer:** Designer Name[^ref-1]
> **Publisher:** Publisher Name[^ref-1]
> **Engine:** Engine Name[^ref-2]
> **Platforms:** Platform list[^ref-3]
> **Release Year:** Year[^ref-1]
> **Series:** Series Name
> **Protagonist:** Character Name
> **Sierra Lineage:** Core Sierra
```

**Rules:**
- **Plain text only** - NO wiki links
- **Standard fields only** - No Director, Producer, Programmer, Artist, Composer, Writer
- **Field order matters**
- Minimal citations (heavy citation in prose)

---

## Version History Format

Under `## Development`:

```markdown
### Version History

| Version | Date | Platform | Notes |
|---------|------|----------|-------|
| 1.0 | November 1990 | DOS | Original release[^ref-1] |
| 2.0 | March 1991 | DOS | Bug fixes, speed control[^ref-1] |
| CD-ROM | August 1991 | DOS | Full voice acting[^ref-2] |
```

**SCI Interpreter Table** (Sierra games):
```markdown
**SCI Interpreter Versions:**[^ref-3]

| Game Version | Interpreter | Type | Notes |
|--------------|-------------|------|-------|
| 1.000 | 1.001.054 | SCI1.1 | Initial release |
| 1.034 | 1.001.069 | SCI1.1 | Windows CD version |
```

**AGI Interpreter Table:**
```markdown
**AGI Interpreter Versions:**[^ref-3]

| Game Version | Interpreter | Notes |
|--------------|-------------|-------|
| 1.01 | AGI 2.272 | Initial release |
| 2.00 | AGI 2.435 | Bug fix version |
```

**Additional elements:**
- **Cancelled Ports:** Single line listing
- **Copy Protection:** Document protection schemes
- Separate subsections for notable ports (`### NES Version`)

---

## Voice Cast Format

For CD-ROM/talkie games, under `## Development`:

```markdown
### Voice Cast

[Brief intro about voice production, studio, notable aspects]

**Principal Cast:**[^ref-X]

| Actor | Characters |
|-------|------------|
| Robby Benson | Prince Alexander |
| Tony Jay | Captain Saladin, Gate Guard, Arch Druid |
| Josh Mandel | King Graham, Shamir Shamazel |
```

**Guidelines:**
- Table format (not bullets or prose)
- Alphabetical or by prominence (main character first)
- Multiple roles comma-separated
- Note "(uncredited)" for uncredited roles
- Include voice director in intro if known

**Include when:**
- CD-ROM "talkie" versions
- 5+ credited voice actors
- Skip for text-only or minimal voice work

---

## Reference Requirements

- **Minimum 15 references** (target 20+)
- Inline citations throughout prose: `[^ref-1][^ref-2]`

**Reference format:**
```markdown
[^ref-1]: [Source – Title](URL) – what info was used
```

---

## Wiki Link Rules

- Basename only, no `.md` extension, no folder paths
- Correct: `[[Roberta Williams]]`
- Wrong: `[[Designers/Roberta Williams.md]]`

**Allowed even if page doesn't exist:**
- Designers, Developers, Publishers (planned future pages)

**Verify target exists for:**
- Series names, game titles

```bash
find Games -name "*.md" | grep -i "game name"
```

---

## Fan Game Guidelines

### Section Header
Use `## Related Games` instead of `## Series Continuity`

### Linking Rules
- **Remakes** (AGDI KQ1-3, IA KQ4): Link to original Sierra game
- **Fan sequels**: Do NOT wiki link to official series
- **Fan Timeline**: Only link to games from same fan studio

**Example - Fan Remake:**
```markdown
## Related Games

This VGA remake reimagines the original [[1985 - King's Quest II - Romancing the Throne]].

**AGDI Fan Games:**
- **Previous:** King's Quest I VGA Remake (2001)
- **Next:** King's Quest III Redux (2011)
```

**Example - Fan Sequel:**
```markdown
## Related Games

Space Quest: Incinerations continues Roger Wilco's adventures in an unofficial fan timeline.

**Fan Game Timeline:**
- **Previous:** Space Quest: Vohaul Strikes Back (2011)
- **Next:** N/A
```

---

## Cancelled Game Guidelines

- Use `## Development` to document what was known
- Include cancellation date and reason if known
- `## Reception` becomes `## Legacy` only
- Aim for 90%, more leeway acceptable due to limited sources

---

## GOG Link Verification

1. Search: `site:gog.com "Game Title"`
2. `/wishlist/` or `/dreamlist/` URLs = NOT available
3. Only `/game/slug` URLs are valid
4. Format: `https://www.gog.com/en/game/game_slug`

**Common mistake:** Linking `kings_quest_4_5_6` on a KQ7 page. Collections must match the game being documented.

---

## Formatting Checks

```bash
# .md in links (wrong)
rg '\[\[.*\.md' Games/

# Folder paths in links (wrong)
rg '\[\[Games/' Games/

# Validate all wiki links
python3 validate_links.py
```
