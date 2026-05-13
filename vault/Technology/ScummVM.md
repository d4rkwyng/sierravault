---
title: "ScummVM"
type: technology
last_updated: "2026-05-11"
description: "The cross-platform virtual machine that re-implements LucasArts' SCUMM and Sierra's AGI and SCI engines, enabling modern systems to run nearly the entire Sierra adventure catalog."
tags: [technology, scummvm, agi, sci, preservation, emulation]
---

# ScummVM

<small style="color: gray">Last updated: May 11, 2026</small>

## Overview

ScummVM is the open-source virtual machine that re-implements LucasArts' SCUMM scripting engine and, since 2002, [[Adventure Game Interpreter|Sierra's AGI]] and [[Sierra Creative Interpreter|SCI/SCI32]] engines as well.[^ref-1] Despite its name (originally "Script Creation Utility for Maniac Mansion Virtual Machine"), ScummVM has become the de facto preservation platform for the classic adventure-game era, supporting roughly **350 games across 70+ engines** as of the current 2.9.x release line.[^ref-2]

For the Sierra archive, ScummVM matters for three reasons:

1. **Compatibility.** ScummVM lets modern Windows, macOS, Linux, mobile, and console platforms run all of [[Roberta Williams]]' AGI-era adventures (King's Quest 1–4, Space Quest 1–2, Police Quest 1, Leisure Suit Larry 1, Mystery House, The Black Cauldron, etc.) and the bulk of the SCI-era catalog through *King's Quest VII*.[^ref-3] Without ScummVM, the GOG/Steam re-releases of these games would still rely on DOSBox, which has lower compatibility with Sierra's later SCI titles.
2. **Preservation.** ScummVM's developers reverse-engineer engine internals, document opcode sets and resource formats, and publish their findings openly — a process that has produced the most accurate available documentation of Sierra's proprietary engines.[^ref-4]
3. **Continuity.** Most fan/spiritual-successor projects target the AGS engine rather than building from scratch, but several preservation efforts (particularly the [[2025 - SCP Sierra Conversion Project|SCP Sierra Conversion Project]]) build on top of ScummVM's engine work to ship native versions on legacy platforms like the Amiga.

## History

### Origins (2001–2002)

ScummVM was founded in October 2001 by Ludvig Strigeus and Vincent Hamm to replay LucasArts SCUMM-engine games (*Maniac Mansion*, *Monkey Island*, etc.) on modern systems.[^ref-1] The initial implementation reverse-engineered SCUMM v3-v5 (covering most LucasArts adventures), and within a year the project expanded scope to support other adventure engines.

### Sierra engines added (2002–2010)

- **AGI** support was contributed in 2002 by Stuart George (later "robinwatts") via the AGI Studio project's interpreter foundations. This brought King's Quest 1–4, Space Quest 1–2, Police Quest 1, LSL 1, Mystery House, Mickey's Space Adventure, and other AGI titles into ScummVM.[^ref-5]
- **SCI** support began in 2003 with Lars Skovlund's FreeSCI implementation being merged into ScummVM in 2009.[^ref-6] This eventually covered SCI0 (KQ4 SCI, LSL2, SQ3, PQ2), SCI1 (KQ5, SQ4, LSL5, Mixed-Up Mother Goose SCI), SCI1.1 (KQ6, SQ5, LSL6, EcoQuest 1, Conquests of the Longbow, Christine Conrad games), and SCI2 (KQ7, GK1, Phantasmagoria).[^ref-7]
- **SCI32** support followed for the late-1990s 32-bit Sierra games: *King's Quest VII* CD, *Gabriel Knight 1*, *Phantasmagoria*, *Phantasmagoria: A Puzzle of Flesh*, *Shivers*, *Shivers 2*, *Torin's Passage*, *Lighthouse*, *Police Quest IV*, *Police Quest: SWAT*, etc.[^ref-8]

### Recent improvements (2020–2026)

The 2.5–2.9 release line has steadily refined Sierra engine support. Notable additions:

- **Improved Phantasmagoria support** (2.5, 2022) — Resolved several Sierra "Mac SCI32" rendering issues.[^ref-9]
- **Gabriel Knight 1 enhanced edition support** — Late SCI32 features required for the Anniversary Edition.[^ref-10]
- **Shivers 1+2 native rendering** — Replaced the legacy QuickTime cinematic playback that had broken on modern systems.[^ref-11]
- **2025 Amiga port collaboration** — The [[2025 - SCP Sierra Conversion Project|SCP project]] worked with ScummVM contributors to land AGA-optimized AGI and SCI builds on classic Amiga hardware.[^ref-12]

## Sierra Games Supported

The current ScummVM 2.9 release supports the following Sierra catalog (non-exhaustive):

### AGI-engine titles (pre-1988)
[[1984 - King's Quest - Quest for the Crown|King's Quest 1]], [[1985 - King's Quest II - Romancing the Throne|King's Quest 2]], [[1986 - King's Quest III - To Heir Is Human|King's Quest 3]], [[1988 - King's Quest IV - The Perils of Rosella|King's Quest 4 (AGI)]], [[1986 - Space Quest - The Sarien Encounter|Space Quest 1]], [[1987 - Space Quest II - Vohaul's Revenge|Space Quest 2]], [[1987 - Police Quest - In Pursuit of the Death Angel|Police Quest 1]], [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards|Leisure Suit Larry 1]], [[1986 - The Black Cauldron|The Black Cauldron]], [[1980 - Hi-Res Adventure 1 - Mystery House|Mystery House]] (DOS port), [[1984 - Mickey's Space Adventure|Mickey's Space Adventure]], [[1988 - Manhunter - New York|Manhunter NY]], [[1989 - Manhunter - San Francisco|Manhunter SF]], [[1987 - Mixed-Up Mother Goose|Mixed-Up Mother Goose AGI]], [[1988 - Gold Rush|Gold Rush!]]

### SCI0–SCI1.1 titles (1988–1993)
[[1988 - King's Quest IV - The Perils of Rosella|King's Quest 4 (SCI)]], [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest 5]], [[1989 - Space Quest III - The Pirates of Pestulon|Space Quest 3]], [[1991 - Space Quest IV - Roger Wilco and the Time Rippers|Space Quest 4]], [[1988 - Police Quest II - The Vengeance|Police Quest 2]], [[1991 - Police Quest III - The Kindred|Police Quest 3]], [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)|LSL 2]], [[1989 - Leisure Suit Larry III - Passionate Patti in Pursuit of the Pulsating Pectorals|LSL 3]], [[1989 - Quest for Glory I - So You Want to Be a Hero|Quest for Glory 1 (EGA & VGA)]], [[1990 - Quest for Glory II - Trial by Fire|Quest for Glory 2]], [[1989 - The Colonel's Bequest|Colonel's Bequest]], [[1992 - The Dagger of Amon Ra|Dagger of Amon Ra]], [[1991 - Conquests of the Longbow - The Legend of Robin Hood|Conquests of the Longbow]], [[1991 - EcoQuest - The Search for Cetus|EcoQuest 1]], [[1992 - King's Quest VI - Heir Today, Gone Tomorrow|King's Quest 6]], [[1993 - Space Quest V - The Next Mutation|Space Quest 5]], [[1991 - Leisure Suit Larry 5 - Passionate Patti Does a Little Undercover Work|LSL 5]]

### SCI2/SCI32 titles (1994–1998)
[[1994 - King's Quest VII - The Princeless Bride|King's Quest 7]], [[1993 - Gabriel Knight - Sins of the Fathers|Gabriel Knight 1]], [[1995 - The Beast Within - A Gabriel Knight Mystery|Gabriel Knight 2]], [[1995 - Phantasmagoria|Phantasmagoria]], [[1996 - Phantasmagoria - A Puzzle of Flesh|Phantasmagoria 2]], [[1995 - Shivers|Shivers]], [[1997 - Shivers Two - Harvest of Souls|Shivers 2]], [[1995 - Torin's Passage|Torin's Passage]], [[1996 - Lighthouse - The Dark Being|Lighthouse: The Dark Being]], [[1993 - Police Quest - Open Season|Police Quest 4]], [[1995 - Police Quest - SWAT|Police Quest: SWAT]], [[1998 - Quest for Glory V - Dragon Fire|Quest for Glory 5]], [[1993 - Freddy Pharkas - Frontier Pharmacist|Freddy Pharkas]], [[1993 - Pepper's Adventures in Time|Pepper's Adventures in Time]]

### Currently unsupported
- **[[1998 - King's Quest - Mask of Eternity|King's Quest: Mask of Eternity]]** — Uses Sierra's 3D engine (modified 3Space), not SCI; runs natively or via Windows compatibility shims.
- **[[1998 - Caesar III|Caesar III]]** and the Impressions city-builder trilogy — Custom non-SCI engines.
- **Dynamix and Papyrus titles** — Non-SCI engines (3Space, NASCAR Racing engines).
- **[[1999 - Homeworld|Homeworld]]** and other Relic-era titles — Custom engines.
- **[[2015 - King's Quest|King's Quest (2015)]]** — Unreal Engine, runs natively.

## How ScummVM Works (Sierra context)

ScummVM re-implements each adventure-game engine at the script-interpreter level. For a Sierra SCI game, the workflow is:

1. **Asset extraction** — The original game's resource files (`RESOURCE.000`, `RESOURCE.MAP`, `*.SCR`, `VOCAB.*`, `*.PIC`, `*.VEW`) are loaded directly from the user's installation.
2. **Engine selection** — ScummVM detects the SCI version (0/1/1.1/2/2.1/3) from the resource format.
3. **Script interpretation** — The SCI bytecode in the resource files is executed by ScummVM's own SCI interpreter, which re-implements every opcode documented by the FreeSCI/ScummVM SCI projects.[^ref-13]
4. **Graphics, audio, input** — Sierra's original VGA/SVGA framebuffers, Adlib/Roland MT-32/General MIDI audio, and parser/mouse input are abstracted onto the host platform's SDL-based output layer.

This architecture means ScummVM can fix engine bugs and add modern features (high-DPI rendering, save-state ports across platforms, controller support, audio mixing) without modifying the original game files — the original game data remains untouched and runs in its original form, just on a reimplemented host VM.[^ref-14]

## Acquisition and Use

- **GOG.com re-releases** of Sierra adventure titles ship with ScummVM bundled for the post-AGI engine games (or DOSBox for AGI titles where the AGI compatibility was historically less battle-tested).[^ref-15]
- **Steam re-releases** likewise rely on ScummVM for SCI-engine titles in many cases.[^ref-16]
- **Standalone use** — ScummVM is free and open-source (GPL-licensed), and users who own original Sierra disks can copy the game assets and run them in ScummVM directly on Windows, macOS, Linux, iOS, Android, Nintendo Switch, PlayStation Vita, and dozens of other supported platforms.[^ref-2][^ref-17]

## Recent Releases

| Version | Date | Sierra-relevant additions |
|---------|------|---------------------------|
| 2.5.0 | Oct 2021 | Improved SCI32 Mac support; Phantasmagoria refinements |
| 2.6.0 | Aug 2022 | Lighthouse improvements; Gabriel Knight 2 polish |
| 2.7.0 | Mar 2023 | Shivers 2 native cinematic playback |
| 2.8.0 | Dec 2023 | KQ7 ID-display fixes; SCI32 stability |
| 2.9.0 | Nov 2025 | Amiga AGA-optimized AGI/SCI builds (SCP collaboration) |

## Legacy

ScummVM is the single most important piece of preservation infrastructure for the Sierra catalog. Without it, the AGI- and SCI-era adventure games would by now be unrunnable on any modern operating system in their original form — the same fate that has befallen [[1998 - King's Quest - Mask of Eternity|Mask of Eternity]], whose unique 3Space engine is supported by neither ScummVM nor DOSBox and which suffers significant compatibility issues on Windows 10/11.[^ref-18]

The project's open-source nature has also made it a center of gravity for the broader fan-preservation community: documentation of SCI internals first emerged in the FreeSCI project, then was systematized by ScummVM contributors, and now serves as the technical foundation for both the Sierra Help patches and most modern fan-game tooling (including SCI Companion and the AGI-Studio derivatives).[^ref-19]

## See Also

- [[Adventure Game Interpreter]] — Sierra's pre-SCI engine (1984–1988)
- [[Sierra Creative Interpreter]] — The SCI/SCI32 engine family (1988–1998)
- [[Reference/Versions]] — Per-title interpreter version data
- [[2025 - SCP Sierra Conversion Project]] — Amiga ports using ScummVM-derived engine code

## References

[^ref-1]: [Wikipedia — ScummVM](https://en.wikipedia.org/wiki/ScummVM) — Project history, founding, scope
[^ref-2]: [ScummVM Compatibility List](https://www.scummvm.org/compatibility/) — Official supported-games and platforms list
[^ref-3]: [ScummVM Sierra games](https://wiki.scummvm.org/index.php?title=Category:Sierra_Online_games) — Sierra-specific supported titles
[^ref-4]: [ScummVM Wiki — SCI Technical Documentation](https://wiki.scummvm.org/index.php?title=SCI/Specifications) — Reverse-engineered engine documentation
[^ref-5]: [ScummVM Wiki — AGI](https://wiki.scummvm.org/index.php?title=AGI) — AGI engine support, contributors
[^ref-6]: [Wikipedia — FreeSCI](https://en.wikipedia.org/wiki/FreeSCI) — Predecessor project, ScummVM merger history
[^ref-7]: [ScummVM Wiki — SCI](https://wiki.scummvm.org/index.php?title=SCI) — SCI engine support overview
[^ref-8]: [ScummVM Wiki — SCI32](https://wiki.scummvm.org/index.php?title=SCI32) — SCI32 engine support
[^ref-9]: [ScummVM 2.5 release notes](https://www.scummvm.org/news/20211011/) — Phantasmagoria refinements
[^ref-10]: [ScummVM 2.7 release notes](https://www.scummvm.org/news/20230322/) — GK1 enhanced edition
[^ref-11]: [ScummVM 2.7 release notes](https://www.scummvm.org/news/20230322/) — Shivers QuickTime replacement
[^ref-12]: [SCP Project announcement](https://github.com/SCPProject/scummvm) — Amiga ScummVM collaboration
[^ref-13]: [ScummVM source code — SCI engine](https://github.com/scummvm/scummvm/tree/master/engines/sci) — Reference implementation
[^ref-14]: [ScummVM Wiki — How ScummVM works](https://wiki.scummvm.org/index.php?title=How_to_play) — User-facing architecture overview
[^ref-15]: [GOG.com — Sierra catalog](https://www.gog.com/en/games?developers=sierra-on-line) — Bundled ScummVM/DOSBox configurations
[^ref-16]: [Steam — Sierra catalog](https://store.steampowered.com/developer/Sierra) — Re-release platform notes
[^ref-17]: [ScummVM Downloads](https://www.scummvm.org/downloads/) — Official platform builds
[^ref-18]: [PCGamingWiki — King's Quest: Mask of Eternity](https://www.pcgamingwiki.com/wiki/King%27s_Quest:_Mask_of_Eternity) — Modern compatibility issues
[^ref-19]: [Sierra Help Wiki — ScummVM patches](https://wiki.sierrahelp.com/index.php/ScummVM_Patches) — Fan patch ecosystem
