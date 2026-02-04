# Batch Game Entry Mode

Process Sierra game entries in batch. The user wants to create multiple game entries efficiently.

## Instructions

1. Based on user input (number, series name, or specific games), identify targets
2. For each game:
   - Research via MobyGames, Wikipedia, Sierra Gamers
   - Create full entry following CLAUDE.md structure
   - Update Series Continuity bidirectionally
   - Create Designer/Developer pages if missing
3. After all entries created:
   - Update Guide files (Game Index, Series Guide, Release Timeline)
   - Run `python3 scripts/validate_links.py`
4. Report summary with links to new pages

## User input: $ARGUMENTS

If no arguments provided, ask: "How many games would you like me to process? Or specify a series/game list."

## Quality checklist per entry:
- [ ] YAML front matter complete
- [ ] All sections present (Overview through Sources & Notes)
- [ ] Wiki links use basename only
- [ ] Series Continuity bidirectional
- [ ] Sources cited (15+ minimum)
- [ ] Downloads with verified links
