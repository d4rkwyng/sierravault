---
title: "Adventure Game Interpreter (AGI)"
type: technology
developer: "Sierra On-Line"
years_active: "1984-1989"
total_games: 14
last_updated: "2026-10-26"
---

# Adventure Game Interpreter (AGI)

<small style="color: gray">Last updated: October 26, 2026</small>

## Overview

The Adventure Game Interpreter (AGI) was the engine Sierra On-Line built for *King's Quest* (1984), with Ken Williams and Jeff Stephenson as its authors.[^ref-1] A year before the PCjr was announced, IBM asked Sierra "to create a game that would show off the new computer's color graphics capabilities"; eighteen months later Roberta Williams and a team of six programmers and artists had finished *King's Quest*.[^ref-2] AGI was not Sierra's first engine — the Hi-Res Adventures, beginning with *Mystery House* (1980), the first graphical adventure game, ran on Ken Williams' Adventure Development Language (ADL)[^ref-3][^ref-4] — but it was the first to show an animated character moving through graphical scenes. *Electronic Games* called *King's Quest* "a major breakthrough in action-adventure games".[^ref-5] Sierra used AGI for 14 games between 1984 and 1989 before replacing it with the [[Sierra Creative Interpreter]] (SCI).[^ref-1]

Most AGI games combine a 160×200 logical resolution, 16 colours, a typed text parser and a pseudo-3D perspective that lets characters walk in front of and behind background objects. AGI games with no parser at all include [[1986 - The Black Cauldron|The Black Cauldron]], [[1987 - Mixed-Up Mother Goose|Mixed-Up Mother Goose]] and [[1988 - Manhunter - New York|Manhunter: New York]] (see their pages).

## Technical Specifications

| Specification | Details |
|---------------|---------|
| Logical resolution | 160×200; each AGI pixel is two EGA pixels wide[^ref-6] |
| Colour depth | 16 colours |
| Graphics modes | CGA, Hercules and EGA in the interpreter's monitor-type variable;[^ref-7] PCjr/Tandy versions;[^ref-8] DOS Days adds MCGA and, in later AGI2 versions, VGA (unconfirmed elsewhere)[^ref-9] |
| Interface | Text parser (typed commands) in most games |
| Audio | PC speaker (melody only), Tandy/PCjr three voices plus noise, Apple IIgs wavetable music and sampled effects[^ref-10] |
| Memory required | *King's Quest*: 128K[^ref-2][^ref-5] |

## Graphics System

### Pseudo-3D Environment
Characters walk both horizontally and vertically, and the interpreter decides whether they appear in front of or behind scenery from a hidden priority screen.[^ref-11]

### Drawing Priority
Each PICTURE resource draws two screens at once: the "picture" screen the player sees, and a "priority" screen "held in memory" that "contains control information invisible to the player". As a picture is drawn, "both screens are updated depending on whether drawing is enabled from each screen".[^ref-11] For *King's Quest*, artists drew each of the 80 scenes in colour and traced them on a Calcomp graphics tablet, which generated the drawing instructions automatically.[^ref-2]

### Character Animation
Characters and objects are VIEW resources, stored as bitmaps. Each view holds one or more loops, each loop one or more cels (frames); the interpreter supports up to 255 loops per view and 255 cels per loop.[^ref-6]

## Audio Capabilities

AGI's audio support varied by platform:

| Platform | Audio capability |
|----------|------------------|
| IBM PC | PC speaker plays the melody voice only[^ref-10] |
| Tandy 1000 / PCjr | Three voices plus noise[^ref-10] |
| Amiga | Three-voice soundtrack (*Space Quest*)[^ref-12] |
| Apple IIgs | "16 channel wavetable based MIDI songs" and "digitally sampled PCM sound effects";[^ref-10] *Space Quest* had a "fifteen-voice soundtrack with notably richer sound"[^ref-12] |

The sound data for the MS-DOS, Tandy and Macintosh versions has the same four parts: a melody, two accompaniment voices and a noise channel.[^ref-10]

## Interface Evolution

### Text Parser
Players typed short commands such as:
- `LOOK TREE`
- `GET SWORD`
- `TALK MAN`
- `OPEN DOOR`

Each game's vocabulary is stored in its `words.tok` file, "the dictionary of words that the interpreter understands"; many words can share a word number, so synonyms are treated alike.[^ref-13] Roberta Williams said in 1985 that she wished the *King's Quest* "language interpreter had a larger vocabulary".[^ref-2]

### Game logic
Each room's behaviour was written in Sierra's "Game Adaptation Language", a set of IF-THEN statements the program "constantly loops through".[^ref-2]

### Pull-Down Menus (AGI2, 1986)
AGI1 games had no drop-down menus. Around 1986 Sierra's AGI2 added a dropdown menu bar and selectable animation speeds;[^ref-9] *King's Quest III* (interpreter 2.272) is dated November 8, 1986.[^ref-8]

## Games Using AGI

The 14 Sierra AGI games, per the ScummVM wiki:[^ref-14][^ref-1]

### King's Quest Series
- [[1984 - King's Quest - Quest for the Crown]] - AGI debut
- [[1985 - King's Quest II - Romancing the Throne]]
- [[1986 - King's Quest III - To Heir Is Human]]
- [[1988 - King's Quest IV - The Perils of Rosella]] - released in both AGI and SCI versions; the AGI 2.0 build is dated July 27, 1988[^ref-8]

### Space Quest Series
- [[1986 - Space Quest - The Sarien Encounter]]
- [[1987 - Space Quest II - Vohaul's Revenge]]

### Other AGI Games
- [[1986 - The Black Cauldron]]
- [[1984 - Donald Duck's Playground]] - the AGI version dates from 1986 (interpreter 2.001, June 8, 1986)[^ref-8]
- [[1987 - Police Quest - In Pursuit of the Death Angel]]
- [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards]]
- [[1987 - Mixed-Up Mother Goose]]
- [[1988 - Gold Rush]] - December 22, 1988[^ref-8]
- [[1988 - Manhunter - New York]] - August 31, 1988[^ref-8]
- [[1989 - Manhunter - San Francisco]] - Sierra's final AGI title[^ref-1]

### Pre-AGI games
Several earlier games "used some parts of this engine, before it was mature enough": Dragon's Keep (1982), The Gelfling Adventure (1983), Troll's Tale (1983), [[1984 - Mickey's Space Adventure|Mickey's Space Adventure]] (1984) and Winnie the Pooh in the Hundred Acre Wood (1984).[^ref-14] ScummVM's detection tables also label *Mickey's Space Adventure* a "Preagi game".[^ref-15]

## Technical Notes

### Cross-Platform Architecture
AGI was "a scripting engine that made it easier to port previous software to different platforms", which gave *King's Quest* a second life on the Apple II and Tandy 1000 after the PCjr was discontinued.[^ref-16] ScummVM's version list covers AGI releases for DOS (including PCjr and Tandy), Apple II and IIgs, Macintosh, Atari ST, the TRS-80 Color Computer 3 and Amiga.[^ref-8]

### Save/Restore
AGI1 games could only save to a blank floppy disk, though a game could format one from within.[^ref-9]

## Limitations

### Resolution Constraints
The 160×200 logical resolution (each pixel two EGA pixels wide) limited detail in character art and backgrounds.[^ref-6] Artists such as [[Mark Crowe]], who worked on *King's Quest II* and was art director of *The Black Cauldron*, worked within it.[^ref-17]

### Parser Frustrations
The parser only understood words in each game's vocabulary file,[^ref-13] and even its designer wanted a larger one.[^ref-2]

## Transition to SCI

Sierra replaced AGI with SCI, whose first game was *King's Quest IV* (1988).[^ref-1] The first version of SCI still used a text parser, at 320×200 in 16-colour EGA;[^ref-18] it "did not support the impressive but expensive new MCGA and VGA graphics standards".[^ref-19] 256-colour VGA and an icon-driven point-and-click interface came with SCI1 and *King's Quest V* in 1990.[^ref-18]

| Feature | AGI | SCI0 (1988) | SCI1 (1990) |
|---------|-----|-------------|-------------|
| Resolution | 160×200 logical | 320×200 | 320×200 |
| Colours | 16 | 16 (EGA) | 256 (VGA) |
| Interface | Text parser | Text parser | Icon-driven point-and-click |

*King's Quest IV* (1988) shipped in both AGI and SCI versions; the following year Sierra published its final AGI title, *Manhunter 2: San Francisco*, and then used SCI for all new adventure games.[^ref-1]

## Legacy

### Fan Development
The AGI engine has been thoroughly documented by fans:
- **AGI Specifications** — fan-written documentation of AGI's resource and sound formats (the sound chapter by Claudio Matsuoka, Paul Lunga and Ian Schmidt, 1999)[^ref-10]
- **AGI Studio** — Peter Kelly's 1997 tool for viewing, editing and creating AGI games[^ref-9]
- **NAGI** — Nick Sonneveld's New Adventure Game Interpreter[^ref-9]
- **ScummVM** — AGI support since version 0.10.0 (2006)[^ref-14]

### Preservation
ScummVM supports all the Sierra AGI games.[^ref-20]

## Playing AGI Games Today

### Recommended Method
- **ScummVM** — runs every AGI game[^ref-20]
- GOG.com's *King's Quest 1+2+3* and *Space Quest 1+2+3* are "powered by ScummVM"[^ref-21][^ref-22]

### Tips for Modern Players
- Save frequently (Sierra games are unforgiving)
- Keep notes on parser vocabulary that works
- Use walkthrough assistance sparingly

## See Also

- [[Sierra Creative Interpreter]] - AGI's successor engine
- [[Engine History]] - Sierra's full engine lineage
- [[ScummVM]] - Preservation interpreter
- [[King's Quest Series]] - Flagship AGI series
- [[Space Quest Series]] - Sci-fi comedy series
- [[Ken Williams]], [[Jeff Stephenson]] - AGI's authors
- [[Roberta Williams]] - Designer of King's Quest

## References

[^ref-1]: [Wikipedia — Adventure Game Interpreter](https://en.wikipedia.org/wiki/Adventure_Game_Interpreter) — authors Ken Williams and Jeff Stephenson; released May 1984; "employed it in 14 of their games between 1984 and 1989"; "its final AGI-based title, Manhunter 2: San Francisco"
[^ref-2]: [COMPUTE! #57 (February 1985) — "Inside King's Quest", Internet Archive](https://archive.org/stream/1985-02-compute-magazine/Compute_Issue_057_1985_Feb_djvu.txt) — IBM asked Sierra "to create a game that would show off the new computer's color graphics capabilities"; "Eighteen months later"; 80 scenes traced on a Calcomp tablet; "Game Adaptation Language"; "require 128K of memory"; "a larger vocabulary"
[^ref-3]: [Wikipedia — Mystery House](https://en.wikipedia.org/wiki/Mystery_House) — "Mystery House is the first graphical adventure game"
[^ref-4]: [ScummVM Wiki — ADL (Wayback, 2024)](http://web.archive.org/web/2024/https://wiki.scummvm.org/index.php?title=ADL) — "ADL stands for "Adventure Development Language". It was created by Ken Williams"; the Hi-Res Adventure series
[^ref-5]: [Electronic Games, December 1984 — King's Quest review, Internet Archive](https://archive.org/stream/Electronic_Games_Volume_02_Number_17_1984-12_Reese_Communications_US/Electronic_Games_Volume_02_Number_17_1984-12_Reese_Communications_US_djvu.txt) — header "Sierra/IBM/128K Disk"; "a major breakthrough in action-adventure games"
[^ref-6]: [AGI Specifications, ch. 8 — VIEW resources](https://www.agidev.com/articles/agispec/agispecs-8.html) — "AGI pixels are 2 normal EGA pixels wide"; "maximum number of loops… is 255… and the maximum number of cels in each is 255"
[^ref-7]: [AGI Specifications, ch. 3 — variables](https://www.agidev.com/articles/agispec/agispecs-3.html) — "26 - monitor type 0 - CGA; 2 - Hercules; 3 - EGA"
[^ref-8]: [ScummVM Wiki — Sierra Game Versions (Wayback, May 18, 2024)](http://web.archive.org/web/20240518064410/https://wiki.scummvm.org/index.php/Sierra_Game_Versions) — AGI interpreter versions and dates: Donald Duck's Playground 2.001 1986-06-08; King's Quest III 2.272 1986-11-08; King's Quest IV 3.002.086 1988-07-27; Manhunter: New York 1988-08-31; Gold Rush! 1988-12-22; Manhunter 2 1989-08-17
[^ref-9]: [DOS Days — Sierra's AGI](https://dosdays.co.uk/topics/sierra_agi.php) — AGI1 "no dropdown menus… you could only save a game to a blank floppy disk"; AGI2 "around 1986… a dropdown menu bar"; Hercules and MCGA from 2.4xx; "Later versions of AGI2 would also add support for VGA"; AGI Studio; NAGI (undated, unsigned page; used only where noted)
[^ref-10]: [AGI Specifications, ch. 9 — sound](https://www.agidev.com/articles/agispec/agispecs-9.html) — four parts, "one which is the melody, two which are accompaniment, and the final one being noise"; "The IBM PC can only play one note at a time"; Apple IIgs "16 channel wavetable based MIDI songs… and digitally sampled PCM sound effects"
[^ref-11]: [AGI Specifications, ch. 7 — PICTURE resources](https://www.agidev.com/articles/agispec/agispecs-7.html) — priority screen "held in memory and contains control information invisible to the player"; "both screens are updated"
[^ref-12]: [Wikipedia — Space Quest: The Sarien Encounter](https://en.wikipedia.org/wiki/Space_Quest:_The_Sarien_Encounter) — "Tandy 1000, PCjr, and Amiga computers would hear a three-voice soundtrack, while Apple IIGS owners were treated to a fifteen-voice soundtrack"
[^ref-13]: [AGI Specifications, ch. 10 — words.tok](https://www.agidev.com/articles/agispec/agispecs-10.html) — "the dictionary of words that the interpreter understands"; "Many words can have the same word number"
[^ref-14]: [ScummVM Wiki — AGI (Wayback, January 1, 2025)](https://web.archive.org/web/20250101192119/https://wiki.scummvm.org/index.php?title=AGI) — list of 14 Sierra AGI games; PreAGI: Dragon's Keep, The Gelfling Adventure, Troll's Tale, Mickey's Space Adventure, Winnie the Pooh; first release containing it 0.10.0 (2006)
[^ref-15]: [ScummVM — engines/agi/detection_tables.h](https://raw.githubusercontent.com/scummvm/scummvm/master/engines/agi/detection_tables.h) — "Mickey's Space Adventure // Preagi game"
[^ref-16]: [The Strong — King's Quest, World Video Game Hall of Fame](https://www.museumofplay.org/games/kings-quest/) — AGI "a scripting engine that made it easier to port previous software to different platforms"
[^ref-17]: [Wikipedia — Mark Crowe](https://en.wikipedia.org/wiki/Mark_Crowe) — worked on "King's Quest II, before collaborating with Scott Murphy on The Black Cauldron. Crowe was the Art Director for the game"
[^ref-18]: [Wikipedia — Sierra Creative Interpreter](https://en.wikipedia.org/wiki/Sierra_Creative_Interpreter) — SCI0 1988 "320 × 200, 16-color EGA", text parser; SCI1 with King's Quest V in 1990, "256-color VGA graphics with an icon-driven interface"
[^ref-19]: [The Digital Antiquarian — Sierra Gets Creative (August 2016)](https://www.filfre.net/2016/08/sierra-gets-creative/) — "the first version of SCI did not support the impressive but expensive new MCGA and VGA graphics standards"
[^ref-20]: [ScummVM — Compatibility](https://www.scummvm.org/compatibility/) — AGI entries for the Sierra games (agi:kq1 … agi:mh2)
[^ref-21]: [GOG.com — King's Quest 1+2+3](https://www.gog.com/en/game/kings_quest_1_2_3) — "This game is powered by ScummVM"
[^ref-22]: [GOG.com — Space Quest 1+2+3](https://www.gog.com/en/game/space_quest_1_2_3) — "This game is powered by ScummVM"
