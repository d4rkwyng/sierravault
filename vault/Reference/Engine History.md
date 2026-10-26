---
title: "Engine History"
type: reference
last_updated: "2026-10-26"
description: "The technical evolution of Sierra On-Line's game engines from 1980 to 2015 — ADL (Hi-Res Adventures), AGI, SCI0/SCI1/SCI1.1/SCI2/SCI2.1/SCI3, the ThreeSpace-based Mask of Eternity, and the engines used by acquired studios and the 2015 Odd Gentlemen reboot."
tags: [reference, engines, technology, agi, sci, sci32]
---

# Engine History

<small style="color: gray">Last updated: October 26, 2026</small>

## Overview

Sierra On-Line developed and maintained a progression of in-house adventure-game engines between 1980 and 1996 — ADL for the Hi-Res Adventures, AGI, and the Sierra Creative Interpreter (SCI) in its SCI0, SCI1, SCI1.1, SCI2, SCI2.1 and SCI3 versions — plus engines used by acquired and partner studios (Dynamix's 3Space, Impressions' 2D city-builder engine, Coktel's adventure engine and others). This page traces the version history with release-year boundaries, the games that defined each generation, and what each generation added.

For GOG and compilation build numbers, see [[Versions|GOG and compilation version tables (2015 SCG snapshot)]], which transcribes the Sierra Classic Gaming wiki's version tables and cross-checks them against the ScummVM version list.[^ref-20] The `engine:` YAML field on game pages is a quick guide, but where it disagrees with the version list, the version list is the better source.

---

## Generation 1: ADL — Hi-Res Adventures (1980–1983)

**Engine:** ADL ("Adventure Development Language"), created by Ken Williams.[^ref-21]
**Platform:** Apple II family.
**Era:** Pre-AGI.

"ADL stands for 'Adventure Development Language'. It was created by Ken Williams for the first games created by Sierra (then known as On-Line Systems)", and the games using it "were known as the Hi-Res Adventure series" — seven titles numbered #0 to #6.[^ref-21] For *Time Zone*, some 1,400 pencil sketches were traced on Apple's Graphics Tablet with the tools Ken had built for *The Wizard and the Princess*, filled with color, and stored on disk in a highly compressed format; even so, the game grew to twelve disk sides.[^ref-2]

Defining games:

- [[1980 - Hi-Res Adventure 0 - Mission Asteroid|Mission Asteroid]] — numbered #0 but released after Mystery House and The Wizard and the Princess.[^ref-21]
- [[1980 - Hi-Res Adventure 1 - Mystery House|Mystery House]] — Founded the line.
- [[1980 - Hi-Res Adventure 2 - The Wizard and the Princess|The Wizard and the Princess]]
- [[1981 - Hi-Res Adventure 3 - Cranston Manor|Cranston Manor]] and [[1981 - Hi-Res Adventure 4 - Ulysses and the Golden Fleece|Ulysses and the Golden Fleece]]
- [[1982 - Hi-Res Adventure 5 - Time Zone|Time Zone]] — The most ambitious, twelve disk sides.[^ref-2]
- [[1983 - Hi-Res Adventure 6 - The Dark Crystal|The Dark Crystal]] — Final Hi-Res Adventure.

LucasArts' rival engine, SCUMM, came later: it was built at Lucasfilm Games for *Maniac Mansion* (1987).[^ref-25]

## Generation 2: AGI — Adventure Game Interpreter (1984–1989)

**Engine:** [[Adventure Game Interpreter|AGI]], versions AGI0 to AGI3.[^ref-20]
**Platforms:** IBM PC (including PCjr and Tandy), Apple II and IIGS, Macintosh, Atari ST, Amiga, TRS-80 Color Computer.[^ref-5][^ref-20]
**Authors:** Ken Williams and Jeff Stephenson;[^ref-5] Stephenson "had created AGI on IBM's dime and IBM's timetable".[^ref-22]

AGI was developed for [[1984 - King's Quest - Quest for the Crown|King's Quest]] (1984), which Sierra and IBM wanted to use to attract buyers to the IBM PCjr.[^ref-5] King's Quest was "Originally released in 1984 for IBM's ill-fated PCjr".[^ref-3] What it offered:

1. **Animated, color adventures** — AGI "was capable of running animated, color adventure games with music and sound effects".[^ref-5] AGI2.425 briefly introduced script-settable priority bands, which were removed immediately afterwards and returned in 2.936, the last AGI2 version.[^ref-20]
2. **Portable bytecode** — Games were written in a C-like Game Adaptation Language, compiled to bytecode and run by the interpreter.[^ref-5] The Strong museum credits AGI, "a scripting engine that made it easier to port previous software to different platforms", with giving King's Quest a second life after the PCjr.[^ref-3]

Sierra used AGI in 14 games between 1984 and 1989.[^ref-5] ScummVM's version list groups the interpreters as AGI0 (King's Quest on IBM PC, PCjr and Tandy), AGI1 (The Black Cauldron and King's Quest II), AGI2, and AGI3, which begins with King's Quest IV (July 27, 1988) and also ran Manhunter: New York, Gold Rush! and Manhunter 2.[^ref-20]

Defining games:

- [[1984 - King's Quest - Quest for the Crown|King's Quest]] (AGI0)
- [[1985 - King's Quest II - Romancing the Throne|King's Quest II]]
- [[1986 - King's Quest III - To Heir Is Human|King's Quest III]]
- [[1988 - King's Quest IV - The Perils of Rosella|King's Quest IV (AGI version)]] — released in both AGI and SCI versions[^ref-20]
- [[1986 - Space Quest - The Sarien Encounter|Space Quest 1]], [[1987 - Space Quest II - Vohaul's Revenge|Space Quest 2]]
- [[1987 - Police Quest - In Pursuit of the Death Angel|Police Quest 1]]
- [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards|Leisure Suit Larry 1]]
- [[1986 - The Black Cauldron|The Black Cauldron]]
- [[1988 - Manhunter - New York|Manhunter NY]], [[1989 - Manhunter - San Francisco|Manhunter SF]]
- [[1988 - Gold Rush|Gold Rush!]]
- [[1987 - Mixed-Up Mother Goose|Mixed-Up Mother Goose]] (AGI)
- [[1984 - Donald Duck's Playground|Donald Duck's Playground]] (AGI version dated June 8, 1986, interpreter 2.001; ScummVM calls it "more an hybrid between AGI1 & AGI2")[^ref-20]

Not AGI: [[1984 - Mickey's Space Adventure|Mickey's Space Adventure]], [[1983 - Troll's Tale|Troll's Tale]] and [[1984 - Winnie the Pooh in the Hundred Acre Wood|Winnie the Pooh in the Hundred Acre Wood]] are "Pre-AGI" games, which ScummVM's AGI engine detects as a separate type.[^ref-26][^ref-19]

Technical limits: 160×200 resolution,[^ref-5][^ref-22] up to 16 colors on the PCjr's video hardware,[^ref-5] text parser input, room-based scenes.

## Generation 3: SCI0 — Sierra's Creative Interpreter (1988–1990)

**Engine:** [[Sierra Creative Interpreter|SCI0]] (including the bilingual SCI01 variant).[^ref-20]
**Platforms:** IBM PC (including PCjr and Tandy), Macintosh, Atari ST, Amiga, NEC PC-9801.[^ref-20]
**Authors:** Jeff Stephenson and Robert Heitman.[^ref-8]

SCI debuted in September 1988.[^ref-8] It kept AGI's text parser[^ref-8] but doubled the display resolution "from a rather horrid 160 X 200 to a more reasonable (for the era) 320 X 200", with better mouse support and more complex animation; "the first version of SCI did not support the impressive but expensive new MCGA and VGA graphics standards".[^ref-22] The first SCI game was the SCI version of [[1988 - King's Quest IV - The Perils of Rosella|King's Quest IV]].[^ref-20]

Key innovations:

1. **Object-oriented script language** — Stephenson rewrote the scripting language into "a full-fledged modern programming language reminiscent of C++";[^ref-22] he had been influenced by Smalltalk.[^ref-8]
2. **Graphics** — 320×200 in 16-color EGA.[^ref-8][^ref-22]
3. **Sound cards** — Sierra supported the Roland MT-32, Ad Lib and later the Game Blaster. For King's Quest IV, Ken Williams and composer William Goldstein wanted "a full-fledged musical score, arguably the first such ever to be written for a computer game".[^ref-22]

Defining games (SCI0):

- [[1988 - King's Quest IV - The Perils of Rosella|King's Quest IV (SCI version)]]
- [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)|Leisure Suit Larry 2]], [[1989 - Leisure Suit Larry III - Passionate Patti in Pursuit of the Pulsating Pectorals|Leisure Suit Larry III]]
- [[1988 - Police Quest II - The Vengeance|Police Quest II]]
- [[1989 - Space Quest III - The Pirates of Pestulon|Space Quest III]]
- [[1989 - The Colonel's Bequest|The Colonel's Bequest]]
- [[1989 - Quest for Glory I - So You Want to Be a Hero|Quest for Glory I]] (original EGA, first released as Hero's Quest)
- [[1989 - Hoyle Official Book of Games - Volume 1|Hoyle Official Book of Games: Volume 1]]
- [[1990 - Codename - Iceman|Codename: Iceman]], [[1990 - Conquests of Camelot - The Search for the Grail|Conquests of Camelot]]
- [[1990 - Roberta Williams' King's Quest I - Quest for the Crown|King's Quest I SCI remake]] (SCI01, 16-color)[^ref-20]

## Generation 4: SCI1 / SCI1.1 (1990–1993)

**Engine:** SCI1 and SCI1.1. SCI1.1 CD and Windows re-releases continued into 1994, among them the King's Quest VI Windows CD (September 1994) and the Freddy Pharkas CD (September 1994).[^ref-20]
**Platforms:** IBM PC (286 or better), Macintosh, Amiga, FM Towns, NEC PC-9801 — no Atari ST.[^ref-20] Several SCI1.1 games also had Windows releases.[^ref-20]

SCI1's VGA debut was [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest V]] in 1990, which combined 256-color VGA graphics with an icon-driven interface;[^ref-8] Quest for Glory II had already used an earlier, EGA-only SCI1 build (interpreter 1.000.041, against King's Quest V's 1.000.058).[^ref-20] King's Quest V replaced "its predecessor's 16-color EGA graphics with 256-color VGA graphics" and replaced the text parser "with an entirely mouse-driven point-and-click interface".[^ref-23] SCI1 games were sold in both 16-color EGA and 256-color VGA versions.[^ref-20] SCI1.1 (1992) added "enhanced animation and sprite scaling".[^ref-8]

Key innovations:

1. **Point-and-click icon interface** — replaced the text parser, beginning with King's Quest V.[^ref-8][^ref-23]
2. **CD-ROM speech** — For their first foray into CD-ROM, Sierra chose *Mixed-Up Mother Goose*, and "professional actors were hired to voice every line of dialog".[^ref-23] The Mixed-Up Mother Goose CD (July 1991) and the King's Quest V CD (April 1992) both ran on SCI1.[^ref-20]
3. **Windows releases** — SCI1.1 games such as EcoQuest 2 (February 1993) and Hoyle Classic (March 1993) shipped Windows versions.[^ref-20]

Defining games (SCI1):

- [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest V]]
- [[1990 - Quest for Glory II - Trial by Fire|Quest for Glory II]] (an EGA-only SCI1 version)[^ref-20]
- [[1991 - Space Quest IV - Roger Wilco and the Time Rippers|Space Quest IV]]
- [[1991 - Leisure Suit Larry 5 - Passionate Patti Does a Little Undercover Work|Leisure Suit Larry 5]], [[1991 - Police Quest III - The Kindred|Police Quest III]], [[1991 - EcoQuest - The Search for Cetus|EcoQuest 1]], [[1991 - Conquests of the Longbow - The Legend of Robin Hood|Conquests of the Longbow]][^ref-20]
- [[1991 - Mixed-Up Fairy Tales|Mixed-Up Fairy Tales]], [[1991 - Castle of Dr. Brain|Castle of Dr. Brain]][^ref-20]

Defining games (SCI1.1):[^ref-20]

- [[1992 - King's Quest VI - Heir Today, Gone Tomorrow|King's Quest VI]]
- [[1992 - Quest for Glory III - Wages of War|Quest for Glory III]]
- [[1992 - The Dagger of Amon Ra|Dagger of Amon Ra]]
- [[1992 - The Island of Dr. Brain|The Island of Dr. Brain]]
- [[1993 - Space Quest V - The Next Mutation|Space Quest V]]
- [[1993 - Freddy Pharkas - Frontier Pharmacist|Freddy Pharkas]]
- [[1993 - Pepper's Adventures in Time|Pepper's Adventures in Time]]
- [[1993 - Leisure Suit Larry 6 - Shape Up or Slip Out!|Leisure Suit Larry 6]]
- [[1993 - Slater & Charlie Go Camping|Slater & Charlie Go Camping]]

## Generation 5: SCI2 / SCI2.1 (1993–1996)

**Engine:** SCI2 and SCI2.1 ("SCI21").
**Platforms:** 32-bit DOS and Windows; Macintosh.[^ref-8][^ref-20]

SCI2 (1993) brought 640×480 SVGA in 256 colors and 32-bit protected mode.[^ref-8] Its first games were [[1993 - Gabriel Knight - Sins of the Fathers|Gabriel Knight: Sins of the Fathers]] (November 1993), Police Quest IV and Quest for Glory IV.[^ref-20] SCI2.1 followed: "Robot videos were firstly introduced here, in the DOS version of KQ7", and "VMD videos were introduced" in the middle SCI2.1 versions, with "cartoonish or 3D pre-rendered graphics with actors".[^ref-20] Late SCI2.1 builds were still in use in 1996, for the RAMA (April 1996) and Leisure Suit Larry 7 (July 1996) demos.[^ref-20]

Defining games:

- SCI2: [[1993 - Gabriel Knight - Sins of the Fathers|Gabriel Knight: Sins of the Fathers]], [[1993 - Police Quest - Open Season|Police Quest: Open Season]], [[1993 - Quest for Glory IV - Shadows of Darkness|Quest for Glory IV]][^ref-20]
- SCI2.1: [[1994 - King's Quest VII - The Princeless Bride|King's Quest VII: The Princeless Bride]], [[1995 - Phantasmagoria|Phantasmagoria]], [[1995 - Space Quest 6 - Roger Wilco in the Spinal Frontier|Space Quest 6]], [[1995 - The Beast Within - A Gabriel Knight Mystery|The Beast Within: A Gabriel Knight Mystery]], [[1995 - Torin's Passage|Torin's Passage]], [[1995 - Shivers|Shivers]], [[1995 - Police Quest - SWAT|Police Quest: SWAT]][^ref-20]

## Generation 6: SCI3 (1996)

**Engine:** SCI3, the final SCI version. "SCI2, SCI21, and SCI3 can be collectively referred to as SCI32 because the released original interpreters were 32-bit executables."[^ref-20]

SCI3 (1996) added native Windows 95 support;[^ref-8] Wikipedia dates the final interpreter release, version 3.000.000, to November 30, 1996.[^ref-8]

Defining games (SCI3):[^ref-20]

- [[1996 - Leisure Suit Larry 7 - Love for Sail|Leisure Suit Larry: Love for Sail!]]
- [[1996 - Lighthouse - The Dark Being|Lighthouse: The Dark Being]]
- [[1996 - Phantasmagoria - A Puzzle of Flesh|Phantasmagoria: A Puzzle of Flesh]]
- [[1996 - Rama|RAMA]]

Not SCI: [[1997 - Shivers Two - Harvest of Souls|Shivers Two]] "does not contain SCI scripts, the room logic has been rewritten in native code placed in DLL files".[^ref-20][^ref-27] "After 1997, the SCI engine (and pretty much the adventure genre in general) was abandoned"; ScummVM's list puts [[1998 - Quest for Glory V - Dragon Fire|Quest for Glory V]] and [[1999 - Gabriel Knight 3 - Blood of the Sacred, Blood of the Damned|Gabriel Knight 3]] under post-1997 games that are not SCI.[^ref-20] Gabriel Knight 3 used a new engine, the G-Engine.[^ref-40]

## Generation 7: ThreeSpace (Mask of Eternity, 1998)

**Engine:** Dynamix's ThreeSpace (3Space), adapted for an adventure game.

[[1998 - King's Quest - Mask of Eternity|Mask of Eternity]] used "ThreeSpace… the 3D engine that Dynamix, a Sierra subsidiary, contributed to the project". Moving to a fully 3D world "was a decision Williams made even before she completed work on Phantasmagoria". Roberta Williams explained the difficulty: Dynamix used ThreeSpace for its flight simulators, "and the technology was optimized mostly for looking down from way up high".[^ref-24]

Mask of Eternity was not the last King's Quest: [[2015 - King's Quest|King's Quest (2015)]], built on Unreal Engine 3 by The Odd Gentlemen, was published by Activision under the Sierra Entertainment brand.[^ref-39]

## Generation 8: Engines from Acquired and Partner Studios

Sierra's published catalogue also ran on engines developed by acquired or partner studios. These are not "Sierra engines" in the design-lineage sense but matter for compatibility and preservation.

- **Dynamix 3Space** — Damon Slye: "I designed the Dynamix 3Space engine, along with David McClurg. It was used in Stellar 7, Arcticfox, Abrams Battletank, Nova9, A10 Tank Killer, Red Baron, Aces of the Pacific, Aces over Europe… Mechwarrior, MetalTech: EarthSiege, EarthSiege 2, Silent Thunder, Red Baron II & Red Baron 3D."[^ref-28]
- **Dynamix Darkstar** — Starsiege: Tribes (1998) and Starsiege (1999).[^ref-29]
- **Papyrus racing games** — Sierra Chest lists the NASCAR Racing games, IndyCar Racing 2 and Grand Prix Legends under "Unknown/unnamed" engine; no source names a shared Papyrus engine.[^ref-30]
- **Impressions city-builder engine** — *Emperor: Rise of the Middle Kingdom* (2002, BreakAway Games with Impressions) "is the last of the series to use the same 2D-sprite game engine as seen in the earlier titles".[^ref-32] *Caesar IV* (2006) was developed by Tilted Mill Entertainment, not Impressions,[^ref-31] and *Children of the Nile* (2004) was a Tilted Mill game on the Titan 2.0 engine, published by Myelin Media and Sega rather than Sierra.[^ref-33]
- **Coktel adventure engine** — ScummVM's Gob engine runs the Gobliiins games, Goblins Quest 3, Lost in Time and The Bizarre Adventures of Woodruff and the Schnibble;[^ref-19] its detection tables cover Inca II but not the first Inca.[^ref-34]
- **Relic Homeworld engines** — Homeworld 2 (2003) used Lua for levels, AI and game rules; the 2015 remasters of both games are "built on the Homeworld 2 engine".[^ref-41]
- **Valve GoldSrc** — Half-Life (1998), "a heavily modified version of the Quake engine", developed by Valve and published by Sierra Studios.[^ref-38]
- **Monolith LithTech** — No One Lives Forever 2 (2002, LithTech Jupiter, published on Windows by Vivendi Universal Games under the Sierra brand and by Fox Interactive)[^ref-36] and F.E.A.R. (2005, LithTech Jupiter EX, "Released under the Sierra Entertainment brand name").[^ref-37] The first No One Lives Forever (2000, LithTech 2.2) was published on Windows by Fox Interactive; Sierra Entertainment published its PlayStation 2 version.[^ref-35]
- **Unreal Engine 3** — [[2015 - King's Quest|King's Quest (2015)]], developed by The Odd Gentlemen for the Activision-era Sierra revival.[^ref-39]

## Modern Re-Implementations

Modern preservation depends on projects re-implementing these engines:

- **[[ScummVM|ScummVM]]** — Runs the Hi-Res Adventures through its ADL engine (adl:hires0 to hires6), the Pre-AGI games, AGI, and SCI from SCI0 through SCI3 (for example sci:kq7, sci:lsl7, sci:phantasmagoria2, sci:rama).[^ref-19][^ref-21] It lists Shivers Two as not implemented,[^ref-27] and Mask of Eternity, Quest for Glory V and Gabriel Knight 3 do not appear on its compatibility list.[^ref-19]
- **DOSBox** — Generic DOS emulation; runs Sierra titles on the original engine binaries. The fallback when ScummVM doesn't have native support.
- **FreeSCI** — Predecessor to ScummVM's SCI support; FreeSCI's code was merged into ScummVM on February 15, 2009: "FreeSCI code now lives under engines/sci".[^ref-8][^ref-42]

## See Also

- [[Adventure Game Interpreter|AGI engine deep-dive]]
- [[Sierra Creative Interpreter|SCI engine deep-dive]]
- [[ScummVM|ScummVM]] — Modern re-implementation
- [[Versions|GOG and compilation version tables (2015 SCG snapshot)]]
- [[Engine Index]] — Per-game engine list
- [[Timeline 1980-1999|Timeline 1980–1999]] — Engine-launch context
- [[Jeff Stephenson]] — Chief SCI architect

## References

[^ref-2]: [The Digital Antiquarian — Time Zone](https://www.filfre.net/2012/06/time-zone/) — "draw 1400 pictures for the game in pencil"; "traced the pictures on Apple's Graphics Tablet… highly compressed format… tools Ken had originally developed for The Wizard and the Princess"; "twelve disk sides"
[^ref-3]: [The Strong National Museum of Play — King's Quest (World Video Game Hall of Fame)](https://www.museumofplay.org/games/kings-quest/) — "Originally released in 1984 for IBM's ill-fated PCjr"; AGI "a scripting engine that made it easier to port previous software to different platforms"
[^ref-5]: [Wikipedia — Adventure Game Interpreter](https://en.wikipedia.org/wiki/Adventure_Game_Interpreter) — Authors Ken Williams and Jeff Stephenson; developed for King's Quest (1984) for the IBM PCjr; Game Adaptation Language compiled to bytecode; used "in 14 of their games between 1984 and 1989"; 160×200; platforms
[^ref-8]: [Wikipedia — Sierra Creative Interpreter](https://en.wikipedia.org/wiki/Sierra_Creative_Interpreter) — Authors Jeff Stephenson and Robert Heitman; released September 1988; Smalltalk influence; SCI1 with KQ V in 1990; SCI1.1 1992; SCI2 1993 640×480; SCI3 1996 native Windows 95; latest release November 30, 1996; FreeSCI merged 2009
[^ref-19]: [ScummVM Compatibility List](https://www.scummvm.org/compatibility/) — adl:hires0–hires6, agi:mickey, agi:troll, agi:winnie, sci:kq1sci, sci:kq7, sci:lsl7, sci:phantasmagoria2, sci:rama, gob titles; no Mask of Eternity, Quest for Glory V or Gabriel Knight 3 (checked 2026-10-16)
[^ref-20]: [ScummVM Wiki — Sierra Game Versions (Wayback, May 2024)](http://web.archive.org/web/20240518064410/https://wiki.scummvm.org/index.php/Sierra_Game_Versions) — per-game interpreter versions AGI0–AGI3, SCI0–SCI3; platform table; "SCI2, SCI21, and SCI3 can be collectively referred to as SCI32"; Robot and VMD videos; Shivers II "Not SCI"; "After 1997, the SCI engine… was abandoned"
[^ref-21]: [ScummVM Wiki — ADL (Wayback, 2024)](http://web.archive.org/web/2024/https://wiki.scummvm.org/index.php?title=ADL) — "ADL stands for 'Adventure Development Language'. It was created by Ken Williams"; Hi-Res Adventure #0–#6
[^ref-22]: [The Digital Antiquarian — Sierra Gets Creative (2016)](https://www.filfre.net/2016/08/sierra-gets-creative/) — Stephenson "had created AGI on IBM's dime"; 160×200 to 320×200; no MCGA/VGA in the first SCI; language "reminiscent of C++"; MT-32, Ad Lib, Game Blaster; KQ IV score "arguably the first such ever to be written for a computer game"
[^ref-23]: [The Digital Antiquarian — Sierra at the Cusp of the Multimedia Age (2018)](https://www.filfre.net/2018/01/sierra-at-the-cusp-of-the-multimedia-age/) — KQ V's 256-color VGA and point-and-click interface; Mixed-Up Mother Goose as Sierra's "first foray into CD-ROM", "professional actors were hired to voice every line of dialog"
[^ref-24]: [Next Generation #30 (June 1997) — Internet Archive](https://archive.org/details/NextGeneration30Jun1997) — Mask of Eternity feature: "ThreeSpace is the 3D engine that Dynamix, a Sierra subsidiary, contributed to the project"; "optimized mostly for looking down from way up high"
[^ref-25]: [Wikipedia — SCUMM](https://en.wikipedia.org/wiki/SCUMM) — developed by Lucasfilm Games; Maniac Mansion (1987), "the game for which the SCUMM system was originally designed"
[^ref-26]: [ScummVM source — engines/agi/detection_tables.h](https://github.com/scummvm/scummvm/blob/master/engines/agi/detection_tables.h) — Pre-AGI games detected as GType_PreAGI
[^ref-27]: [ScummVM source — engines/sci/detection_tables.h](https://github.com/scummvm/scummvm/blob/master/engines/sci/detection_tables.h) — "Shivers 2 doesn't contain SCI scripts… which classifies Shivers 2 as 'not SCI'"; GAME_NOT_IMPLEMENTED
[^ref-28]: [The Sierra Chest — Engine: 3-Space (Wayback, May 2019)](https://web.archive.org/web/20190512155308/http://sierrachest.com/index.php?a=engines&id=30) — Damon Slye's list of 3Space games
[^ref-29]: [PCGamingWiki — Engine: Darkstar](https://www.pcgamingwiki.com/wiki/Engine:Darkstar) — Starsiege (1999-03-24) and Starsiege: Tribes (1998-12-23), developer Dynamix
[^ref-30]: [The Sierra Chest — Engine: Unknown/unnamed (Wayback, May 2019)](https://web.archive.org/web/20190512153148/http://sierrachest.com/index.php?a=engines&id=15) — lists Nascar Racing titles, IndyCar Racing 2 and Grand Prix Legends
[^ref-31]: [Wikipedia — Caesar IV](https://en.wikipedia.org/wiki/Caesar_IV) — developed by Tilted Mill Entertainment, published by Sierra Entertainment, 2006
[^ref-32]: [Wikipedia — Emperor: Rise of the Middle Kingdom](https://en.wikipedia.org/wiki/Emperor:_Rise_of_the_Middle_Kingdom) — developers BreakAway Games and Impressions Games; "the last of the series to use the same 2D-sprite game engine as seen in the earlier titles"
[^ref-33]: [Wikipedia — Immortal Cities: Children of the Nile](https://en.wikipedia.org/wiki/Immortal_Cities:_Children_of_the_Nile) — developer Tilted Mill Entertainment; publishers Myelin Media (NA), Sega (EU); engine Titan 2.0
[^ref-34]: [ScummVM source — engines/gob/detection](https://github.com/scummvm/scummvm/tree/master/engines/gob/detection) — detection tables include tables_inca2.h; none for the first Inca
[^ref-35]: [Wikipedia — The Operative: No One Lives Forever](https://en.wikipedia.org/wiki/The_Operative:_No_One_Lives_Forever) — Lithtech 2.2; publishers Fox Interactive (Windows), MacPlay (Mac), Sierra Entertainment (PlayStation 2)
[^ref-36]: [Wikipedia — No One Lives Forever 2: A Spy in H.A.R.M.'s Way](https://en.wikipedia.org/wiki/No_One_Lives_Forever_2:_A_Spy_in_H.A.R.M.%27s_Way) — LithTech Jupiter; Windows publishers Vivendi Universal Games ("Released under the Sierra Entertainment brand") and Fox Interactive; 2002
[^ref-37]: [Wikipedia — F.E.A.R. (video game)](https://en.wikipedia.org/wiki/F.E.A.R._(video_game)) — LithTech Jupiter EX; publisher Vivendi Universal Games, "Released under the Sierra Entertainment brand name"; 2005
[^ref-38]: [Wikipedia — Half-Life (video game)](https://en.wikipedia.org/wiki/Half-Life_(video_game)) — engine GoldSrc, "a heavily modified version of the Quake engine"; developer Valve, publisher Sierra Studios
[^ref-39]: [Wikipedia — King's Quest (2015 video game)](https://en.wikipedia.org/wiki/King%27s_Quest_(2015_video_game)) — engine Unreal Engine 3; developed by The Odd Gentlemen and "published by Activision under the Sierra Entertainment brand name"
[^ref-40]: [Jane Jensen — GK3 Designer Diaries #4 (June 1998), Gabriel Knight Pages](http://gkpages.altervista.org/Interviews/DesignerDiaries_04.html) — "GK3 needed this new engine… The G-Engine is a fabulous piece of engineering"
[^ref-41]: [Wikipedia — Homeworld 2](https://en.wikipedia.org/wiki/Homeworld_2) — Lua for levels, AI and a rules engine; remastered versions "both built on the Homeworld 2 engine"
[^ref-42]: [ScummVM News — FreeSCI SCI engine implementation has been merged in (February 15, 2009)](https://www.scummvm.org/news/20090215/) — posted by sev: "FreeSCI code now lives under engines/sci"
