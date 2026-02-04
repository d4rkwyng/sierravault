# Batch Game Entry Mode

Process Sierra game entries in batch. The user wants to create multiple game entries efficiently.

## Instructions

1. Read `internal/GameList-ToDo.md` to find unchecked games `[ ]`
2. Based on user input (number, series name, or specific games), identify targets
3. For each game:
   - Research via MobyGames, Wikipedia, Sierra Gamers
   - Create full entry following CLAUDE.md structure
   - Update Series Continuity bidirectionally
   - Create Designer/Developer pages if missing
4. After all entries created:
   - Update Guide files (Game Index, Series Guide, Release Timeline)
   - Run `python3 internal/validate_links.py`
   - Mark games as `[x]` in GameList-ToDo.md
5. Report summary with links to new pages

## User input: $ARGUMENTS

If no arguments provided, ask: "How many games would you like me to process? Or specify a series/game list."

## Quality checklist per entry:
- [ ] YAML front matter complete
- [ ] All sections present (Overview through Sources & Notes)
- [ ] Wiki links use basename only
- [ ] Series Continuity bidirectional
- [ ] Sources cited
- [ ] Files & Downloads with working links
