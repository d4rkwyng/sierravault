# Batch Game Entry Mode

When this skill is invoked, enter batch processing mode for Sierra Games research.

## Workflow

1. **Pick Game**: Select the next game to research
2. **Research**: Gather sources from MobyGames, Wikipedia, gaming databases
3. **Generate Page**: Create the game page from research data
4. **Score**: Run both scoring scripts to validate
5. **Iterate**: Fix issues, re-score, then move to next

## Commands

When user says `/batch`, do the following:

1. Ask user which action:
   - **Continue**: Process next game
   - **Pick**: Let user choose a specific game
   - **Status**: Show detailed progress

2. For each game, follow this process:
   ```
   a. Research (gather sources)
   b. Review research quality
   c. Generate page from research
   d. Score with both validators
   e. If score ≥90%, mark complete
   f. Ask: Continue to next game?
   ```

## Research Process

For each game:

```bash
source .venv/bin/activate
python3 scripts/score_page.py "vault/Games/Series/YEAR - Game Title.md"
python3 scripts/score_page_llm.py "vault/Games/Series/YEAR - Game Title.md" --model both
```

Then generate the page following CLAUDE.md guidelines.

## Quality Standards

- All pages must score ≥90% (≥95% for flagship games)
- Minimum 15 citations per page
- Both Claude AND GPT must score ≥90%
- All wiki links must resolve
- No duplicate reference URLs
