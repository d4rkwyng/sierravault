---
title: "Sierra Parser Commands Guide"
type: guide
topic: "Text Parser Interface"
engines: ["AGI", "SCI0", "SCI1"]
years_covered: "1984-1991"
last_updated: '2026-10-26'
---

# Sierra Parser Commands Guide

<small style="color: gray">Last updated: October 26, 2026</small>

## Overview

The text parser was Sierra On-Line's primary interface for adventure games from 1984 to 1991, requiring players to type commands to interact with game worlds. This system powered the [[Adventure Game Interpreter|AGI]] engine era (1984-1989) and continued into the early [[Sierra Creative Interpreter|SCI]] era (1988-1991) before being replaced by point-and-click interfaces.

Understanding the parser is essential for playing classic Sierra adventures—from [[1984 - King's Quest - Quest for the Crown|King's Quest]] through [[1990 - Quest for Glory II - Trial by Fire|Quest for Glory II]]—and can mean the difference between frustration and enjoyment.

## What is a Text Parser?

A text parser is an input system that interprets typed commands and translates them into game actions. Each AGI game carried its own vocabulary file (WORDS.TOK), "the dictionary of words that the interpreter understands"; several words could share one word number, so synonyms behaved alike, and filler words such as "the" and "at" were simply ignored.[^ext-agispec] Vocabulary size varied by title: [[1986 - King's Quest III - To Heir Is Human|King's Quest III]]'s parser "was improved from the previous games to understand more words."[^ext-wikipedia-kq3]

Sierra's 1987 MS-DOS reference card for its "3-D animated adventures" told players: "Talk to your computer in commands of one or two words, or even simple sentences." Its examples were:[^ext-kq-refcard]
- `TALK TO THE GNOME`
- `GET THE KEY`
- `LOOK AT THE SHIP`
- `GIVE THE BASKET TO THE GIRL`

Players typed commands into a text input line while controlling their character with arrow keys or joystick. *Electronic Games* (December 1984) called King's Quest "a major breakthrough in action-adventure games," saying its "combination of keyboard-input and joystick-operated on-screen character movement blows everything away."[^ref-kq1][^ext-eg-1984]

### How It Worked

1. Player positions character near an object or person
2. Player types a command (e.g., `LOOK AT THE SHIP`)[^ext-kq-refcard]
3. Parser analyzes the text for recognized verbs and nouns
4. If understood, the game executes the action
5. If not understood, the game replies with a message saying so (wording varies by game)

Discovering the designers' witty replies to odd commands became part of the entertainment (see [Humorous Parser Responses](#humorous-parser-responses) below).

## Common Verbs and Commands

### Essential Verbs

Common verbs seen in Sierra parser games, with examples taken from Sierra's own reference card or from the cited game sources (exact vocabulary varied from game to game, so check each game's manual):

| Verb | Function | Example | Source |
|------|----------|---------|--------|
| TALK | Speak to characters | `TALK TO THE GNOME` | Sierra reference card[^ext-kq-refcard] |
| GET | Pick up items | `GET THE KEY` | Sierra reference card[^ext-kq-refcard] |
| LOOK | Examine an object closely | `LOOK AT THE SHIP` | Sierra reference card[^ext-kq-refcard] |
| GIVE | Give inventory items | `GIVE THE BASKET TO THE GIRL` | Sierra reference card[^ext-kq-refcard] |
| SLOW / FAST / NORMAL | Change animation speed | `FAST` | Sierra reference card[^ext-kq-refcard] |
| SAVE / RESTORE | Save or restore the game | `SAVE GAME`, `RESTORE GAME` | Sierra reference card[^ext-kq-refcard] |
| USE | Use an item on something | `USE KEY ON LOCK` | King's Quest III[^ext-wikipedia-kq3] |
| PUT | Place items | `PUT THE BAG IN BOTTLE` | Leisure Suit Larry II[^ext-allowe-bug] |
| READ | Read something aloud | `READ RIGHTS` | Police Quest I[^ext-sierrahelp-pq1] |
| PRESS | Operate controls | `PRESS BUTTON` | Space Quest I[^ext-sierrahelp-sq1] |

### Game-Specific Commands

Different series required specialized vocabulary:

**[[Police Quest Series|Police Quest]]**[^ref-pq1][^ext-mobygames-pq1][^ext-sierrahelp-pq1]:
- `HANDCUFF SUSPECT` / `CUFF SUSPECT` - Handcuff suspects
- `SEARCH PRISONER` - Pat down suspects
- `READ RIGHTS` - Read a suspect his rights
- `WRITE TICKET` - Issue a traffic citation
- `BOOK HIM` (for `FELONY`) - Book a prisoner at the jail

**[[Space Quest Series|Space Quest]]**[^ref-sq1][^ext-sierra-fandom-sq1]:
- `PRESS BUTTON` - Operate controls (e.g. the escape pod's launch button)[^ext-sq1-points][^ext-sierrahelp-sq1]

**[[1986 - King's Quest III - To Heir Is Human|King's Quest III]]** spell-casting[^ref-kq3][^ext-wikipedia-kq3]:
- Spell steps are listed in the game's manual, not in the game itself
- Commands had to follow the manual's wording
- A misspelling during a spell could make it backfire fatally[^ext-gamefaqs-kq3]

## Parser Tips and Tricks

### Phrasing Matters

The parser was notoriously literal. If one phrasing doesn't work, try alternatives:

❌ `PUT BAG BOTTLE` (fails due to parser bug in [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)|LSL2]][^ref-lsl2][^ext-allowe-bug])
✅ `PUT THE BAG IN BOTTLE`

As Al Lowe explained: "The day before the game shipped, the system programmer in charge of 'the parser' fixed a bug that I'd been complaining about for days. He assured me he changed nothing else. I foolishly added the new code to the game."[^ext-allowe-bug] The bug causes commands like "PUT BAG BOTTLE" to fail because the parser incorrectly treats "bag" as a verb rather than a noun. "16 years later, I'm still answering emails about a bug I swear I didn't create!"[^ext-allowe-bug]

### Positioning is Critical

Most commands only work when your character is standing close enough to the object; Wikipedia's King's Quest III article notes that "get stone" only has an effect if Gwydion "is standing in a part of a screen where there is a stone present."[^ext-wikipedia-kq3] Hardcore Gaming 101 called the [[1989 - Space Quest III - The Pirates of Pestulon|Space Quest III]] parser "extremely fussy with your positioning."[^ext-hg101-sq3]

- Walk **directly next** to objects before interacting
- Some commands only work from specific screen positions
- If a command fails, try moving closer

### Common Frustrations

The exact wording of error messages differs between games, but failures generally fall into a few kinds:

**The parser doesn't recognize a word**
The word isn't in that game's vocabulary file. Try:
- Simpler phrasing
- Different synonyms (games often map several words to the same meaning)[^ext-agispec]
- Articles such as "the" are ignored by the AGI parser, so adding or removing them rarely matters[^ext-agispec]

**The parser understands, but the action isn't possible**
Either:
- Wrong location/timing
- Inventory item required
- Different approach needed

**The object isn't here**
The object isn't in this screen or isn't visible. Check:
- Are you on the right screen?
- Is the object hidden?
- Have you looked around the room?

### The Speed Problem

In AGI games such as [[1988 - Gold Rush|Gold Rush!]], the game kept running while you typed. George Starostin describes Gold Rush! as using "Sierra's standard AGI interface of the time, including the old version of the text parser in which the game does not pause while you are typing in commands, something that can be quite a hassle if you are playing against a rigidly timed puzzle."[^ref-gr][^ext-starostin-gr]

### Spell-Casting Nightmare

[[1986 - King's Quest III - To Heir Is Human|King's Quest III]] made especially heavy demands on the parser. Its spells and potions are made by following steps listed in the game's manual, not in the game itself[^ext-wikipedia-kq3], so players had to:

1. Follow spell recipes from the physical manual
2. Type each step carefully
3. Complete entire spell sequences without errors

A GameFAQs reviewer wrote: "Casting spells is a bit nerve-wracking since a single misspelling, even when just preparing the ingredients, results in the spell backfiring with fatal results."[^ref-kq3-gfaqs][^ext-gamefaqs-kq3] One blogger recalled that "sometimes I had to try upwards of ten or fifteen times before I got the ingredients, directions, incantation, and spell storage right."[^ext-diary-kq3] Just Games Retro listed "Parser is still stubborn" among the game's faults.[^ext-justgames-kq3]

## Humorous Parser Responses

Sierra designers filled their games with witty responses to unusual commands:

### Leisure Suit Larry Series

Typing inappropriate commands in [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards|Leisure Suit Larry]] yielded memorable responses[^ref-lsl1][^ext-hg101-lsl1]:

- `MASTURBATE` → "Larry, the whole idea was to stop doing that!"
- `LOOK AT PUSSY` → "Obviously, restraint is no problem for you, Larry."

IGN's retrospective, writing about the first game, said "the clever and often funny parser responses are also probably the only parts of the game that have aged gracefully," adding that they were wordy "as seen in the first game and especially the [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)|second]]."[^ref-lsl2-ign][^ext-ign-lsl2]

### King's Quest III

When players used profanity: "Obviously, you were raised by a naughty wizard"[^ref-kq3-easter][^ext-kq-omnipedia].

Typing `EAT CHICKENS` produced: "Sorry, Colonel; they're not even dead yet!"—referencing KFC founder Colonel Sanders[^ref-kq3-easter][^ext-kq-omnipedia].

### Space Quest Series

The Space Quest games rewarded experimentation with the parser. Hidden easter eggs in [[1986 - Space Quest - The Sarien Encounter|Space Quest I]] included[^ref-sq1-tcrf]:
- In early versions only, typing `KEN` on the first screen made Ken Williams appear, "complaining how the game was behind schedule"; it was removed from later versions[^ext-sierrahelp-sqeggs]
- Saying "yes" when a Sarien guard asks about King's Quest II is worth 5 points (plus 1 point for talking to him)[^ext-sq1-points][^ext-sq-historian]

## The Transition to Point-and-Click

### Why the Parser Disappeared

By 1990-1991, Sierra phased out the parser for several reasons:

1. **Accessibility**: "People solved the game much faster because they didn't have to guess which words we wanted them to type"—Al Lowe on [[1991 - Leisure Suit Larry 5 - Passionate Patti Does a Little Undercover Work|LSL5]][^ref-lsl5][^ext-ign-allowe]

2. **Technical Progress**: SCI1's VGA debut was [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest V]] in 1990, and Wikipedia says SCI1 "combined 256-color VGA graphics with an icon-driven interface"[^ext-wikipedia-sci]; [[1990 - Quest for Glory II - Trial by Fire|Quest for Glory II]] had already used an earlier, EGA-only SCI1 build[^ext-scummvm-sgv] and kept the parser[^ext-wikipedia-qfg2]

### The SCI1 Icon Bar

SCI1's VGA debut, King's Quest V (1990), introduced the icon interface that replaced the parser[^ref-sci][^ext-wikipedia-sci]; the EGA-only [[Sierra Creative Interpreter|SCI1]] build used by Quest for Glory II still had the parser[^ext-scummvm-sgv][^ext-wikipedia-qfg2]:

- **Walk** - Navigate character
- **Look** - Examine objects
- **Hand** - Interact/manipulate
- **Talk** - Converse with characters
- **Inventory** - Access collected items

### Hybrid Approaches

Some later games offered both options:

**[[2014 - Gold Rush Anniversary|Gold Rush! Anniversary]]** offers, in its Steam listing's words, "Two possibilities for controlling (original parser as well as a new intelligent Point&Click control)."[^ref-gr-ann][^ext-steam-grann]

**[[1996 - Leisure Suit Larry 7 - Love for Sail|Leisure Suit Larry 7]]** combines point-and-click play with an optional typed-command box[^ref-lsl7][^ext-mobygames-lsl7]. The game remembers commands you have typed, so actions like "fart" are added to your list for reuse; A Force For Good noted, "if you've farted once, it's added to your list of actions!"[^ref-lsl7-parser][^ext-forceforgood-lsl7]

## Parser Era Games

### AGI Era (Text Parser Required)

- **1984** — [[1984 - King's Quest - Quest for the Crown|King's Quest I]] — Notable Parser Feature: Typed commands plus an animated, on-screen hero (IEEE Spectrum calls it "the first animated 3D adventure game"; the first graphical adventure was On-Line Systems' 1980 *Mystery House*)[^ext-ieee-kq1][^ext-wikipedia-mh]
- **1985** — [[1985 - King's Quest II - Romancing the Throne|King's Quest II]] — Notable Parser Feature: Pull-down menus added (1987 re-release)[^ext-sierra-fandom-kq2]
- **1986** — [[1986 - King's Quest III - To Heir Is Human|King's Quest III]] — Notable Parser Feature: Complex spell-casting system[^ext-wikipedia-kq3]
- **1986** — [[1986 - Space Quest - The Sarien Encounter|Space Quest I]] — Notable Parser Feature: Sci-fi vocabulary, hidden parser easter eggs[^ext-mobygames-sq1][^ext-sierrahelp-sqeggs]
- **1987** — [[1987 - Space Quest II - Vohaul's Revenge|Space Quest II]] — Notable Parser Feature: Sci-fi sequel on the same AGI parser[^ext-scummvm-agilist]
- **1987** — [[1987 - Police Quest - In Pursuit of the Death Angel|Police Quest I]] — Notable Parser Feature: Police procedure vocabulary[^ext-mobygames-pq1]
- **1987** — [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards|Leisure Suit Larry I]] — Notable Parser Feature: Adult humor responses[^ext-mobygames-lsl1][^ext-hg101-lsl1]
- **1988** — [[1988 - Gold Rush|Gold Rush!]] — Notable Parser Feature: Sierra's standard AGI parser, which (like other AGI games) does not pause while you type[^ext-starostin-gr]

Later AGI parser releases also included the AGI version of King's Quest IV (1988).[^ext-scummvm-agilist] [[1988 - Manhunter - New York|Manhunter: New York]] (1988) also ran on AGI but had no text parser (see below).[^ext-wikipedia-mhny]

### SCI0 Era (Parser with Mouse Movement)

- **1988** — [[1988 - King's Quest IV - The Perils of Rosella|King's Quest IV]] — Notable Parser Feature: SCI engine debut, also released in an AGI version[^ext-wikipedia-sci][^ext-scummvm-agilist]
- **1988** — [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)|Leisure Suit Larry II]] — Notable Parser Feature: Famous parser bug ("PUT BAG")[^ext-allowe-bug]
- **1989** — [[1989 - Leisure Suit Larry III - Passionate Patti in Pursuit of the Pulsating Pectorals|Leisure Suit Larry III]] — Notable Parser Feature: Last fully parser-driven Larry; the next Larry game, [[1991 - Leisure Suit Larry 5 - Passionate Patti Does a Little Undercover Work|LSL5]], dropped typing[^ext-acg-lsl3][^ext-ign-allowe]
- **1989** — [[1989 - Space Quest III - The Pirates of Pestulon|Space Quest III]] — Notable Parser Feature: Parser with SCI graphics
- **1989** — [[1989 - Quest for Glory I - So You Want to Be a Hero|Quest for Glory I]] — Notable Parser Feature: RPG elements with parser

Other SCI0 parser games with vault pages include [[1988 - Police Quest II - The Vengeance|Police Quest II]] (1988), [[1989 - The Colonel's Bequest|The Colonel's Bequest]] (1989), [[1990 - Codename - Iceman|Codename: ICEMAN]], [[1990 - Conquests of Camelot - The Search for the Grail|Conquests of Camelot]] and the [[1990 - Roberta Williams' King's Quest I - Quest for the Crown|1990 SCI remake of King's Quest I]]. [[1990 - Quest for Glory II - Trial by Fire|Quest for Glory II]] (1990) also kept the text parser, but ScummVM's version list places it under SCI1 (EGA), not SCI0.[^ext-scummvm-sgv]

### Simplified/No Parser

In [[1986 - The Black Cauldron|The Black Cauldron]] (1986), made to be more accessible to children, "the text parser was removed in favor of the function keys."[^ext-wikipedia-bc]

Like The Black Cauldron before it, [[1987 - Mixed-Up Mother Goose|Mixed-Up Mother Goose]] was designed for young children, and its AGI version did away with the text parser so that non-readers could play[^ref-mumg].

[[1988 - Manhunter - New York|Manhunter: New York]] (1988) used AGI too, but Wikipedia notes it "did not use a text parser" and "featured a rudimentary point-and-click interface."[^ext-wikipedia-mhny]

## Playing Parser Games Today

### Tips for Modern Players

1. **Keep notes** on parser vocabulary that works[^ref-agi]
2. **Save frequently**—Sierra games are unforgiving
3. **Be patient** with phrasing—try multiple approaches
4. **Read the manual**—essential for copy protection puzzles and spell systems[^ext-kq-omnipedia]
5. **Use walkthroughs sparingly**—much of the fun is in experimenting with the parser

### ScummVM Enhancement

ScummVM supports Sierra's AGI games; its wiki lists Space Quest as supported in its AGI version since ScummVM 0.10.0 and its SCI version since 1.2.0.[^ref-agi][^ext-scummvm-agi] For AGI games it adds a **Predictive Input Dialog**, "a ScummVM aid for running AGI engine games (which notoriously require command line input) on devices with limited keyboard support."[^ext-scummvm-agi]

## See Also

- [[Adventure Game Interpreter]] – The AGI engine that powered parser games
- [[Sierra Creative Interpreter]] – SCI and the transition to point-and-click
- [[Compatibility Guide]] – Running classic Sierra games today
- [[Engine Index]] – Complete list of Sierra game engines

## Internal References

[^ref-agi]: [[Adventure Game Interpreter]] – Parser vocabulary, interface details, ScummVM support
[^ref-sci]: [[Sierra Creative Interpreter]] – Icon bar interface, SCI evolution
[^ref-kq1]: [[1984 - King's Quest - Quest for the Crown]] – Hybrid keyboard/parser interface, parser commands
[^ref-kq3]: [[1986 - King's Quest III - To Heir Is Human]] – Spell-casting system, parser criticism
[^ref-kq3-gfaqs]: [[1986 - King's Quest III - To Heir Is Human]] – GameFAQs review on spell-casting deaths
[^ref-kq3-easter]: [[1986 - King's Quest III - To Heir Is Human]] – Easter egg responses (Colonel Sanders, wizard quote)
[^ref-sq1]: [[1986 - Space Quest - The Sarien Encounter]] – Parser interface
[^ref-sq1-tcrf]: [[1986 - Space Quest - The Sarien Encounter]] – Ken Williams easter egg, King's Quest II guard exchange
[^ref-pq1]: [[1987 - Police Quest - In Pursuit of the Death Angel]] – Parser interface
[^ref-lsl1]: [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards]] – Parser responses, humor
[^ref-lsl2]: [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)]] – Parser bug ("PUT BAG")
[^ref-lsl2-ign]: [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)]] – IGN on parser responses
[^ref-lsl5]: [[1991 - Leisure Suit Larry 5 - Passionate Patti Does a Little Undercover Work]] – Al Lowe on faster gameplay without parser
[^ref-lsl7]: [[1996 - Leisure Suit Larry 7 - Love for Sail]] – Hybrid point-and-click/parser system
[^ref-lsl7-parser]: [[1996 - Leisure Suit Larry 7 - Love for Sail]] – Parser memory feature, "fart" command
[^ref-gr]: [[1988 - Gold Rush]] – Standard AGI parser that does not pause while typing
[^ref-gr-ann]: [[2014 - Gold Rush Anniversary]] – Dual interface system
[^ref-mumg]: [[1987 - Mixed-Up Mother Goose]] – Simplified interface for children, no parser

## External References

[^ext-sierra-fandom-sq1]: [Sierra Fandom Wiki – Space Quest I](https://sierra.fandom.com/wiki/Space_Quest%3A_The_Sarien_Encounter_%28AGI%29) – Parser commands, pseudo-3D environment
[^ext-mobygames-sq1]: [MobyGames – Space Quest I](https://www.mobygames.com/game/114/space-quest-chapter-i-the-sarien-encounter/) – Technical specifications, credits
[^ext-mobygames-pq1]: [MobyGames – Police Quest I](https://www.mobygames.com/game/146/police-quest-in-pursuit-of-the-death-angel/) – Parser-based police adventure
[^ext-mobygames-lsl1]: [MobyGames – Leisure Suit Larry I](https://www.mobygames.com/game/379/leisure-suit-larry-in-the-land-of-the-lounge-lizards/) – Parser-driven adult comedy adventure
[^ext-wikipedia-kq3]: [Wikipedia – King's Quest III](https://en.wikipedia.org/wiki/King%27s_Quest_III) – Contextual commands ("get stone", "use key on lock"), spells listed only in the manual, parser that understands more words
[^ext-gamefaqs-kq3]: [GameFAQs – King's Quest III User Review](https://gamefaqs.gamespot.com/appleii/938229-kings-quest-iii-to-heir-is-human/reviews/74441) – Spell mechanic criticism, death on typos
[^ext-justgames-kq3]: [Just Games Retro – King's Quest III](https://www.justgamesretro.com/dos/kings-quest-iii-to-heir-is-human) – Parser stubbornness, version differences
[^ext-diary-kq3]: [Diary of a Part Time Writer – King's Quest III](https://diaryofapartimewriter.wordpress.com/tag/kings-quest-iii-to-heir-is-human/) – Spell attempt counts, magic map mechanic
[^ext-kq-omnipedia]: [King's Quest Omnipedia – King's Quest III](https://kingsquest.fandom.com/wiki/King%27s_Quest_III:_To_Heir_is_Human_(1987)) – Easter eggs, copy protection, manual requirements
[^ext-allowe-bug]: [Al Lowe Official Site – Clues and Cheats](https://allowe.com/games/larry/tips-manuals/clues-cheats.html) – LSL2 parser bug explanation, development anecdote
[^ext-ign-lsl2]: [IGN – Revisiting Leisure Suit Larry](https://www.ign.com/articles/2014/11/28/revisiting-leisure-suit-larry) – Parser responses "aged gracefully" (said in the LSL1 section, referring to the first and second games)
[^ext-acg-lsl3]: [Adventure Classic Gaming – LSL3 Review](https://www.adventureclassicgaming.com/index.php/site/reviews/355/) – Inventory use "depends entirely on typing in the correct commands into the text parser"
[^ext-ign-allowe]: [IGN – Talking Leisure Suit Larry with Al Lowe](https://www.ign.com/articles/talking-leisure-suit-larry-with-al-lowe) – Al Lowe on parser vs point-and-click accessibility
[^ext-steam-grann]: [Steam – Gold Rush! Anniversary](https://store.steampowered.com/app/319230/Gold_Rush_Anniversary/) – Dual interface system description
[^ext-mobygames-lsl7]: [MobyGames – Leisure Suit Larry 7](https://www.mobygames.com/game/381/leisure-suit-larry-love-for-sail/) – Hybrid point-and-click and typed-command interface
[^ext-sq-historian]: [Space Quest Historian – 11 Things You Probably Didn't Know About Space Quest](https://www.youtube.com/watch?v=Hvux-A0oGiM) – Chapter "The Sarien King's Quest fan (SQ1)" at 11:20, per the video's chapter list
[^ext-scummvm-agi]: [ScummVM Wiki – Space Quest (Wayback, 2024-08-09)](https://web.archive.org/web/20240809115745/https://wiki.scummvm.org/index.php?title=Space_Quest) – AGI support since 0.10.0, SCI since 1.2.0; Predictive Input Dialog
[^ext-sierra-fandom-kq2]: [Sierra Fandom Wiki – King's Quest II](https://sierra.fandom.com/wiki/King%27s_Quest_II:_Romancing_the_Throne) – 1987 re-release with pull-down menus
[^ext-agispec]: [AGI Specifications, ch. 10 – Other game data (Lance Ewing)](https://www.agidev.com/articles/agispec/agispecs-10.html) – WORDS.TOK is "the dictionary of words that the interpreter understands"; word number 0 = "Words are ignored (e.g. the, at)"
[^ext-eg-1984]: [Electronic Games, December 1984 (archive.org scan, OCR text)](https://archive.org/stream/Electronic_Games_Volume_02_Number_17_1984-12_Reese_Communications_US/Electronic_Games_Volume_02_Number_17_1984-12_Reese_Communications_US_djvu.txt) – "Passport to Adventure": "King's Quest is a major breakthrough in action-adventure games"
[^ext-sierrahelp-pq1]: [Sierra Help – Police Quest AGI Walkthrough](https://sierrahelp.com/Walkthroughs/PQ1AGIWalkthrough.html) – WRITE TICKET, HANDCUFF SUSPECT, CUFF SUSPECT, SEARCH PRISONER, READ RIGHTS, booking at the jail
[^ext-sq1-points]: [The Broomcloset – Space Quest 1 Complete Point List](https://wiw.org/~jess/sq1pts.html) – "Talk to Sarien Guard 1", "Say 'Yes' Regarding King's Quest II 5", "Press Launch Button 3"
[^ext-hg101-sq3]: [Hardcore Gaming 101 – Space Quest III](http://www.hardcoregaming101.net/space-quest-iii/) – "the parser is extremely fussy with your positioning"
[^ext-starostin-gr]: [George Starostin – Review: Gold Rush! (1988)](https://onlysolitaire.substack.com/p/review-gold-rush-1988) – "the game does not pause while you are typing in commands"
[^ext-hg101-lsl1]: [Hardcore Gaming 101 – Leisure Suit Larry in the Land of the Lounge Lizards](http://www.hardcoregaming101.net/leisure-suit-larry-in-the-land-of-the-lounge-lizards/) – Both quoted parser responses verbatim
[^ext-sierrahelp-sqeggs]: [Sierra Help – Space Quest Easter Eggs](https://sierrahelp.com/Misc/EasterEggs/SQEasterEggs.html) – "In early versions of the game, type 'ken' on the first screen"; eliminated in later versions
[^ext-wikipedia-sci]: [Wikipedia – Sierra Creative Interpreter](https://en.wikipedia.org/wiki/Sierra%27s_Creative_Interpreter) – SCI0 debut with King's Quest IV; SCI1 with King's Quest V (1990), "icon-driven interface"
[^ext-forceforgood-lsl7]: [A Force For Good – Leisure Suit Larry: Love for Sail!](https://forceforgood.co.uk/adventure/leisure-suit-larry-love-for-sail/) – "I like the way it remembers the ones you've used before"
[^ext-ieee-kq1]: [IEEE Spectrum – Meet Roberta Williams](https://spectrum.ieee.org/meet-roberta-williams-the-queen-of-graphic-adventure-video-games) – King's Quest, "the first animated 3D adventure game"
[^ext-wikipedia-mh]: [Wikipedia – Mystery House](https://en.wikipedia.org/wiki/Mystery_House) – "Mystery House is the first graphical adventure game"
[^ext-scummvm-agilist]: [ScummVM Wiki – AGI (Wayback, 2025-01-01)](https://web.archive.org/web/20250101192119/https://wiki.scummvm.org/index.php?title=AGI) – Sierra AGI game list incl. Gold Rush (1988), King's Quest IV (1988), Manhunter (1988), Manhunter 2 (1989)
[^ext-scummvm-sgv]: [ScummVM Wiki – Sierra Game Versions (Wayback, May 2024)](http://web.archive.org/web/20240518064410/https://wiki.scummvm.org/index.php/Sierra_Game_Versions) – Quest for Glory II listed in the "SCI1 (ega)" table
[^ext-kq-refcard]: [Sierra 3-D Animated Adventure Game Reference Card for MS-DOS, 1987 (archive.org scan, "king's quest - ref card")](https://archive.org/details/kings_quest_-_ref_card) – "Talk to your computer in commands of one or two words, or even simple sentences"; TALK TO THE GNOME, GET THE KEY, LOOK AT THE SHIP, GIVE THE BASKET TO THE GIRL
[^ext-sierrahelp-sq1]: [Sierra Help – Space Quest 1 AGI Walkthrough](https://sierrahelp.com/Walkthroughs/SQ1AGIWalkthrough.html) – "Press button on control panel marked open bay door", "Press autonav button"
[^ext-wikipedia-mhny]: [Wikipedia – Manhunter: New York](https://en.wikipedia.org/wiki/Manhunter:_New_York) – "did not use a text parser… featured a rudimentary point-and-click interface"
[^ext-wikipedia-bc]: [Wikipedia – The Black Cauldron (video game)](https://en.wikipedia.org/wiki/The_Black_Cauldron_(video_game)) – "the text parser was removed in favor of the function keys"
[^ext-wikipedia-qfg2]: [Wikipedia – Quest for Glory II: Trial by Fire](https://en.wikipedia.org/wiki/Quest_for_Glory_II:_Trial_by_Fire) – "The game's interface is a text parser"
