---
title: "Sierra Parser Commands Guide"
type: guide
topic: "Text Parser Interface"
engines: ["AGI", "SCI0", "SCI1"]
years_covered: "1984-1993"
last_updated: "2026-02-07"
---

# Sierra Parser Commands Guide

<small style="color: gray">Last updated: February 7, 2026</small>

## Overview

The text parser was Sierra On-Line's primary interface for adventure games from 1984 to 1991, requiring players to type commands to interact with game worlds. This system powered the [[Adventure Game Interpreter\|AGI]] engine era (1984-1989) and continued into the early [[Sierra Creative Interpreter\|SCI]] era (1988-1991) before being replaced by point-and-click interfaces.

Understanding the parser is essential for playing classic Sierra adventures—from [[1984 - King's Quest - Quest for the Crown\|King's Quest]] through [[1989 - Leisure Suit Larry III - Passionate Patti in Pursuit of the Pulsating Pectorals\|Leisure Suit Larry III]]—and can mean the difference between frustration and enjoyment.

## What is a Text Parser?

A text parser is an input system that interprets typed commands and translates them into game actions. Sierra's parser understood approximately **1,000 words per game**[^ref-agi][^ext-hcg101], though this varied by title—with responses ranging "from helpful to humorously sarcastic."[^ext-hcg101]

The parser worked through **verb-noun combinations**:
- `LOOK TREE`
- `GET SWORD`
- `TALK MAN`
- `OPEN DOOR`

Players typed commands into a text input line while controlling their character with arrow keys or joystick. This hybrid approach—keyboard movement plus typed commands—was revolutionary for 1984[^ref-kq1][^ext-sierra-fandom].

### How It Worked

1. Player positions character near an object or person
2. Player types a command (e.g., `LOOK AT STATUE`)
3. Parser analyzes the text for recognized verbs and nouns
4. If understood, the game executes the action
5. If not understood: "I don't understand" or similar response

The parser responses ranged from "helpful to humorously sarcastic"[^ref-agi], and discovering witty rejection messages became part of the entertainment.

## Common Verbs and Commands

### Essential Verbs

These verbs work across virtually all Sierra parser games:

| Verb | Function | Example |
|------|----------|---------|
| LOOK | Examine objects/environment | `LOOK AT PAINTING` |
| GET/TAKE | Pick up items | `GET KEY` |
| OPEN | Open doors, containers | `OPEN CHEST` |
| CLOSE | Close doors, containers | `CLOSE DOOR` |
| TALK/ASK | Speak to characters | `TALK TO MAN` |
| GIVE | Give inventory items | `GIVE BREAD TO BEGGAR` |
| USE | General interaction | `USE ROPE` |
| DROP/PUT | Place items | `PUT ROCK IN HOLE` |
| READ | Read signs, books, notes | `READ SIGN` |
| PUSH/PULL | Move objects | `PUSH BOULDER` |
| CLIMB | Ascend surfaces | `CLIMB LADDER` |
| SWIM | Water navigation | `SWIM` |

### Game-Specific Commands

Different series required specialized vocabulary:

**[[Police Quest Series\|Police Quest]]**[^ref-pq1][^ext-mobygames-pq1]:
- `RADIO` - Use police radio
- `CUFF` - Handcuff suspects
- `SEARCH` - Pat down suspects
- `CITE` - Issue citations
- `BOOK` - Process prisoners

**[[Space Quest Series\|Space Quest]]**[^ref-sq1][^ext-sierra-fandom-sq1]:
- `SCAN` - Use scanner equipment
- `PRESS BUTTON` - Operate controls
- `HIDE` - Take cover

**[[King's Quest Series\|King's Quest III]]** spell-casting[^ref-kq3][^ext-wikipedia-kq3]:
- Commands followed exact manual wording
- Required precise punctuation
- Single typos caused death

## Parser Tips and Tricks

### Phrasing Matters

The parser was notoriously literal. If one phrasing doesn't work, try alternatives:

❌ `PUT BAG BOTTLE` (fails due to parser bug in [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)\|LSL2]][^ref-lsl2][^ext-allowe-bug])
✅ `PUT THE BAG IN BOTTLE`

As Al Lowe explained: "The day before the game shipped, the system programmer in charge of 'the parser' fixed a bug that I'd been complaining about for days. He assured me he changed nothing else. I foolishly added the new code to the game."[^ext-allowe-bug] The bug causes commands like "PUT BAG BOTTLE" to fail because the parser incorrectly treats "bag" as a verb rather than a noun. "16 years later, I'm still answering emails about a bug I swear I didn't create!"[^ext-allowe-bug]

❌ `TAKE ITEM`
✅ `GET ITEM` or `PICK UP ITEM`

### Positioning is Critical

"The parser system, while functional, could be frustratingly rigid, requiring precise positioning and phrasing to execute commands successfully"[^ref-lsl3][^ext-acg-lsl3].

- Walk **directly next** to objects before interacting
- Some commands only work from specific screen positions
- If a command fails, try moving closer

### Common Frustrations

**"I don't understand"**
The parser didn't recognize your wording. Try:
- Simpler phrasing
- Different synonyms
- Removing articles (THE, A, AN)

**"You can't do that"**
The parser understood but the action isn't possible. Either:
- Wrong location/timing
- Inventory item required
- Different approach needed

**"I see no _____ here"**
The object isn't in this screen or isn't visible. Check:
- Are you on the right screen?
- Is the object hidden?
- Have you examined the area with `LOOK AROUND`?

### The Speed Problem

In [[1988 - Gold Rush\|Gold Rush!]], "the text parser doesn't pause while typing commands"[^ref-gr][^ext-abandonwaredos-gr], meaning the game continued running while you typed. This required fast typing during time-sensitive sequences.

### Spell-Casting Nightmare

[[1986 - King's Quest III - To Heir Is Human\|King's Quest III]] featured the most demanding parser use in Sierra history. Players had to:

1. Follow spell recipes from the physical manual exactly
2. Type every word, comma, and period precisely
3. Complete entire spell sequences without errors

"A single misspelling when casting spells, even when just preparing ingredients, results in spell backfiring with fatal results"[^ref-kq3-gfaqs][^ext-gamefaqs-kq3]. Players often needed **10-15 attempts** to complete spells correctly[^ref-kq3][^ext-diary-kq3]. The parser was described as "stubborn" by reviewers, requiring precise phrasing to accomplish tasks.[^ext-justgames-kq3]

## Humorous Parser Responses

Sierra designers filled their games with witty responses to unusual commands:

### Leisure Suit Larry Series

Typing inappropriate commands in [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards\|Leisure Suit Larry]] yielded memorable responses[^ref-lsl1][^ext-mobygames-lsl1]:

- `MASTURBATE` → "Larry, the whole idea was to stop doing that!"
- `LOOK AT PUSSY` → "Obviously, restraint is no problem for you, Larry"

The [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)\|second game]]'s parser responses were praised as "the only parts of the game that have aged gracefully"[^ref-lsl2-ign][^ext-ign-lsl2].

### King's Quest III

When players used profanity: "Obviously, you were raised by a naughty wizard"[^ref-kq3-easter][^ext-kq-omnipedia].

Typing `EAT CHICKENS` produced: "Sorry, Colonel; they're not even dead yet!"—referencing KFC founder Colonel Sanders[^ref-kq3-easter][^ext-kq-omnipedia].

### Space Quest Series

The Space Quest games rewarded experimentation with the parser. Hidden easter eggs included[^ref-sq1-tcrf][^ext-tcrf-sq1]:
- Typing `KEN` made Ken Williams walk onscreen complaining the game was behind schedule
- A specific dialogue with a Sarien guard about owning King's Quest II awarded 6 bonus points[^ext-sq-historian]

## The Transition to Point-and-Click

### Why the Parser Disappeared

By 1990-1991, Sierra phased out the parser for several reasons:

1. **Accessibility**: "People solved the game much faster because they didn't have to guess which words we wanted them to type"—Al Lowe on [[1991 - Leisure Suit Larry 5 - Passionate Patti Does a Little Undercover Work\|LSL5]][^ref-lsl5][^ext-ign-allowe]

2. **Competition**: LucasArts' SCUMM interface proved more accessible[^ext-hcg101]

3. **Technical Progress**: Mouse-driven interfaces became standard

### The SCI1 Icon Bar

[[Sierra Creative Interpreter\|SCI1]] games (1990-1991) introduced the iconic interface replacing the parser[^ref-sci][^ext-scummvm-sci]:

- **Walk** - Navigate character
- **Look** - Examine objects
- **Hand** - Interact/manipulate
- **Talk** - Converse with characters
- **Inventory** - Access collected items

### Hybrid Approaches

Some later games offered both options:

**[[2014 - Gold Rush Anniversary\|Gold Rush! Anniversary]]** lets players "switch between a traditional text parser interface and a modern point-and-click system at any time"[^ref-gr-ann][^ext-steam-grann]. However, "certain puzzles require switching to typed commands to complete"[^ref-gr-ann].

**[[1996 - Leisure Suit Larry 7 - Love for Sail\|Leisure Suit Larry 7]]** features "a unique hybrid interface that combines point-and-click mechanics with an optional text parser"[^ref-lsl7][^ext-mobygames-lsl7]. The parser remembered previously used commands, allowing players to reuse actions like "fart" throughout the game[^ref-lsl7-parser].

## Parser Era Games

### AGI Era (Text Parser Required)

| Year | Game | Notable Parser Feature |
|------|------|------------------------|
| 1984 | [[1984 - King's Quest - Quest for the Crown\|King's Quest I]] | First graphical adventure parser[^ext-sierra-fandom] |
| 1985 | [[1985 - King's Quest II - Romancing the Throne\|King's Quest II]] | Pull-down menus added (1987 re-release)[^ext-sierra-fandom-kq2] |
| 1986 | [[1986 - King's Quest III - To Heir Is Human\|King's Quest III]] | Complex spell-casting system[^ext-wikipedia-kq3] |
| 1986 | [[1986 - Space Quest - The Sarien Encounter\|Space Quest I]] | Sci-fi vocabulary, witty responses[^ext-mobygames-sq1] |
| 1987 | [[1987 - Space Quest II - Vohaul's Revenge\|Space Quest II]] | Last major AGI release |
| 1987 | [[1987 - Police Quest - In Pursuit of the Death Angel\|Police Quest I]] | Police procedure vocabulary[^ext-mobygames-pq1] |
| 1987 | [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards\|Leisure Suit Larry I]] | Adult humor responses[^ext-mobygames-lsl1] |
| 1988 | [[1988 - Gold Rush\|Gold Rush!]] | Real-time parser (no pause while typing)[^ext-abandonwaredos-gr] |

### SCI0 Era (Parser with Mouse Movement)

| Year | Game | Notable Parser Feature |
|------|------|------------------------|
| 1988 | [[1988 - King's Quest IV - The Perils of Rosella\|King's Quest IV]] | Dual AGI/SCI release |
| 1988 | [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)\|Leisure Suit Larry II]] | Famous parser bug ("PUT BAG")[^ext-allowe-bug] |
| 1989 | [[1989 - Leisure Suit Larry III - Passionate Patti in Pursuit of the Pulsating Pectorals\|Leisure Suit Larry III]] | Last Larry parser game[^ext-acg-lsl3] |
| 1989 | [[1989 - Space Quest III - The Pirates of Pestulon\|Space Quest III]] | Parser with SCI graphics |
| 1989 | [[1989 - Quest for Glory I - So You Want to Be a Hero\|Quest for Glory I]] | RPG elements with parser |

### Simplified/No Parser (Children's Games)

[[1987 - Mixed-Up Mother Goose\|Mixed-Up Mother Goose]] was "deliberately designed to be simple enough that 'even young children can play it when adults are out of the room'"[^ref-mumg]. The AGI implementation was "notably simplified, removing the text parser that was standard in other AGI titles to accommodate non-reading players"[^ref-mumg].

## Playing Parser Games Today

### Tips for Modern Players

1. **Keep notes** on parser vocabulary that works[^ref-agi]
2. **Save frequently**—Sierra games are unforgiving
3. **Be patient** with phrasing—try multiple approaches
4. **Read the manual**—essential for copy protection puzzles and spell systems[^ext-kq-omnipedia]
5. **Use walkthroughs sparingly**—"half the fun is experimentation"[^ref-agi]

### ScummVM Enhancement

ScummVM offers features that ease parser frustration[^ext-scummvm-agi]:
- Save states
- Text input history
- Consistent speed across systems

All AGI and SCI parser games are fully supported[^ref-agi][^ext-scummvm-agi].

## See Also

- [[Adventure Game Interpreter]] – The AGI engine that powered parser games
- [[Sierra Creative Interpreter]] – SCI and the transition to point-and-click
- [[Compatibility Guide]] – Running classic Sierra games today
- [[Engine Index]] – Complete list of Sierra game engines

## Internal References

[^ref-agi]: [[Adventure Game Interpreter]] – Parser vocabulary, interface details, ScummVM support
[^ref-sci]: [[Sierra Creative Interpreter]] – Icon bar interface, SCI evolution
[^ref-kq1]: [[1984 - King's Quest - Quest for the Crown]] – Hybrid keyboard/parser interface, parser commands
[^ref-kq3]: [[1986 - King's Quest III - To Heir Is Human]] – Spell-casting system, parser criticism, 10-15 spell attempts
[^ref-kq3-gfaqs]: [[1986 - King's Quest III - To Heir Is Human]] – GameFAQs review on spell-casting deaths
[^ref-kq3-easter]: [[1986 - King's Quest III - To Heir Is Human]] – Easter egg responses (Colonel Sanders, wizard quote)
[^ref-sq1]: [[1986 - Space Quest - The Sarien Encounter]] – Parser input, sci-fi commands
[^ref-sq1-tcrf]: [[1986 - Space Quest - The Sarien Encounter]] – Ken Williams easter egg, KQ2 bonus points
[^ref-pq1]: [[1987 - Police Quest - In Pursuit of the Death Angel]] – Police procedure commands, protocol requirements
[^ref-lsl1]: [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards]] – Parser responses, humor
[^ref-lsl2]: [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)]] – Parser bug ("PUT BAG")
[^ref-lsl2-ign]: [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)]] – IGN on parser responses
[^ref-lsl3]: [[1989 - Leisure Suit Larry III - Passionate Patti in Pursuit of the Pulsating Pectorals]] – Precise positioning requirements
[^ref-lsl5]: [[1991 - Leisure Suit Larry 5 - Passionate Patti Does a Little Undercover Work]] – Al Lowe on faster gameplay without parser
[^ref-lsl7]: [[1996 - Leisure Suit Larry 7 - Love for Sail]] – Hybrid point-and-click/parser system
[^ref-lsl7-parser]: [[1996 - Leisure Suit Larry 7 - Love for Sail]] – Parser memory feature, "fart" command
[^ref-gr]: [[1988 - Gold Rush]] – Real-time parser without pause
[^ref-gr-ann]: [[2014 - Gold Rush Anniversary]] – Dual interface system, puzzle limitations
[^ref-mumg]: [[1987 - Mixed-Up Mother Goose]] – Simplified interface for children, no parser

## External References

[^ext-hcg101]: [Hardcore Gaming 101 – Space Quest](http://www.hardcoregaming101.net/space-quest/) – Retrospective on parser mechanics, series analysis
[^ext-sierra-fandom]: [Sierra Fandom Wiki – Space Quest: The Sarien Encounter](https://sierra.fandom.com/wiki/Space_Quest%3A_The_Sarien_Encounter_%28AGI%29) – Parser input interface, AGI engine details
[^ext-sierra-fandom-sq1]: [Sierra Fandom Wiki – Space Quest I](https://sierra.fandom.com/wiki/Space_Quest%3A_The_Sarien_Encounter_%28AGI%29) – Parser commands, pseudo-3D environment
[^ext-mobygames-sq1]: [MobyGames – Space Quest I](https://www.mobygames.com/game/114/space-quest-chapter-i-the-sarien-encounter/) – Technical specifications, credits
[^ext-mobygames-pq1]: [MobyGames – Police Quest I](https://www.mobygames.com/game/145/police-quest-in-pursuit-of-the-death-angel/) – Police procedure commands, game mechanics
[^ext-mobygames-lsl1]: [MobyGames – Leisure Suit Larry I](https://www.mobygames.com/game/379/leisure-suit-larry-in-the-land-of-the-lounge-lizards/) – Parser responses, adult humor
[^ext-wikipedia-kq3]: [Wikipedia – King's Quest III](https://en.wikipedia.org/wiki/King%27s_Quest_III) – Release dates, spell-casting system, technical firsts
[^ext-gamefaqs-kq3]: [GameFAQs – King's Quest III User Review](https://gamefaqs.gamespot.com/appleii/938229-kings-quest-iii-to-heir-is-human/reviews/74441) – Spell mechanic criticism, death on typos
[^ext-justgames-kq3]: [Just Games Retro – King's Quest III](https://www.justgamesretro.com/dos/kings-quest-iii-to-heir-is-human) – Parser stubbornness, version differences
[^ext-diary-kq3]: [Diary of a Part Time Writer – King's Quest III](https://diaryofapartimewriter.wordpress.com/tag/kings-quest-iii-to-heir-is-human/) – Spell attempt counts, magic map mechanic
[^ext-kq-omnipedia]: [King's Quest Omnipedia – King's Quest III](https://kingsquest.fandom.com/wiki/King%27s_Quest_III:_To_Heir_is_Human_(1987)) – Easter eggs, copy protection, manual requirements
[^ext-allowe-bug]: [Al Lowe Official Site – Clues and Cheats](https://allowe.com/games/larry/tips-manuals/clues-cheats.html) – LSL2 parser bug explanation, development anecdote
[^ext-ign-lsl2]: [IGN – Revisiting Leisure Suit Larry](https://www.ign.com/articles/2014/11/28/revisiting-leisure-suit-larry) – Parser responses praised as aging gracefully
[^ext-acg-lsl3]: [Adventure Classic Gaming – LSL3 Review](https://www.adventureclassicgaming.com/index.php/site/reviews/355/) – Positioning requirements, interface rigidity
[^ext-ign-allowe]: [IGN – Talking Leisure Suit Larry with Al Lowe](https://www.ign.com/articles/talking-leisure-suit-larry-with-al-lowe) – Al Lowe on parser vs point-and-click accessibility
[^ext-abandonwaredos-gr]: [Abandonware DOS – Gold Rush!](https://www.abandonwaredos.com/abandonware-game.php?abandonware=Gold+Rush!&gid=324) – Real-time parser mechanic
[^ext-steam-grann]: [Steam – Gold Rush! Anniversary](https://store.steampowered.com/app/319230/Gold_Rush_Anniversary/) – Dual interface system description
[^ext-mobygames-lsl7]: [MobyGames – Leisure Suit Larry 7](https://www.mobygames.com/game/1102/leisure-suit-larry-love-for-sail/) – Hybrid interface, parser memory feature
[^ext-tcrf-sq1]: [The Cutting Room Floor – Space Quest I](https://tcrf.net/Space_Quest:_Chapter_I_-_The_Sarien_Encounter_(1986)) – Ken Williams easter egg, hidden content
[^ext-sq-historian]: [Space Quest Historian – 11 Things You Didn't Know About Space Quest](https://www.youtube.com/watch?v=Hvux-A0oGiM) – Ken Williams easter egg programming anecdote
[^ext-scummvm-agi]: [ScummVM Wiki – Space Quest](https://wiki.scummvm.org/index.php?title=Space_Quest) – AGI support, platform compatibility
[^ext-scummvm-sci]: [ScummVM Wiki – SCI](https://wiki.scummvm.org/index.php?title=SCI) – SCI engine support, interface evolution
[^ext-sierra-fandom-kq2]: [Sierra Fandom Wiki – King's Quest II](https://sierra.fandom.com/wiki/King%27s_Quest_II:_Romancing_the_Throne) – 1987 re-release with pull-down menus
