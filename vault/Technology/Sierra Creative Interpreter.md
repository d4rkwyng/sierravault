---
title: "Sierra Creative Interpreter (SCI)"
type: technology
developer: "Sierra On-Line"
years_active: "1988-1996"
last_updated: "2026-10-26"
---

# Sierra Creative Interpreter (SCI)

<small style="color: gray">Last updated: October 26, 2026</small>

## Overview

The Sierra Creative Interpreter (SCI) was Sierra On-Line's game engine for its adventure games from 1988 through 1996. Written originally by [[Jeff Stephenson]] and [[Bob Heitman|Robert Heitman]], it debuted in September 1988 with *King's Quest IV* and replaced the [[Adventure Game Interpreter|AGI]]; its final interpreter, version 3.000.000, dates from November 1996.[^ref-1] Over its life SCI moved Sierra's games from 16-color EGA to 256-color VGA and 640×480 SVGA, from the text parser to point-and-click icons, and from floppy disks to CD-ROM speech and full-motion video.[^ref-1][^ref-2]

SCI evolved through several major versions. It powered nearly every major Sierra adventure franchise during those years, including King's Quest, Space Quest, Quest for Glory, Police Quest, Gabriel Knight, and Leisure Suit Larry.[^ref-1]

## Version History

| Version | Years | Resolution | Key Features |
|---------|-------|------------|--------------|
| SCI0 / SCI01 | 1988–1990 | 320×200 (16-color EGA) | Text parser with mouse support |
| SCI1 | 1990–1992 | 320×200 (16-color EGA and 256-color VGA versions) | Icon-based point-and-click interface |
| SCI1.1 | 1992–1993 | 320×200 (256 colors) | Enhanced animation, sprite scaling |
| SCI2 | 1993 | 640×480 (256 colors) | 32-bit protected mode |
| SCI2.1 | 1994–1996 | 640×480 (256 colors) | Robot and VMD video |
| SCI3 | 1996 | 640×480 (256 colors) | Native Windows 95 support |

Sources: Wikipedia's version table and the ScummVM wiki's interpreter-version lists, whose dated builds show each version's span.[^ref-1][^ref-2] SCI2, SCI2.1 and SCI3 "can be collectively referred to as SCI32 because the released original interpreters were 32-bit executables."[^ref-2]

## SCI0 (1988–1990)

The first SCI version doubled AGI's display resolution, "from a rather horrid 160 X 200 to a more reasonable (for the era) 320 X 200", and improved mouse support and animation.[^ref-3]

### Technical Specifications
| Specification | Details |
|---------------|---------|
| Resolution | 320×200 pixels |
| Color Depth | 16 colors (EGA); SCI0 "did not support the impressive but expensive new MCGA and VGA graphics standards"[^ref-3] |
| Interface | Text parser with mouse support |
| Audio | PC Speaker, AdLib, Game Blaster, Roland MT-32[^ref-3] |

### Audio Revolution
SCI0 brought composed scores to Sierra's games through Roland MT-32 support; King's Quest IV's score was written for it.[^ref-3] A period Sierra mail-order flyer described the module this way: "The MT-32 is actually eight individual synthesizers and a percussion sound module."[^ref-6] See [[Audio and Music Tech]] for the full story.

[[1989 - Space Quest III - The Pirates of Pestulon|Space Quest III]] (1989) was "one of the first games to support the new Sound Blaster sound card".[^ref-7]

### Notable SCI0 Games
- [[1988 - King's Quest IV - The Perils of Rosella]] — The first SCI game[^ref-1]
- [[1988 - Police Quest II - The Vengeance]]
- [[1989 - Space Quest III - The Pirates of Pestulon]] — One of the first Sound Blaster games[^ref-7]
- [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)]]
- [[1989 - Leisure Suit Larry III - Passionate Patti in Pursuit of the Pulsating Pectorals]]
- [[1989 - Quest for Glory I - So You Want to Be a Hero]] (EGA version)
- [[1989 - The Colonel's Bequest]]
- [[1990 - Codename - Iceman]]
- [[1990 - Conquests of Camelot - The Search for the Grail]] — Late SCI0 (interpreter 0.000.685, March 1990)[^ref-2]

## SCI1 (1990–1992)

SCI1 arrived with King's Quest V in 1990 and "combined 256-color VGA graphics with an icon-driven interface."[^ref-1] Many SCI1 games shipped in both 16-color EGA and 256-color VGA versions.[^ref-2]

### Technical Specifications
| Specification | Details |
|---------------|---------|
| Resolution | 320×200 pixels |
| Color Depth | 256 colors (VGA); EGA versions of many games |
| Interface | Point-and-click with icon bar |
| Audio | Wider sound card support, digitized sound; CD-ROM speech in later releases |

### Point-and-Click Interface
SCI1 introduced Sierra's icon-driven point-and-click interface, which replaced the text parser.[^ref-1]

### Voice Acting Debuts
Sierra's "first foray into CD-ROM" was the [[1990 - Mixed-Up Mother Goose (SCI Remake)|Mixed-Up Mother Goose]] CD, for which "professional actors were hired to voice every line of dialog"; ScummVM's version lists date that SCI1 CD build to July 1991.[^ref-4][^ref-2] [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest V]]'s later CD-ROM talkie was voiced in-house: according to The Digital Antiquarian it "had apparently been voiced by whoever happened to be hanging around the office that day".[^ref-5]

### Notable SCI1 Games
- [[1990 - King's Quest V - Absence Makes the Heart Go Yonder]] — The first SCI1 game[^ref-1]
- [[1991 - Space Quest IV - Roger Wilco and the Time Rippers]]
- [[1991 - Leisure Suit Larry 5 - Passionate Patti Does a Little Undercover Work]]
- [[1991 - Police Quest III - The Kindred]]
- [[1991 - Conquests of the Longbow - The Legend of Robin Hood]]
- [[1991 - Castle of Dr. Brain]]
- [[1991 - EcoQuest - The Search for Cetus]]
- [[1990 - Mixed-Up Mother Goose (SCI Remake)]] — CD version 1991[^ref-2]

## SCI1.1 (1992–1993)

SCI1.1 (1992) "added enhanced animation and sprite scaling".[^ref-1]

### Technical Specifications
| Specification | Details |
|---------------|---------|
| Resolution | 320×200 pixels |
| Color Depth | 256 colors |
| Interface | Refined point-and-click |
| Audio | Digitized speech on CD-ROM releases |
| New Features | Lip-sync technology (King's Quest VI) |

### Production Values Rise
SCI1.1 powered several of Sierra's most acclaimed games:
- King's Quest VI's budget was "about US$700,000" according to Roberta Williams; The Digital Antiquarian says Sierra was "prepared to push its development budget to $1 million and beyond".[^ref-11][^ref-5]
- King's Quest VI "got a professional cast, headed by Robby Benson".[^ref-5]
- Technology from Bright Star, acquired in July 1992, synced recorded voices to characters' mouths; "King's Quest VI became the first Sierra game to make use of it".[^ref-5]

### Notable SCI1.1 Games
- [[1992 - King's Quest VI - Heir Today, Gone Tomorrow]]
- [[1992 - Quest for Glory I - So You Want to Be a Hero VGA]] — VGA remake
- [[1992 - Quest for Glory III - Wages of War]]
- [[1992 - The Dagger of Amon Ra]]
- [[1993 - Space Quest V - The Next Mutation]]
- [[1993 - Freddy Pharkas - Frontier Pharmacist]]
- [[1993 - Pepper's Adventures in Time]]
- [[1993 - Leisure Suit Larry 6 - Shape Up or Slip Out!]] (original low-resolution release)[^ref-2]

## SCI2 (1993)

SCI2 (1993) brought 640×480 SVGA graphics in 256 colors and moved the interpreter to 32-bit protected mode.[^ref-1] The first SCI2 games appeared in late 1993.[^ref-2]

### Technical Specifications
| Specification | Details |
|---------------|---------|
| Resolution | 640×480 pixels (Super VGA) |
| Color Depth | 256 colors |
| Architecture | 32-bit protected mode |

### Notable SCI2 Games
- [[1993 - Gabriel Knight - Sins of the Fathers]] — SCI2 2.000.000, November 1993 (only its demo is SCI1.1)[^ref-2]
- [[1993 - Police Quest - Open Season]] — November 1993[^ref-2]
- [[1993 - Quest for Glory IV - Shadows of Darkness]] — December 1993 (only its demo is SCI1.1)[^ref-2]

## SCI2.1 (1994–1996)

SCI2.1 introduced Sierra's video formats: "Robot videos were firstly introduced here, in the DOS version of KQ7", and VMD video followed in later SCI2.1 builds.[^ref-2]

### Animation Quality
King's Quest VII's hand-drawn animation drew comparisons to film: Computer Gaming World's February 1995 review praised "Animation as good as you'd get from a middle-quality Disney feature, with voices and writing to match."[^ref-17]

### Notable SCI2.1 Games
- [[1994 - King's Quest VII - The Princeless Bride]] — November 1994[^ref-2]
- [[1995 - Phantasmagoria]] — FMV horror on seven discs[^ref-2][^ref-8]
- [[1995 - The Beast Within - A Gabriel Knight Mystery]] — FMV
- [[1995 - Space Quest 6 - Roger Wilco in the Spinal Frontier]]
- [[1995 - Torin's Passage]]
- [[1995 - Shivers]]
- [[1995 - Police Quest - SWAT]]

## SCI3 (1996)

SCI3 was the final iteration, adding native Windows 95 support; the last interpreter was 3.000.000.[^ref-1]

### Technical Specifications
| Specification | Details |
|---------------|---------|
| Resolution | 640×480 pixels |
| Color Depth | 256 colors |
| Architecture | 32-bit |

### Notable SCI3 Games
- [[1996 - Leisure Suit Larry 7 - Love for Sail]] — SCI3 3.000.000 (only its demo is SCI2.1)[^ref-2]
- [[1996 - Lighthouse - The Dark Being]][^ref-2]
- [[1996 - Phantasmagoria - A Puzzle of Flesh]][^ref-2]
- [[1996 - Rama]] — Developed by Dynamix; SCI3 3.000.000[^ref-9][^ref-2]

## Sound System Support

SCI supported "a variety of sound hardware, including AdLib, Sound Blaster, and Roland MT-32."[^ref-1] From SCI0 on, Sierra supported the Roland MT-32, Ad Lib and Game Blaster.[^ref-3]

| Device | Type |
|--------|------|
| Roland MT-32 / LAPC-I | MIDI synthesizer |
| AdLib | FM synthesis card |
| Sound Blaster family | Sound card |
| Game Blaster | Sound card |
| General MIDI | MIDI standard (later games) |
| Tandy 3-voice | Built-in audio |
| PC Speaker | Internal speaker |

## Technical Achievements

### Sierra firsts
| Achievement | Game | Year |
|-------------|------|------|
| One of the first Sound Blaster games | Space Quest III | 1989[^ref-7] |
| Sierra's first CD-ROM release, with professional voice actors | Mixed-Up Mother Goose (CD) | 1991[^ref-4][^ref-2] |
| Sierra's first game with lip-sync technology | King's Quest VI | 1992[^ref-5] |

### Production Scale
SCI enabled increasingly ambitious productions:
- King's Quest VI: about $700,000 by Roberta Williams's estimate (The Digital Antiquarian: $1 million and beyond); voice cast headed by Robby Benson[^ref-11][^ref-5]
- Gabriel Knight: CD-ROM version voiced by Tim Curry, Leah Remini and Mark Hamill[^ref-12]
- Phantasmagoria: budgeted at $800,000, "it ultimately cost $4.5 million"; released on seven discs[^ref-8]

## Decline and Legacy

### End of SCI
SCI's last interpreter shipped in 1996.[^ref-1] Sierra's later adventures moved to new 3D engines:
- [[1998 - Quest for Glory V - Dragon Fire|Quest for Glory V]] (1998) — began on a voxel engine, "later changed to a 3D engine"[^ref-15]
- [[1998 - King's Quest - Mask of Eternity|King's Quest: Mask of Eternity]] (1998) — the first King's Quest "to use a full 3D" engine[^ref-16]

### Preservation
SCI games are preserved through multiple methods:
- **ScummVM** — Supports SCI0 through SCI3; the FreeSCI code was merged into ScummVM in 2009, and ScummVM 2.0 (2017) added "almost all of the 32-bit Sierra adventures".[^ref-13][^ref-14][^ref-10]
- **FreeSCI** — The earlier open-source interpreter, merged into ScummVM in 2009.[^ref-1][^ref-13]
- **DOSBox** — DOS emulation for running the original interpreters.

### Ongoing Development
The SCI engine has been extensively reverse-engineered by the FreeSCI and ScummVM projects, whose work documents the interpreter versions game by game.[^ref-13][^ref-2]

## Playing SCI Games Today

### Recommended Setup
- **ScummVM** — Runs SCI games from SCI0 through SCI3; its compatibility list rates every SCI32 title "Good" or "Excellent".[^ref-10]
- **GOG.com versions** — Pre-configured for modern systems; GOG's Gabriel Knight, for example, "replaced DOSBox with ScummVM 2.0" in 2018.[^ref-18]

### Audio Enhancement
- ScummVM includes built-in MT-32 emulation (it needs the original MT-32 ROMs) and General MIDI output. See [[Audio and Music Tech]].

### Known Issues
- Voice acting quality varies on early CD-ROM releases; the King's Quest V talkie is the usual example.[^ref-5]

## See Also

- [[Adventure Game Interpreter]] — AGI predecessor
- [[Engine History]] — Sierra's engine generations
- [[Versions|GOG and compilation version tables (2015 SCG snapshot)]]
- [[ScummVM]] — Modern SCI interpreter
- [[King's Quest Series]] — Flagship SCI series
- [[Quest for Glory Series]] — RPG-adventure hybrid
- [[Gabriel Knight Series]] — Mature SCI storytelling

## References

[^ref-1]: [Wikipedia — Sierra Creative Interpreter](https://en.wikipedia.org/wiki/Sierra_Creative_Interpreter) — Authors Jeff Stephenson and Robert Heitman; September 1988 debut with KQ IV; version table (SCI0 16-color EGA, SCI1 1990 VGA + icons, SCI1.1 sprite scaling, SCI2 1993 640×480 32-bit, SCI3 1996 Windows 95); final 3.000.000 (November 30, 1996); FreeSCI merged into ScummVM 2009
[^ref-2]: [ScummVM Wiki — Sierra Game Versions (Wayback, May 2024)](http://web.archive.org/web/20240518064410/https://wiki.scummvm.org/index.php/Sierra_Game_Versions) — Dated interpreter builds per game; "SCI2, SCI21, and SCI3 can be collectively referred to as SCI32"; Robot video "firstly introduced ... in the DOS version of KQ7"
[^ref-3]: [The Digital Antiquarian — Sierra Gets Creative](https://www.filfre.net/2016/08/sierra-gets-creative/) — Resolution doubled to 320 X 200; SCI0 did not support MCGA/VGA; MT-32, Ad Lib, Game Blaster support
[^ref-4]: [The Digital Antiquarian — Sierra at the Cusp of the Multimedia Age](https://www.filfre.net/2018/01/sierra-at-the-cusp-of-the-multimedia-age/) — Mixed-Up Mother Goose as Sierra's "first foray into CD-ROM"; "professional actors were hired to voice every line of dialog"
[^ref-5]: [The Digital Antiquarian — The Mortgaging of Sierra On-Line](https://www.filfre.net/2019/07/the-mortgaging-of-sierra-online/) — KQ VI budget "$1 million and beyond"; KQ V talkie voiced by office staff; KQ VI cast headed by Robby Benson; Bright Star lip-sync, KQ VI first Sierra game to use it
[^ref-6]: [Sierra mail-order flyer — Ad Lib and Roland MT-32 (mocagh)](https://mocagh.org/sierra/sierra-musicdemoad.pdf) — Period source: "The MT-32 is actually eight individual synthesizers and a percussion sound module"
[^ref-7]: [Wikipedia — Space Quest III](https://en.wikipedia.org/wiki/Space_Quest_III) — "one of the first games to support the new Sound Blaster sound card"
[^ref-8]: [Wikipedia — Phantasmagoria (video game)](https://en.wikipedia.org/wiki/Phantasmagoria_(video_game)) — Budgeted at $800,000, "ultimately cost $4.5 million"; released on seven discs
[^ref-9]: [Wikipedia — Rama (video game)](https://en.wikipedia.org/wiki/Rama_(video_game)) — Developer Dynamix (1996)
[^ref-10]: [ScummVM Compatibility List](https://www.scummvm.org/compatibility/) — SCI game support ratings (checked 2026-10-16)
[^ref-11]: [Wikipedia — King's Quest VI](https://en.wikipedia.org/wiki/King%27s_Quest_VI) — Williams "estimated the budget to have been about US$700,000"
[^ref-12]: [Wikipedia — Gabriel Knight: Sins of the Fathers](https://en.wikipedia.org/wiki/Gabriel_Knight:_Sins_of_the_Fathers) — CD-ROM voices of Tim Curry, Leah Remini and Mark Hamill
[^ref-13]: [ScummVM News — FreeSCI merged (February 15, 2009)](https://www.scummvm.org/news/20090215/) — "FreeSCI code now lives under engines/sci"
[^ref-14]: [ScummVM News — ScummVM 2.0 (December 17, 2017)](https://www.scummvm.org/news/20171217/) — "almost all of the 32-bit Sierra adventures"
[^ref-15]: [Wikipedia — Quest for Glory V: Dragon Fire](https://en.wikipedia.org/wiki/Quest_for_Glory_V:_Dragon_Fire) — "originally had a voxel engine, which was later changed to a 3D engine"
[^ref-16]: [Wikipedia — King's Quest: Mask of Eternity](https://en.wikipedia.org/wiki/King%27s_Quest:_Mask_of_Eternity) — First in the series to use full 3D
[^ref-17]: [Computer Gaming World #127 (February 1995)](https://archive.org/download/Computer_Gaming_World_Issue_127/Computer_Gaming_World_Issue_127_djvu.txt) — Period scan (OCR): KQ VII "Animation as good as you'd get from a middle-quality Disney feature, with voices and writing to match"
[^ref-18]: [GOG.com — Gabriel Knight: Sins of the Fathers](https://www.gog.com/en/game/gabriel_knight_sins_of_the_fathers) — Internal Update (23 April 2018): "replaced DOSBox with ScummVM 2.0"
