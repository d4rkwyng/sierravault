# Batch Game Entry Mode

When this skill is invoked, enter batch processing mode for Sierra Games research.

## Workflow

1. **Load Queue**: Read `internal/games_queue.json` to get the priority queue
2. **Pick Next Game**: Select the next unresearched game from the priority queue
3. **Research**: Run parallel research using `research_game_parallel.py`
4. **Generate Page**: Create the game page from research data
5. **Score**: Run both scoring scripts to validate
6. **Update Queue**: Mark game as completed, move to next

## Commands

When user says `/batch`, do the following:

1. Show current queue status:
   - How many games completed
   - How many pending
   - Next 5 games in queue

2. Ask user which action:
   - **Continue**: Process next game in queue
   - **Pick**: Let user choose a specific game
   - **Status**: Show detailed progress

3. For each game, follow this process:
   ```
   a. Research (parallel fetch 60+ sources)
   b. Review research quality
   c. Generate page from research
   d. Score with both validators
   e. If score ≥90%, mark complete
   f. Ask: Continue to next game?
   ```

## Research Process

For each game:

```bash
cd .
source .venv/bin/activate
python3 research_game_parallel.py "GAME TITLE"
```

Then read the research folder and generate the page following CLAUDE.md guidelines.

## Queue Management

After completing a game:
1. Add to `completed` array in games_queue.json
2. Remove from `priority_queue`
3. Update stats
4. Commit changes

## Example Session

```
User: /batch
Claude: 📊 **Batch Mode Status**
        - Completed: 8 games
        - Pending: 362 games

        **Next in queue:**
        1. King's Quest VIII - Mask of Eternity
        2. Space Quest - The Sarien Encounter
        3. Space Quest II - Vohaul's Revenge

        What would you like to do?
        - [Continue] Process next game
        - [Pick] Choose specific game
        - [Status] Detailed progress

User: Continue
Claude: Starting research for "King's Quest VIII - Mask of Eternity"...
        [runs parallel research]
        [generates page]
        [scores page]
        ✅ Complete! Score: 94%

        Continue to next game?
```
