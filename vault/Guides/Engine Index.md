---
title: "Engine Index"
type: index
last_updated: "2026-10-26"
---
# Engine Index

<small style="color: gray">Last updated: October 26, 2026</small>

A listing of Sierra games organized by engine, with technical specifications and compatibility information. It is not exhaustive: some vault games are not listed yet, and games whose engine no source documents are grouped at the end. Use ScummVM for most adventure games, DOSBox for simulations and sports titles.

---

## Quick Reference

| Engine | Years | Resolution | Colors | Interface | Best Emulator |
|--------|-------|------------|--------|-----------|---------------|
| AGI | 1984–1989 | 160×200 | 16 (EGA) | Text parser | ScummVM |
| SCI0 | 1988–1990 | 320×200 | 16 (EGA) | Text parser + mouse | ScummVM |
| SCI1 | 1990–1992 | 320×200 | 256 (VGA), some 16-color EGA versions | Point-and-click (QfG II kept the text parser)[^ref-26] | ScummVM |
| SCI1.1 | 1992–1993 | 320×200 | 256 (VGA) | Point-and-click | ScummVM |
| SCI2/SCI32 | 1993–1996 | Up to 640×480 | 256 | — | ScummVM |
| DGDS | 1990–1993 | 320×200 | 16 (EGA) / 256 (VGA) | Point-and-click | ScummVM |
| 3-Space | Listed games 1989–1998 | Various | Various | Sim controls | DOSBox |

Engine years and colors: AGI[^ref-6], SCI[^ref-7][^ref-1]; DGDS colors per ScummVM's DGDS detection table, which includes a 16-color EGA Rise of the Dragon.[^ref-4] DGDS and 3-Space years are the span of the games listed below; Sierra Chest's engine pages give no years or colors.[^ref-11][^ref-10]

---

## Sierra Adventure Engines

### ADL (Adventure Development Language) — 1980–1983

Created by Ken Williams for On-Line Systems' first games, the Hi-Res Adventure series. ScummVM supports all seven Hi-Res Adventures (rated "Good"); its ADL page lists Adventure in Serenia as a version of Hi-Res Adventure #2.[^ref-28][^ref-5]

**Play with:** ScummVM

- **1980** — [[1980 - Hi-Res Adventure 0 - Mission Asteroid|Hi-Res Adventure #0: Mission Asteroid]]
- **1980** — [[1980 - Hi-Res Adventure 1 - Mystery House|Hi-Res Adventure #1: Mystery House]]
- **1980** — [[1980 - Hi-Res Adventure 2 - The Wizard and the Princess|Hi-Res Adventure #2: The Wizard and the Princess]]
- **1981** — [[1981 - Hi-Res Adventure 3 - Cranston Manor|Hi-Res Adventure #3: Cranston Manor]]
- **1981** — [[1981 - Hi-Res Adventure 4 - Ulysses and the Golden Fleece|Hi-Res Adventure #4: Ulysses and the Golden Fleece]]
- **1982** — [[1982 - Adventure in Serenia|Adventure in Serenia]] (version of Hi-Res Adventure #2)
- **1982** — [[1982 - Hi-Res Adventure 5 - Time Zone|Hi-Res Adventure #5: Time Zone]]
- **1983** — [[1983 - Hi-Res Adventure 6 - The Dark Crystal|Hi-Res Adventure #6: The Dark Crystal]]

---

### AGI (Adventure Game Interpreter) — 1984–1989

The engine Sierra created for King's Quest I on the IBM PCjr, used for 14 games between 1984 and 1989.[^ref-6]

| Spec | Details |
|------|---------|
| Resolution | 160×200 (displayed 320×200) |
| Colors | 16 (EGA/CGA) |
| Interface | Text parser |

**Play with:** ScummVM (recommended), DOSBox

- **1984** — [[1984 - King's Quest - Quest for the Crown|King's Quest I: Quest for the Crown]]
- **1984** — [[1984 - Donald Duck's Playground|Donald Duck's Playground]] (the AGI version dates from June 8, 1986: interpreter 2.001, which ScummVM calls "more an hybrid between AGI1 & AGI2")[^ref-1]
- **1985** — [[1985 - King's Quest II - Romancing the Throne|King's Quest II: Romancing the Throne]]
- **1986** — [[1986 - King's Quest III - To Heir Is Human|King's Quest III: To Heir Is Human]]
- **1986** — [[1986 - Space Quest - The Sarien Encounter|Space Quest I: The Sarien Encounter]]
- **1986** — [[1986 - The Black Cauldron|The Black Cauldron]]
- **1987** — [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards|Leisure Suit Larry 1]]
- **1987** — [[1987 - Mixed-Up Mother Goose|Mixed-Up Mother Goose]]
- **1987** — [[1987 - Police Quest - In Pursuit of the Death Angel|Police Quest I]]
- **1987** — [[1987 - Space Quest II - Vohaul's Revenge|Space Quest II: Vohaul's Revenge]]
- **1988** — [[1988 - King's Quest IV - The Perils of Rosella|King's Quest IV: The Perils of Rosella]] (AGI version, released alongside the SCI version)[^ref-1][^ref-6]
- **1988** — [[1988 - Gold Rush|Gold Rush!]]
- **1988** — [[1988 - Manhunter - New York|Manhunter: New York]]
- **1989** — [[1989 - Manhunter - San Francisco|Manhunter 2: San Francisco]]

AGI assignments per the ScummVM version list.[^ref-1]

**Pre-AGI** (earlier Sierra engine; ScummVM runs these through its AGI engine):[^ref-2][^ref-5]
- **1983** — [[1983 - Troll's Tale|Troll's Tale]]
- **1984** — [[1984 - Mickey's Space Adventure|Mickey's Space Adventure]]
- **1984** — [[1984 - Winnie the Pooh in the Hundred Acre Wood|Winnie the Pooh in the Hundred Acre Wood]]

---

### SCI0 (Sierra Creative Interpreter) — 1988–1990

First SCI version, doubling AGI's resolution with sound card support.[^ref-7]

| Spec | Details |
|------|---------|
| Resolution | 320×200 |
| Colors | 16 (EGA) |
| Interface | Enhanced text parser + mouse movement |
| Audio | PC Speaker, AdLib, Roland MT-32, Game Blaster |

**Play with:** ScummVM (recommended), DOSBox

- **1988** — [[1988 - King's Quest IV - The Perils of Rosella|King's Quest IV: The Perils of Rosella]]
- **1988** — [[1988 - Leisure Suit Larry Goes Looking for Love (in Several Wrong Places)|Leisure Suit Larry 2]]
- **1988** — [[1988 - Police Quest II - The Vengeance|Police Quest II: The Vengeance]]
- **1989** — [[1990 - Codename - Iceman|Codename: Iceman]][^ref-16]
- **1989** — [[1989 - Hoyle Official Book of Games - Volume 1|Hoyle Volume 1]]
- **1989** — [[1989 - Leisure Suit Larry III - Passionate Patti in Pursuit of the Pulsating Pectorals|Leisure Suit Larry 3]]
- **1989** — [[1989 - Quest for Glory I - So You Want to Be a Hero|Quest for Glory I]]
- **1989** — [[1989 - Space Quest III - The Pirates of Pestulon|Space Quest III]]
- **1989** — [[1989 - The Colonel's Bequest|The Colonel's Bequest]]
- **1990** — [[1990 - Conquests of Camelot - The Search for the Grail|Conquests of Camelot]]
- **1990** — [[1990 - Hoyle Official Book of Games - Volume 2|Hoyle Volume 2]]
- **1990** — [[1990 - Mixed-Up Mother Goose (SCI Remake)|Mixed-Up Mother Goose (SCI)]]
- **1990** — [[1990 - Roberta Williams' King's Quest I - Quest for the Crown|King's Quest I SCI Remake]]

SCI0 assignments per the ScummVM version list (King's Quest I SCI uses the SCI01 revision).[^ref-1]

---

### SCI1 — 1990–1992

First VGA engine, with 256 colors and point-and-click interfaces. SCI1 games were released in both 16-color EGA and 256-color VGA versions, and Quest for Glory II used an earlier, EGA-only SCI1 build (1.000.041).[^ref-1][^ref-7]

| Spec | Details |
|------|---------|
| Resolution | 320×200 |
| Colors | 256 (VGA); 16 (EGA) versions too |
| Interface | Point-and-click icon bar (QfG II kept the text parser)[^ref-26] |
| Audio | AdLib, Sound Blaster, Roland MT-32 |
| CD-ROM | Mixed-Up Mother Goose CD and King's Quest V CD were SCI1 releases[^ref-1] |

**Play with:** ScummVM (recommended), DOSBox

- **1990** — [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest V]]
- **1990** — [[1990 - Quest for Glory II - Trial by Fire|Quest for Glory II]] (SCI1, EGA only)
- **1991** — [[1991 - Castle of Dr. Brain|Castle of Dr. Brain]]
- **1991** — [[1991 - Conquests of the Longbow - The Legend of Robin Hood|Conquests of the Longbow]]
- **1991** — [[1991 - EcoQuest - The Search for Cetus|EcoQuest]]
- **1991** — [[1991 - Hoyle Official Book of Games - Volume 3|Hoyle Volume 3]]
- **1991** — [[1990 - Jones in the Fast Lane|Jones in the Fast Lane]][^ref-17]
- **1991** — [[1991 - Leisure Suit Larry 1 - In the Land of the Lounge Lizards (VGA)|Leisure Suit Larry 1 VGA]]
- **1991** — [[1991 - Leisure Suit Larry 5 - Passionate Patti Does a Little Undercover Work|Leisure Suit Larry 5]]
- **1991** — [[1991 - Mixed-Up Fairy Tales|Mixed-Up Fairy Tales]]
- **1991** — [[1991 - Police Quest III - The Kindred|Police Quest III]]
- **1991** — [[1991 - Space Quest I - Roger Wilco in the Sarien Encounter|Space Quest I VGA]]
- **1991** — [[1991 - Space Quest IV - Roger Wilco and the Time Rippers|Space Quest IV]]

SCI1 assignments per the ScummVM version list.[^ref-1]

---

### SCI1.1 — 1992–1993

Revised SCI1 with enhanced animation and sprite scaling; many SCI1.1 games also had CD-ROM talkie versions.[^ref-7][^ref-1]

| Spec | Details |
|------|---------|
| Resolution | 320×200 |
| Colors | 256 (VGA) |
| Interface | Point-and-click (refined) |
| Audio | Sound Blaster |

**Play with:** ScummVM (recommended), DOSBox

- **1992** — [[1992 - Crazy Nick's Software Picks - King Graham's Board Game Challenge|Crazy Nick's: King Graham]]
- **1992** — [[1992 - Crazy Nick's Software Picks - Leisure Suit Larry's Casino|Crazy Nick's: Larry's Casino]]
- **1992** — [[1992 - Crazy Nick's Software Picks - Parlor Games with Laura Bow|Crazy Nick's: Laura Bow]]
- **1992** — [[1992 - Crazy Nick's Software Picks - Robin Hood's Games of Skill and Chance|Crazy Nick's: Robin Hood]]
- **1992** — [[1992 - Crazy Nick's Software Picks - Roger Wilco's Spaced Out Game Pack|Crazy Nick's: Roger Wilco]]
- **1992** — [[1992 - King's Quest VI - Heir Today, Gone Tomorrow|King's Quest VI]]
- **1992** — [[1992 - Police Quest - In Pursuit of the Death Angel VGA|Police Quest I VGA]]
- **1992** — [[1992 - Quest for Glory I - So You Want to Be a Hero VGA|Quest for Glory I VGA]]
- **1992** — [[1992 - Quest for Glory III - Wages of War|Quest for Glory III]]
- **1992** — [[1992 - The Dagger of Amon Ra|Laura Bow 2: Dagger of Amon Ra]]
- **1992** — [[1992 - The Island of Dr. Brain|Island of Dr. Brain]]
- **1993** — [[1993 - EcoQuest - Lost Secret of the Rainforest|EcoQuest 2]]
- **1993** — [[1993 - Freddy Pharkas - Frontier Pharmacist|Freddy Pharkas]]
- **1993** — [[1991 - Hoyle Official Book of Games - Volume 4|Hoyle Volume 4 (Hoyle Classic Card Games)]][^ref-18]
- **1993** — [[1993 - Leisure Suit Larry 6 - Shape Up or Slip Out!|Leisure Suit Larry 6]]
- **1993** — [[1993 - Pepper's Adventures in Time|Pepper's Adventures in Time]]
- **1993** — [[1993 - Slater & Charlie Go Camping|Slater & Charlie Go Camping]]
- **1993** — [[1993 - Space Quest V - The Next Mutation|Space Quest V]]

SCI1.1 assignments per the ScummVM version list.[^ref-1]

---

### SCI2 / SCI2.1 / SCI3 (SCI32) — 1993–1996

SCI2, SCI2.1 and SCI3 are together called SCI32 because the original interpreters were 32-bit executables. They brought SVGA graphics and full-motion video, and shipped for DOS as well as Windows; SCI3 (1996) added native Windows 95 support. Sierra abandoned SCI after 1997.[^ref-1][^ref-7]

| Spec | Details |
|------|---------|
| Resolution | Up to 640×480 (SVGA) |
| Colors | 256 |
| Platform | 32-bit DOS, Windows 3.1/95 and Macintosh[^ref-1] |
| New Features | FMV cutscenes, higher resolution |

**Play with:** ScummVM (recommended), Windows compatibility mode

- **1993** — [[1993 - Gabriel Knight - Sins of the Fathers|Gabriel Knight]] (SCI2; only the demo was SCI1.1)
- **1993** — [[1993 - Police Quest - Open Season|Police Quest: Open Season]] (SCI2; only the demo was SCI1.1)
- **1993** — [[1993 - Quest for Glory IV - Shadows of Darkness|Quest for Glory IV]] (SCI2; only the demo was SCI1.1)
- **1994** — [[1994 - King's Quest VII - The Princeless Bride|King's Quest VII]]
- **1995** — [[1995 - Mixed-Up Mother Goose Deluxe|Mixed-Up Mother Goose Deluxe]]
- **1995** — [[1995 - Phantasmagoria|Phantasmagoria]]
- **1995** — [[1995 - Police Quest - SWAT|Police Quest: SWAT]]
- **1995** — [[1995 - Shivers|Shivers]]
- **1995** — [[1995 - Space Quest 6 - Roger Wilco in the Spinal Frontier|Space Quest 6]]
- **1995** — [[1995 - The Beast Within - A Gabriel Knight Mystery|Gabriel Knight 2]]
- **1995** — [[1995 - Torin's Passage|Torin's Passage]]
- **1996** — [[1996 - Hoyle Bridge|Hoyle Bridge]] (SCI2.1)[^ref-27]
- **1996** — [[1996 - Hoyle Official Book of Games - Volume 5|Hoyle Volume 5]] (SCI2.1) — note: the linked page currently describes Hoyle Solitaire; ScummVM lists Hoyle Classic Games (hoyle5) and Hoyle Solitaire (hoyle5solitaire) as separate games[^ref-27]
- **1996** — [[1996 - Hoyle Solitaire|Hoyle Solitaire]] (SCI2.1)
- **1996** — [[1996 - Leisure Suit Larry 7 - Love for Sail|Leisure Suit Larry 7]]
- **1996** — [[1996 - Lighthouse - The Dark Being|Lighthouse]] (SCI3)
- **1996** — [[1996 - Phantasmagoria - A Puzzle of Flesh|Phantasmagoria 2]]
- **1996** — [[1996 - Rama|RAMA]]
- **1996** — [[1996 - The Realm Online|The Realm Online]] (SCI2.1)[^ref-27]

SCI32 assignments per the ScummVM version list.[^ref-1]

---

### Later Sierra Engines (not SCI)

- **1997** — [[1997 - Shivers Two - Harvest of Souls|Shivers II]] — SCI resources, but its room logic was rewritten as native code in DLL files, so ScummVM classes it "not SCI"[^ref-1][^ref-3]
- **1998** — [[1998 - King's Quest - Mask of Eternity|King's Quest: Mask of Eternity]] — Engine: Dynamix's ThreeSpace (3-Space), adapted for the game[^ref-8]
- **1998** — [[1998 - Quest for Glory V - Dragon Fire|Quest for Glory V]] — not SCI[^ref-1]
- **1999** — [[1999 - Gabriel Knight 3 - Blood of the Sacred, Blood of the Damned|Gabriel Knight 3]] — Engine: G-Engine[^ref-9]

---

## Dynamix Engines

### DGDS (Dynamix Game Development System)

Point-and-click adventures. **Play with:** ScummVM (Rise of the Dragon, Heart of China, Willy Beamish)[^ref-5]

- **1990** — [[1990 - Rise of the Dragon|Rise of the Dragon]]
- **1991** — [[1991 - Heart of China|Heart of China]]
- **1991** — [[1991 - The Adventures of Willy Beamish|The Adventures of Willy Beamish]]
- **1992** — [[1992 - Johnny Castaway|Johnny Castaway]] (screensaver)[^ref-4]
- **1992** — [[1992 - Quarky & Quaysoo's Turbo Science|Quarky & Quaysoo's Turbo Science]]
- **1993** — [[1993 - Turbo Learning - Mega Math|Turbo Learning: Mega Math]]

DGDS members per Sierra Chest and ScummVM's DGDS detection table.[^ref-11][^ref-4]

---

### 3-Space Engine (Flight & Combat Sims)

Designed by Damon Slye with David McClurg; Slye lists Stellar 7, Arcticfox, Abrams Battletank, Nova 9, A-10 Tank Killer, Red Baron, Aces of the Pacific, Aces Over Europe, David Wolf: Secret Agent, MechWarrior, EarthSiege, EarthSiege 2, Silent Thunder, Red Baron II and Red Baron 3D as 3-Space games.[^ref-10]

**Play with:** DOSBox

- **1989** — [[1989 - A-10 Tank Killer|A-10 Tank Killer]]
- **1989** — [[1989 - David Wolf - Secret Agent|David Wolf: Secret Agent]]
- **1989** — [[1989 - MechWarrior|MechWarrior]]
- **1990** — [[1990 - Red Baron|Red Baron]]
- **1990** — [[1990 - Stellar 7|Stellar 7]]
- **1991** — [[1991 - A-10 Tank Killer v1.5|A-10 Tank Killer v1.5]][^ref-10]
- **1991** — [[1991 - Nova 9 - The Return of Gir Draxon|Nova 9]]
- **1992** — [[1992 - Aces of the Pacific|Aces of the Pacific]]
- **1992** — [[1992 - Aces of the Pacific - WWII 1946|Aces of the Pacific: WWII: 1946]]
- **1992** — [[1992 - Red Baron - Mission Builder|Red Baron: Mission Builder]]
- **1993** — [[1993 - Aces Over Europe|Aces Over Europe]]
- **1993** — [[1993 - Betrayal at Krondor|Betrayal at Krondor]]
- **1994** — [[1994 - Metaltech - Earthsiege|Metaltech: Earthsiege]]
- **1995** — [[1995 - Metaltech - Earthsiege Expansion Pack|Metaltech: Earthsiege Expansion Pack]][^ref-10]
- **1996** — [[1996 - Earthsiege 2|Earthsiege 2]]
- **1996** — [[1996 - Silent Thunder - A-10 Tank Killer II|Silent Thunder: A-10 Tank Killer II]]
- **1997** — [[1997 - Red Baron II|Red Baron II]]
- **1998** — [[1998 - Red Baron 3D|Red Baron 3D]]

---

### 3-D Ultra Series

No source names the engine: Sierra Chest lists the 3-D Ultra series under "Unknown/unnamed".[^ref-12]

**Play with:** DOSBox, Windows compatibility mode

- **1995** — [[1995 - 3-D Ultra Pinball|3-D Ultra Pinball]] — Type: Pinball
- **1996** — [[1996 - 3-D Ultra Pinball - Creep Night|3-D Ultra Pinball: Creep Night]] — Type: Pinball
- **1997** — [[1997 - 3-D Ultra Pinball - The Lost Continent|3-D Ultra Pinball: Lost Continent]] — Type: Pinball
- **1997** — [[1997 - 3-D Ultra MiniGolf|3-D Ultra MiniGolf]] — Type: Minigolf
- **1998** — [[1998 - 3-D Ultra MiniGolf Deluxe|3-D Ultra MiniGolf Deluxe]] — Type: Minigolf
- **1998** — [[1998 - 3-D Ultra NASCAR Pinball|3-D Ultra NASCAR Pinball]] — Type: Pinball
- **1999** — [[1999 - 3-D Ultra Cool Pool|3-D Ultra Cool Pool]] — Type: Pool
- **1999** — [[1999 - 3-D Ultra Lionel TrainTown|3-D Ultra Lionel TrainTown]] — Type: Trains
- **1999** — [[1999 - 3-D Ultra Radio Control Racers|3-D Ultra RC Racers]] — Type: Racing
- **2000** — [[2000 - 3-D Ultra Pinball - Thrill Ride|3-D Ultra Pinball: Thrill Ride]] — Type: Pinball
- **2000** — [[2000 - 3-D Ultra Radio Control Racers Deluxe - Traxxas Edition|3-D Ultra RC Racers Deluxe]] — Type: Racing

---

### Dynamix Sports Titles (engine unnamed)

No source names a shared engine for these; Sierra Chest lists them under "Unknown/unnamed".[^ref-12]

- **1992** — [[1992 - Front Page Sports Football 92|Front Page Sports: Football]]
- **1993** — [[1993 - Front Page Sports - Football Pro|Front Page Sports: Football Pro]]
- **1994** — [[1994 - Front Page Sports - Baseball Pro|Front Page Sports: Baseball Pro]]
- **1994** — [[1994 - Front Page Sports - Football Pro '95|Front Page Sports: Football Pro '95]]
- **1995** — [[1995 - Front Page Sports - Football Pro '96|Front Page Sports: Football Pro '96]]
- **1995** — [[1995 - Trophy Bass|Trophy Bass]]
- **1996** — [[1996 - Front Page Sports - Baseball Pro '96|Front Page Sports: Baseball Pro '96]]
- **1996** — [[1996 - Front Page Sports - Football Pro '97|Front Page Sports: Football Pro '97]]
- **1996** — [[1996 - Front Page Sports - Trophy Bass 2|Trophy Bass 2]]
- **1997** — [[1997 - Front Page Sports - Football Pro '98|Front Page Sports: Football Pro '98]]

---

## Papyrus Racing Titles

Papyrus used its own in-house engines; no source gives them consistent names, and Sierra Chest lists NASCAR Racing, IndyCar Racing II and Grand Prix Legends under "Unknown/unnamed".[^ref-12] See each game page for what is documented.

**Play with:** DOSBox (early), Windows compatibility (later)

- **1989** — [[1989 - Indianapolis 500 - The Simulation|Indianapolis 500: The Simulation]]
- **1993** — [[1993 - IndyCar Racing|IndyCar Racing]]
- **1994** — [[1994 - NASCAR Racing|NASCAR Racing]]
- **1995** — [[1995 - IndyCar Racing II|IndyCar Racing II]] (DOS; reviewed in *PC Games*' December 1995 issue. MobyGames gives 1996, and the Windows 95 and Mac versions followed in 1996)[^ref-25][^ref-19]
- **1996** — [[1996 - NASCAR Racing 2|NASCAR Racing 2]]
- **1997** — [[1997 - CART Racing|CART Racing]]
- **1998** — [[1998 - Grand Prix Legends|Grand Prix Legends]]
- **1999** — [[1999 - NASCAR Racing 3|NASCAR Racing 3]]
- **2001** — [[2001 - NASCAR Racing 4|NASCAR Racing 4]]
- **2002** — [[2002 - NASCAR Racing 2002 Season|NASCAR Racing 2002]]
- **2003** — [[2003 - NASCAR Racing 2003 Season|NASCAR Racing 2003]]

---

## Impressions Engines

### City-Building Games

Impressions' 2D city-builders; Emperor was the last to use the same 2D-sprite engine as the earlier titles.[^ref-22]

**Play with:** DOSBox (Caesar I-II), Windows (Caesar III+)

- **1992** — [[1992 - Caesar|Caesar]][^ref-20]
- **1995** — [[1995 - Caesar II|Caesar II]]
- **1998** — [[1998 - Caesar III|Caesar III]]
- **1999** — [[1999 - Pharaoh|Pharaoh]]
- **2000** — [[2000 - Cleopatra - Queen of the Nile|Cleopatra: Queen of the Nile]]
- **2000** — [[2000 - Zeus - Master of Olympus|Zeus: Master of Olympus]]
- **2001** — [[2001 - Poseidon - Master of Atlantis|Poseidon: Master of Atlantis]]
- **2002** — [[2002 - Emperor - Rise of the Middle Kingdom|Emperor: Rise of the Middle Kingdom]]

**Caesar IV** is not an Impressions game: Tilted Mill Entertainment developed it on a 3D engine (Sierra Chest lists it under Titan 2.0, an update of the original Titan engine used by Empire Earth).[^ref-21][^ref-13]
- **2006** — [[2006 - Caesar IV|Caesar IV]]

### Strategy Titles (engine unnamed)

No source names a shared engine; Sierra Chest lists these under "Unknown/unnamed".[^ref-12]

- **1994** — [[1994 - Lords of the Realm|Lords of the Realm]]
- **1996** — [[1996 - Lords of the Realm II|Lords of the Realm II]]
- **1996** — [[1996 - Robert E. Lee - Civil War General|Robert E. Lee: Civil War General]]
- **1997** — [[1997 - Civil War Generals 2 - Grant–Lee–Sherman|Civil War Generals 2]]
- **1997** — [[1997 - Lords of Magic|Lords of Magic]]
- **1997** — [[1997 - Lords of the Realm II - Siege Pack|Lords of the Realm II: Siege Pack]]
- **1998** — [[1998 - Lords of Magic - Special Edition|Lords of Magic: Special Edition]]
- **2004** — [[2004 - Lords of the Realm III|Lords of the Realm III]]

---

## Coktel Vision / Gob Engine

**Play with:** ScummVM. Inca II and The Last Dynasty are detected by ScummVM's Gob engine but do not appear on its compatibility list.[^ref-5][^ref-23]

- **1991** — [[1991 - Fascination|Fascination]]
- **1991** — [[1991 - Gobliiins|Gobliiins]]
- **1992** — [[1992 - Bargon Attack|Bargon Attack]]
- **1992** — [[1992 - Gobliins 2 - The Prince Buffoon|Gobliins 2]]
- **1992** — [[1992 - Ween - The Prophecy|Ween: The Prophecy]]
- **1993** — [[1993 - Goblins Quest 3|Goblins Quest 3]]
- **1993** — [[1993 - Inca II - Wiracocha|Inca II]]
- **1993** — [[1993 - Lost in Time|Lost in Time]]
- **1995** — [[1995 - The Bizarre Adventures of Woodruff and the Schnibble|Woodruff and the Schnibble]]
- **1995** — [[1995 - The Last Dynasty|The Last Dynasty]]
- **1996** — [[1996 - Urban Runner|Urban Runner]]

---

## Valve / GoldSrc Engine

- **1998** — [[1998 - Half-Life|Half-Life]]
- **1999** — [[1999 - Half-Life - Opposing Force|Half-Life: Opposing Force]]
- **1999** — [[1999 - Team Fortress Classic|Team Fortress Classic]]
- **2000** — [[2000 - Counter-Strike|Counter-Strike]]
- **2000** — [[2000 - Gunman Chronicles|Gunman Chronicles]]
- **2001** — [[2001 - Half-Life - Blue Shift|Half-Life: Blue Shift]]
- **2004** — [[2004 - Counter-Strike - Condition Zero|Counter-Strike: Condition Zero]]

---

## Homeworld Engines

- **1999** — [[1999 - Homeworld|Homeworld]] — Engine: Homeworld
- **2000** — [[2000 - Homeworld - Cataclysm|Homeworld: Cataclysm]] — Engine: Homeworld
- **2003** — [[2003 - Homeworld 2|Homeworld 2]] — Engine: Homeworld 2
- **2015** — [[2015 - Homeworld Remastered Collection|Homeworld Remastered]] — Engine: Homeworld 2
- **2016** — [[2016 - Homeworld - Deserts of Kharak|Homeworld: Deserts of Kharak]] — Engine: Unity 5
- **2024** — [[2024 - Homeworld 3|Homeworld 3]] — Engine: Unreal Engine 4

---

## LithTech Engine (Monolith)

- **2000** — [[2000 - No One Lives Forever|No One Lives Forever]]
- **2002** — [[2002 - No One Lives Forever 2|No One Lives Forever 2]]
- **2003** — [[2003 - Contract J.A.C.K.|Contract J.A.C.K.]]

---

## Unreal Engine

- **2005** — [[2005 - SWAT 4|SWAT 4]] — Version: Unreal 2 (Vengeance)
- **2006** — [[2006 - SWAT 4 - The Stetchkov Syndicate|SWAT 4: Stetchkov Syndicate]] — Version: Unreal 2
- **2009** — [[2009 - Leisure Suit Larry - Box Office Bust|LSL: Box Office Bust]] — Version: Unreal 3
- **2015** — [[2015 - King's Quest|King's Quest (2015)]] — Version: Unreal 3
- **2024** — [[2024 - Homeworld 3|Homeworld 3]] — Version: Unreal 4

---

## Adventure Game Studio (Fan Projects)

- **2001** — [[2001 - King's Quest I VGA Remake|King's Quest I VGA (AGDI)]]
- **2002** — [[2002 - King's Quest II+ - Romancing the Stones|King's Quest II: Romancing the Stones (AGDI)]]
- **2006** — [[2006 - Al Emmo and the Lost Dutchman's Mine|Al Emmo]]
- **2006** — [[2006 - King's Quest III Remake (Infamous Adventures)|King's Quest III (Infamous)]]
- **2008** — [[2008 - Quest for Glory II VGA Remake|Quest for Glory II VGA (AGDI)]]
- **2011** — [[2011 - King's Quest III Redux - To Heir is Human|King's Quest III Redux (AGDI)]]
- **2011** — [[2011 - Space Quest - Vohaul Strikes Back|Space Quest: Vohaul Strikes Back]]
- **2011** — [[2011 - Space Quest II VGA Remake|Space Quest II VGA (Infamous)]]
- **2012** — [[2012 - Space Quest - Incinerations|Space Quest: Incinerations]]
- **2014** — [[2014 - Quest for Infamy|Quest for Infamy]]
- **2016** — [[2015 - Order of the Thorne - The King's Challenge|Order of the Thorne]]
- **2019** — [[2019 - Mage's Initiation - Reign of the Elements|Mage's Initiation]]
- **2021** — [[2021 - King's Quest IV Retold|King's Quest IV Retold]]
- **2023** — [[2023 - Gobliiins 5 - The Morgloton Invasion|Gobliiins 5]]

---

## AGI (Fan Projects)

Fan games built with Sierra's AGI; MobyGames lists both in its AGI engine group.[^ref-14]

- **2001** — [[2001 - Space Quest - The Lost Chapter|Space Quest: The Lost Chapter]]
- **2003** — [[2003 - Space Quest 0 - Replicated|Space Quest 0: Replicated]]

---

## Unity Engine (Modern Projects)

- **2012** — [[2012 - Cognition - An Erica Reed Thriller|Cognition]]
- **2013** — [[2013 - Leisure Suit Larry - Reloaded|Leisure Suit Larry: Reloaded]]
- **2014** — [[2014 - Gabriel Knight - Sins of the Fathers – 20th Anniversary Edition|Gabriel Knight 20th Anniversary]]
- **2014** — [[2014 - Gold Rush Anniversary|Gold Rush! Anniversary]]
- **2014** — [[2014 - Moebius - Empire Rising|Moebius: Empire Rising]]
- **2015** — [[2015 - Cluck Yegger in Escape From The Planet of The Poultroid|Cluck Yegger]]
- **2018** — [[2018 - Hero-U - Rogue to Redemption|Hero-U: Rogue to Redemption]]
- **2018** — [[2018 - Leisure Suit Larry - Wet Dreams Don't Dry|LSL: Wet Dreams Don't Dry]]
- **2020** — [[2020 - Leisure Suit Larry - Wet Dreams Dry Twice|LSL: Wet Dreams Dry Twice]]
- **2022** — [[2022 - SpaceVenture|SpaceVenture]]
- **2023** — [[2023 - Colossal Cave 3D Adventure|Colossal Cave 3D]]
- **2023** — [[2023 - Summer Daze - Tilly's Tale|Summer Daze: Tilly's Tale]]

---

## Darkstar Engine (Tribes/Starsiege)

- **1998** — [[1998 - Starsiege - Tribes|Starsiege: Tribes]][^ref-15]
- **1999** — [[1999 - Starsiege|Starsiege]][^ref-15]

## Torque Game Engine

- **2001** — [[2001 - Tribes 2|Tribes 2]] — Torque was originally developed by Dynamix for Tribes 2[^ref-24]

---

## Engine Unconfirmed

These games were listed under an engine above in earlier versions of this index, but no source confirms it. Sierra Chest lists them under "Unknown/unnamed".[^ref-12]

- **1992** — [[1992 - Inca|Inca]] — ScummVM's Gob engine detects only Inca II[^ref-23]
- **1994** — [[1994 - Aces of the Deep|Aces of the Deep]]
- **1994** — [[1994 - Metaltech - Battledrome|Metaltech: Battledrome]]
- **1995** — [[1995 - The Lost Mind of Dr. Brain|Lost Mind of Dr. Brain]] — not in ScummVM's SCI version list[^ref-1]
- **1996** — [[1996 - The Time Warp of Dr. Brain|Time Warp of Dr. Brain]] — not in ScummVM's SCI version list[^ref-1]
- **1999** — [[1999 - Curse You! Red Baron|Curse You! Red Baron]]
- **2006** — [[2006 - 3D Ultra MiniGolf Adventures|3D Ultra MiniGolf Adventures]] — developed by Wanako Games, not Dynamix; Sierra Chest lists its Deluxe edition under "Unknown/unnamed"[^ref-12]

---

## Emulator Quick Reference

| Engine Type | Best Emulator/Runtime |
|-------------|----------------------|
| ADL (1980–1983) | ScummVM |
| AGI (1984–1989) | ScummVM |
| SCI (1988–1996) | ScummVM |
| Dynamix Adventures (DGDS) | ScummVM |
| Coktel/Gob | ScummVM |
| DOS Flight/Racing Sims | DOSBox |
| Windows 95/98 Games | dgVoodoo2 + Compatibility Mode |
| GoldSrc (Half-Life) | Native Steam |
| Modern Unity/AGS | Native Windows/Mac/Linux |

---

## References

[^ref-1]: [ScummVM Wiki – Sierra Game Versions (archived May 2024)](http://web.archive.org/web/20240518064410/https://wiki.scummvm.org/index.php/Sierra_Game_Versions) – interpreter version lists for AGI, SCI0/SCI01, SCI1 (ega/early/middle/late), SCI1.1, SCI2, SCI21 and SCI3; "SCI1 games were released as two versions: 16 color EGA and 256 color VGA"; "SCI2, SCI21, and SCI3 can be collectively referred to as SCI32 because the released original interpreters were 32-bit executables"; Shivers II and Quest for Glory V "not SCI"; "After 1997, the SCI engine… was abandoned"
[^ref-2]: [ScummVM source – engines/agi/detection_tables.h](https://github.com/scummvm/scummvm/blob/master/engines/agi/detection_tables.h) – "Mickey's Space Adventure // Preagi game"; Troll's Tale and Winnie the Pooh in the Hundred Acre Wood (GAMEpre_P("winnie"…)) detected as Pre-AGI (GType_PreAGI) games
[^ref-3]: [ScummVM source – engines/sci/detection_tables.h](https://github.com/scummvm/scummvm/blob/master/engines/sci/detection_tables.h) – "Shivers 2 doesn't contain SCI scripts… classifies Shivers 2 as 'not SCI'"
[^ref-4]: [ScummVM source – engines/dgds/detection_tables.h](https://github.com/scummvm/scummvm/blob/master/engines/dgds/detection_tables.h) – detection entries for Rise of the Dragon, Willy Beamish, Heart of China, Quarky & Quaysoo's Turbo Science and the Johnny Castaway screensaver
[^ref-5]: [ScummVM – Compatibility list](https://www.scummvm.org/compatibility/) – checked 2026-10-16: agi:mickey, agi:troll; agi:winnie and adl:hires0–hires6, all "Good" (checked 2026-10-26); dgds:rise, dgds:china, dgds:beamish; Gob titles listed (no Inca, Inca II or Last Dynasty)
[^ref-6]: [Wikipedia – Adventure Game Interpreter](https://en.wikipedia.org/wiki/Adventure_Game_Interpreter) – developed for King's Quest (1984) for the IBM PCjr; used "in 14 of their games between 1984 and 1989"; 160×200; KQ IV "Sierra released an AGI version of the game at the same time"
[^ref-7]: [Wikipedia – Sierra Creative Interpreter](https://en.wikipedia.org/wiki/Sierra_Creative_Interpreter) – SCI0 1988 "320 × 200, 16-color EGA", text parser; SCI1 1990 256-color VGA; SCI1.1 1992 "enhanced animation and sprite scaling"; SCI2 1993 640×480 SVGA, 256 colors; SCI3 1996 "native Windows 95 support"; latest release 1996
[^ref-8]: [Next Generation #30 (June 1997), Internet Archive scan](https://archive.org/details/NextGeneration30Jun1997) – King's Quest: Mask of Eternity feature: "ThreeSpace is the 3D engine that Dynamix, a Sierra subsidiary, contributed to the project"
[^ref-9]: [Jane Jensen – GK3 Designer Diaries #4 (June 1998), Gabriel Knight Pages](http://gkpages.altervista.org/Interviews/DesignerDiaries_04.html) – "GK3 needed this new engine… The G-Engine is a fabulous piece of engineering"
[^ref-10]: [Sierra Chest – Engine: 3-Space (archived May 2019)](https://web.archive.org/web/20190512155308/http://sierrachest.com/index.php?a=engines&id=30) – Damon Slye: "I designed the Dynamix 3Space engine, along with David McClurg. It was used in Stellar 7, Arcticfox, Abrams Battletank, Nova9, A10 Tank Killer, Red Baron, Aces of the Pacific, Aces over Europe, David Wolf Secret Agent, Mechwarrior, MetalTech: EarthSiege, EarthSiege 2, Silent Thunder, Red Baron II & Red Baron 3D"; group members include Betrayal at Krondor, Red Baron: Mission Builder, A-10 Tank Killer Version 1.5 and Metaltech: Earthsiege: Expansion Pack
[^ref-11]: [Sierra Chest – Engine: DGDS (archived May 2019)](https://web.archive.org/web/20190512152438/http://sierrachest.com/index.php?a=engines&id=36) – "Initially developed for Rise of the Dragon and enhanced for Heart of China and Willy Beamish"; members include Quarky and Quaysoo's Turbo Science and Turbo Learning: Mega Math
[^ref-12]: [Sierra Chest – Engine: Unknown/unnamed (archived May 2019)](https://web.archive.org/web/20190512153148/http://sierrachest.com/index.php?a=engines&id=15) – lists Front Page Sports, Trophy Bass, Lords of the Realm, Lords of Magic, Civil War Generals, NASCAR Racing, IndyCar Racing 2, Grand Prix Legends, Aces of the Deep, Metaltech: Battledrome, Curse You! Red Baron, Inca, Lost Mind and Timewarp of Dr. Brain
[^ref-13]: [Sierra Chest – Engine: Titan (archived May 2019)](https://web.archive.org/web/20190512153239/http://sierrachest.com/index.php?a=engines&id=10) – "Titan 2.0, an update of the original Titan Engine"; "Games Using Titan 2.0… Caesar IV (September 2006) Tilted Mill Entertainment"; original Titan "used in… Empire Earth"; group members Caesar IV, Empire Earth
[^ref-14]: [MobyGames – Space Quest 0: Replicated](https://www.mobygames.com/game/11653/space-quest-0-replicated/) – this game (11653) and [Space Quest: The Lost Chapter](https://www.mobygames.com/game/54958/space-quest-the-lost-chapter/) (54958) are both members of MobyGames' AGI engine group 5313 (checked via the MobyGames API, 2026-10-16)
[^ref-15]: [PCGamingWiki – Engine: Darkstar](https://www.pcgamingwiki.com/wiki/Engine:Darkstar) – games: Starsiege (1999-03-24) and Starsiege: Tribes (1998-12-23)
[^ref-16]: [MobyGames – Code-Name: Iceman](https://www.mobygames.com/game/436/code-name-iceman/) – DOS 1989, Atari ST 1989 (API)
[^ref-17]: [MobyGames – Jones in the Fast Lane](https://www.mobygames.com/game/370/jones-in-the-fast-lane/) – DOS 1991 (API)
[^ref-18]: [MobyGames – Hoyle Classic Card Games](https://www.mobygames.com/game/30264/hoyle-classic-card-games/) – DOS, Windows, Macintosh 1993 (API); ScummVM lists it as sci:hoyle4
[^ref-19]: [MobyGames – IndyCar Racing II](https://www.mobygames.com/game/4082/indycar-racing-ii/) – DOS, Windows, Macintosh 1996 (API)
[^ref-20]: [Wikipedia – Caesar (video game)](https://en.wikipedia.org/wiki/Caesar_(video_game)) – released October 12, 1992; MobyGames 3146 also gives DOS/Amiga 1992
[^ref-21]: [Wikipedia – Caesar IV](https://en.wikipedia.org/wiki/Caesar_IV) – developer Tilted Mill Entertainment; "a three-dimensional game engine"
[^ref-22]: [Wikipedia – Emperor: Rise of the Middle Kingdom](https://en.wikipedia.org/wiki/Emperor:_Rise_of_the_Middle_Kingdom) – "the last of the series to use the same 2D-sprite game engine as seen in the earlier titles"
[^ref-23]: [ScummVM source – engines/gob/detection](https://github.com/scummvm/scummvm/tree/master/engines/gob/detection) – detection tables include tables_inca2.h and tables_dynasty.h; none for the first Inca
[^ref-24]: [Wikipedia – Tribes 2](https://en.wikipedia.org/wiki/Tribes_2) – infobox "engine = Torque"; [Torque (game engine)](https://en.wikipedia.org/wiki/Torque_(game_engine)): "originally developed by Dynamix for the 2001 first-person shooter Tribes 2"
[^ref-25]: [PC Games – IndyCar Racing 2 review by Bill Meyer, December 1995 issue (Wayback, Feb 1997)](https://web.archive.org/web/19970207065818/http://www.pcgamesmag.com/games/Dec95/indy1295.html) – filed under games/Dec95: "IndyCar Racing 2 picks up where its predecessors left off, adding a full-service garage, crisp Super VGA graphics"
[^ref-26]: [Wikipedia – Quest for Glory II: Trial by Fire](https://en.wikipedia.org/wiki/Quest_for_Glory_II:_Trial_by_Fire) – "The game's interface is a text parser"
[^ref-27]: [ScummVM source – engines/sci/detection.cpp](https://github.com/scummvm/scummvm/blob/master/engines/sci/detection.cpp) – under "SCI2.1 games": "hoyle5" "Hoyle Classic Games", "hoyle5bridge" "Hoyle Bridge", "hoyle5solitaire" "Hoyle Solitaire", "realm" "The Realm"
[^ref-28]: [ScummVM Wiki – ADL (archived May 2024)](http://web.archive.org/web/20240505215014/https://wiki.scummvm.org/index.php/ADL) – "ADL stands for 'Adventure Development Language'. It was created by Ken Williams"; "known as the Hi-Res Adventure series"; "Hi-Res Adventure #2 - Wizard and the Princess/Adventure in Serenia (1980)"

