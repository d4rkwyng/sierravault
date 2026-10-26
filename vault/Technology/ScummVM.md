---
title: "ScummVM"
type: technology
last_updated: "2026-10-26"
description: "The open-source program that re-implements LucasArts' SCUMM and Sierra's AGI and SCI engines, letting modern systems run most of the classic Sierra adventure catalogue."
tags: [technology, scummvm, agi, sci, preservation, emulation]
---

# ScummVM

<small style="color: gray">Last updated: October 26, 2026</small>

## Overview

ScummVM is the open-source program that re-implements LucasArts' SCUMM scripting engine and, since 2006–2010, [[Adventure Game Interpreter|Sierra's AGI]] (from 2006, via the Sarien project) and [[Sierra Creative Interpreter|SCI]] (merged 2009, first released 2010, via FreeSCI) engines as well.[^ref-1][^ref-5][^ref-7] Despite its name ("Script Creation Utility for Maniac Mansion Virtual Machine"), it "is a complete rewrite of these games' executables and is not an emulator"; its home page says it supports "over 325 adventure games".[^ref-23] The January 2026 "Like a version" release alone added 12 engines and, counting its detection tables, "at least 194 titles".[^ref-20]

For the Sierra archive, ScummVM matters for three reasons:

1. **Compatibility.** ScummVM lets modern Windows, macOS, Linux, mobile, and console platforms run Sierra's AGI-era adventures (King's Quest 1–4, Space Quest 1–2, Police Quest 1, Leisure Suit Larry 1, The Black Cauldron, etc.) and most of the SCI catalogue, including the SCI32 games such as *King's Quest VII*, *Gabriel Knight*, *Phantasmagoria* and *Space Quest 6*.[^ref-2][^ref-24] GOG's re-releases of several of these games now ship with ScummVM rather than DOSBox.[^ref-15]
2. **Preservation.** ScummVM's developers reverse-engineer engine internals and publish their findings openly; the ScummVM wiki hosts SCI technical specifications that began in the FreeSCI project.[^ref-4]
3. **Breadth.** Beyond Sierra's own engines, ScummVM also runs the Dynamix DGDS adventures and Coktel Vision's Gob-engine games.[^ref-2]

## History

### Origins (2001–2002)

Work on ScummVM started in September 2001, when computer science student Ludvig Strigeus set out to play LucasArts SCUMM games such as *Monkey Island 2* on Linux; Vincent Hamm, working on a similar player, joined him.[^ref-1] ScummVM's own 20th-anniversary post dates "the initial revision of the ScummVM code" to October 9, 2001.[^ref-9]

### Sierra engines added (2006–2020)

- **AGI** — "AGI support was added in 2006 by incorporating efforts from the Sarien project."[^ref-1] The ScummVM wiki lists the engine's developers as the "Sarien Team, stu, dsymonds, sev, aquadran, md5, Buddha^, m_kiewitz".[^ref-5] The engine first shipped in the June 20, 2007 release, whose notes read "Added Sierra AGI engine."[^ref-24]
- **SCI** — The FreeSCI code was merged into ScummVM in February 2009 ("FreeSCI code now lives under engines/sci").[^ref-6] The wiki lists the date added as 2009-02-14, with six engine developers (fingolfin, lskovlun, m_kiewitz, md5, waltervn, wjp).[^ref-7] SCI0–SCI1.1 games were first officially supported in 1.2.0, the "FaSCInating release" of October 15, 2010.[^ref-24]
- **SCI2–SCI3** — ScummVM 2.0 (December 17, 2017) added "almost all of the 32-bit Sierra adventures", including Gabriel Knight 1 and 2, King's Quest VII, Leisure Suit Larry 6 (hi-res) and 7, Lighthouse, Phantasmagoria 1 and 2, Police Quest 4, Shivers, Space Quest 6 and Torin's Passage.[^ref-8] Police Quest: SWAT followed in 2.2.0 (2020).[^ref-24]

### Refinements in the 2.x line (2021–2024)

The 2.5–2.9 releases continued to refine Sierra support. From ScummVM's release notes:[^ref-24]

- **2.5.0** (October 9, 2021) — Support for the Macintosh version of Gabriel Knight 1 and the CD-Audio version of Mixed-Up Mother Goose; an RGB rendering mode for SCI0–SCI1.1 games.
- **2.6.0** (August 1, 2022) — Text-to-speech in SCI floppy games; fixes for Shivers and Phantasmagoria 2 autosaves.
- **2.7.0** (February 26, 2023)[^ref-10] — Support for Casio MIDI devices in SCI0 games.
- **2.9.0** (December 22, 2024) — Added *Rise of the Dragon* (the first Dynamix DGDS game) and "an impressive speech repair feature for Gabriel Knight 1 CD".[^ref-11]

### Year-based quarterly releases (2026– )

From 2026.1.0, ScummVM switched from 2.x version numbers to year-based releases on a more frequent cadence:[^ref-20]

- **2026.1.0 "Like a version"** (January 31, 2026) — 12 new engines and at least 194 titles, including Dynamix's [[1991 - Heart of China|Heart of China]] and [[1991 - The Adventures of Willy Beamish|The Adventures of Willy Beamish]].[^ref-20]
- **2026.2.0 "Railmonicon"** (March 28, 2026)[^ref-21] — Improved PC-Speaker emulation, and fewer screen blits in the Gob engine, "making Gobliiins and Ween noticeably more responsive on weaker platforms".[^ref-24]
- **2026.3.0 "Carousels & Killer Whales"** (June 20, 2026) — No Sierra-specific changes listed.[^ref-22]
- **2026.4.0 "Never-slop"** (October 11, 2026, the project's 25th anniversary) — No Sierra-specific changes found in its announcement or release notes.[^ref-12][^ref-24]

## Sierra Games Supported

The current ScummVM compatibility list includes the following Sierra catalogue (non-exhaustive):[^ref-2]

### AGI-engine titles (1984–1989)
[[1984 - King's Quest - Quest for the Crown|King's Quest 1]], [[1985 - King's Quest II - Romancing the Throne|King's Quest 2]], [[1986 - King's Quest III - To Heir Is Human|King's Quest 3]], [[1988 - King's Quest IV - The Perils of Rosella|King's Quest 4 (AGI)]], [[1986 - Space Quest - The Sarien Encounter|Space Quest 1]], [[1987 - Space Quest II - Vohaul's Revenge|Space Quest 2]], [[1987 - Police Quest - In Pursuit of the Death Angel|Police Quest 1]], [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards|Leisure Suit Larry 1]], [[1986 - The Black Cauldron|The Black Cauldron]], [[1984 - Mickey's Space Adventure|Mickey's Space Adventure]], [[1984 - Winnie the Pooh in the Hundred Acre Wood|Winnie the Pooh in the Hundred Acre Wood]], Troll's Tale, Donald Duck's Playground, [[1988 - Manhunter - New York|Manhunter NY]], [[1989 - Manhunter - San Francisco|Manhunter SF]], [[1987 - Mixed-Up Mother Goose|Mixed-Up Mother Goose AGI]], [[1988 - Gold Rush|Gold Rush!]]

### Apple II Hi-Res Adventures (ADL engine)
[[1980 - Hi-Res Adventure 1 - Mystery House|Mystery House]] and Hi-Res Adventures #0–#6 run through ScummVM's separate ADL engine (`adl:hires1` for Mystery House), not AGI.[^ref-2]

### SCI0–SCI1.1 titles (1988–1993)
[[1988 - King's Quest IV - The Perils of Rosella|King's Quest 4 (SCI)]], [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest 5]], [[1992 - King's Quest VI - Heir Today, Gone Tomorrow|King's Quest 6]], King's Quest 1 (SCI remake), [[1989 - Space Quest III - The Pirates of Pestulon|Space Quest 3]], [[1991 - Space Quest IV - Roger Wilco and the Time Rippers|Space Quest 4]], [[1993 - Space Quest V - The Next Mutation|Space Quest 5]], Space Quest 1 (SCI remake), [[1988 - Police Quest II - The Vengeance|Police Quest 2]], [[1991 - Police Quest III - The Kindred|Police Quest 3]], Police Quest 1 (SCI remake), [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)|LSL 2]], [[1989 - Leisure Suit Larry III - Passionate Patti in Pursuit of the Pulsating Pectorals|LSL 3]], [[1991 - Leisure Suit Larry 5 - Passionate Patti Does a Little Undercover Work|LSL 5]], [[1993 - Leisure Suit Larry 6 - Shape Up or Slip Out!|LSL 6]], LSL 1 (SCI remake), [[1989 - Quest for Glory I - So You Want to Be a Hero|Quest for Glory 1 (EGA & VGA)]], [[1990 - Quest for Glory II - Trial by Fire|Quest for Glory 2]], [[1992 - Quest for Glory III - Wages of War|Quest for Glory 3]], [[1993 - Quest for Glory IV - Shadows of Darkness|Quest for Glory 4]], [[1989 - The Colonel's Bequest|Colonel's Bequest]], [[1992 - The Dagger of Amon Ra|Dagger of Amon Ra]], [[1990 - Conquests of Camelot - The Search for the Grail|Conquests of Camelot]], [[1991 - Conquests of the Longbow - The Legend of Robin Hood|Conquests of the Longbow]], [[1991 - EcoQuest - The Search for Cetus|EcoQuest 1]], EcoQuest 2, [[1990 - Codename - Iceman|Codename: Iceman]], [[1993 - Freddy Pharkas - Frontier Pharmacist|Freddy Pharkas]], [[1993 - Pepper's Adventures in Time|Pepper's Adventures in Time]], Castle and Island of Dr. Brain, Hoyle 1–5, Jones in the Fast Lane, Mixed Up Fairy Tales

### SCI2/SCI32 titles (1993–1996)
[[1994 - King's Quest VII - The Princeless Bride|King's Quest 7]], [[1993 - Gabriel Knight - Sins of the Fathers|Gabriel Knight 1]], [[1995 - The Beast Within - A Gabriel Knight Mystery|Gabriel Knight 2]], [[1995 - Phantasmagoria|Phantasmagoria]], [[1996 - Phantasmagoria - A Puzzle of Flesh|Phantasmagoria 2]], [[1995 - Shivers|Shivers]], [[1995 - Torin's Passage|Torin's Passage]], [[1996 - Lighthouse - The Dark Being|Lighthouse: The Dark Being]], [[1993 - Police Quest - Open Season|Police Quest 4]], [[1995 - Police Quest - SWAT|Police Quest: SWAT]], [[1995 - Space Quest 6 - Roger Wilco in the Spinal Frontier|Space Quest 6]], [[1996 - Leisure Suit Larry 7 - Love for Sail|LSL 7]], RAMA, King's Questions

### Dynamix DGDS titles (2024–2026)
[[1990 - Rise of the Dragon|Rise of the Dragon]] (added in 2.9.0), [[1991 - Heart of China|Heart of China]] and [[1991 - The Adventures of Willy Beamish|The Adventures of Willy Beamish]] (added in 2026.1.0); the compatibility list rates all three "Good".[^ref-11][^ref-20][^ref-2]

### Currently unsupported
- **[[1997 - Shivers Two - Harvest of Souls|Shivers Two: Harvest of Souls]]** — ScummVM's SCI detection tables note that "Shivers 2 doesn't contain SCI scripts"; its room logic lives in native DLL code, so it cannot be supported without rewriting that logic.[^ref-13]
- **[[1998 - Quest for Glory V - Dragon Fire|Quest for Glory V]]** — A 3D game not on the ScummVM compatibility list.[^ref-2]
- **[[1998 - King's Quest - Mask of Eternity|King's Quest: Mask of Eternity]]** — A 3D game, not SCI; community fix projects exist to run it on Windows 10 and 11.[^ref-18]
- **[[1998 - Caesar III|Caesar III]]** and the Impressions city-builder trilogy — Custom non-SCI engines.
- **Remaining Dynamix and Papyrus titles** — Simulation engines outside ScummVM's scope.
- **[[1999 - Homeworld|Homeworld]]** and other Relic-era titles — Custom engines.
- **[[2015 - King's Quest|King's Quest (2015)]]** — Unreal Engine, runs natively.

## How ScummVM Works (Sierra context)

ScummVM re-implements each adventure-game engine at the script-interpreter level. For a Sierra SCI game, the workflow is:

1. **Asset loading** — The original game's resource files (`RESOURCE.000`, `RESOURCE.MAP`, etc.) are loaded directly from the user's installation.
2. **Engine selection** — ScummVM detects the game and its SCI version from its detection tables.[^ref-13]
3. **Script interpretation** — The SCI bytecode in the resource files is executed by ScummVM's own SCI interpreter.[^ref-13]
4. **Graphics, audio, input** — Sierra's original graphics, AdLib/Roland MT-32/General MIDI audio, and parser/mouse input are mapped onto each host platform's backend.

This architecture means ScummVM can fix engine bugs and add modern features (for example the 2.5.0 RGB rendering mode and 2.6.0 text-to-speech) without modifying the original game files.[^ref-24]

## Acquisition and Use

- **GOG.com re-releases** of Sierra adventures increasingly ship with ScummVM, including AGI titles: GOG's Space Quest 1+2+3 replaced DOSBox with ScummVM 2.0 in 2018 and was updated to ScummVM 2026.1.0 in February 2026; PCGamingWiki lists the GOG King's Quest as pre-packaged with ScummVM.[^ref-15][^ref-14]
- **Standalone use** — ScummVM is free and open-source (GPL-3.0-or-later), and users who own original Sierra disks can copy the game assets and run them directly. Official packages include Windows, macOS, Linux, iOS, Android, Nintendo Switch and PlayStation Vita, among others.[^ref-1][^ref-17]

## Legacy

ScummVM is one of the most important pieces of preservation infrastructure for the Sierra catalogue: it lets the AGI- and SCI-era adventure games run natively on current operating systems from their original data files. Games outside its scope, such as [[1998 - King's Quest - Mask of Eternity|Mask of Eternity]], depend instead on community fix projects to run on Windows 10 and 11.[^ref-18]

The project's open-source nature has also made it a centre of gravity for the broader fan-preservation community: documentation of SCI internals first emerged in the FreeSCI project and is now hosted on the ScummVM wiki.[^ref-4]

## See Also

- [[Adventure Game Interpreter]] — Sierra's pre-SCI engine (1984–1989)
- [[Sierra Creative Interpreter]] — The SCI/SCI32 engine family
- [[Versions|GOG and compilation version tables (2015 SCG snapshot)]]
- [[2025 - SCP Sierra Conversion Project]] — Amiga conversions that run on Sierra's own Amiga executables

## References

[^ref-1]: [Wikipedia — ScummVM](https://en.wikipedia.org/wiki/ScummVM) — Work began September 2001 (Strigeus, Hamm); "AGI support was added in 2006 by incorporating efforts from the Sarien project"; GPL-3.0-or-later
[^ref-2]: [ScummVM Compatibility List](https://www.scummvm.org/compatibility/) — Supported games and ratings, incl. `adl:hires1` Mystery House; DGDS games rated "Good"; no QFG5 or Shivers 2 entry (checked 2026-10-16)
[^ref-4]: [ScummVM Wiki — SCI Specifications](https://wiki.scummvm.org/index.php?title=SCI/Specifications) — Reverse-engineered SCI documentation from the FreeSCI project
[^ref-5]: [ScummVM Wiki — AGI](https://wiki.scummvm.org/index.php?title=AGI) — Engine developers "Sarien Team, stu, dsymonds, sev, aquadran, md5, Buddha^, m_kiewitz"
[^ref-6]: [ScummVM News — FreeSCI merged (February 15, 2009)](https://www.scummvm.org/news/20090215/) — "FreeSCI code now lives under engines/sci"
[^ref-7]: [ScummVM Wiki — SCI](https://wiki.scummvm.org/index.php?title=SCI) — Date added 2009-02-14; first release 1.2.0; developers fingolfin, lskovlun, m_kiewitz, md5, waltervn, wjp
[^ref-8]: [ScummVM News — ScummVM 2.0 (December 17, 2017)](https://www.scummvm.org/news/20171217/) — "almost all of the 32-bit Sierra adventures"
[^ref-9]: [ScummVM News — Twenty years ago today (October 9, 2021)](https://www.scummvm.org/news/20211009/) — "on Tue Oct 9 16:30:12 2001, Ludvig Strigeus pushed the initial revision"; 2.5.0 release, Gabriel Knight 1 Macintosh
[^ref-10]: [ScummVM News — 2.7.0 (February 26, 2023)](https://www.scummvm.org/news/20230226/) — 2.7.0 release announcement
[^ref-11]: [ScummVM News — 2.9.0 (December 22, 2024)](https://www.scummvm.org/news/20241222/) — New games include Rise of the Dragon; "speech repair feature for Gabriel Knight 1 CD"
[^ref-12]: [ScummVM News — 2026.4.0 "Never-slop" (October 11, 2026)](https://www.scummvm.org/news/20261011/) — 25th-anniversary release
[^ref-13]: [ScummVM source — SCI detection tables](https://github.com/scummvm/scummvm/blob/master/engines/sci/detection_tables.h) — "Shivers 2 doesn't contain SCI scripts"; SCI game detection
[^ref-14]: [PCGamingWiki — King's Quest](https://www.pcgamingwiki.com/wiki/King%27s_Quest) — GOG version pre-packaged with ScummVM
[^ref-15]: [GOG.com — Space Quest 1+2+3](https://www.gog.com/en/game/space_quest_1_2_3) — "This game is powered by ScummVM"; changelog: "Replaced DOSBox with ScummVM 2.0" (2018), "Updated ScummVM to version 2026.1.0" (February 20, 2026)
[^ref-17]: [ScummVM Downloads](https://www.scummvm.org/downloads/) — Official platform packages incl. Nintendo Switch, PlayStation Vita
[^ref-18]: [PCGamingWiki — King's Quest: Mask of Eternity](https://www.pcgamingwiki.com/wiki/King%27s_Quest:_Mask_of_Eternity) — Windows 10/11 fix projects (kqmoefix, KQ8FixWin11)
[^ref-20]: [ScummVM 2026.1.0 "Like a version" release announcement](https://www.scummvm.org/news/20260131/) — 12 new engines, "at least 194 titles"; Heart of China and Willy Beamish
[^ref-21]: [ScummVM 2026.2.0 "Railmonicon" release announcement](https://www.scummvm.org/news/20260328/) — 2026.2.0 release
[^ref-22]: [ScummVM 2026.3.0 "Carousels & Killer Whales" release announcement](https://www.scummvm.org/news/20260620/) — Quarterly release, no Sierra changes
[^ref-23]: [ScummVM home page](https://www.scummvm.org/) — "a complete rewrite of these games' executables and is not an emulator"; "over 325 adventure games"
[^ref-24]: [ScummVM NEWS.md](https://github.com/scummvm/scummvm/blob/master/NEWS.md) — Per-release notes: "Added Sierra AGI engine" (2007-06-20); 1.2.0 SCI0–SCI1.1 (2010-10-15); 2.0.0 SCI2–SCI3; 2.2.0 PQ: SWAT; 2.5.0–2.9.0 SCI items; 2026.2.0 PC-Speaker and Gob blits
