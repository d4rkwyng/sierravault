---
title: "Audio and Music Technology"
type: technology
last_updated: "2026-05-12"
description: "Sierra's audio and music technology evolution: PC speaker → AdLib → Roland MT-32 → General MIDI → CD audio → orchestral scores. The technical and creative arc behind one of computer gaming's most ambitious music programs."
tags: [technology, audio, music, midi, mt-32, adlib, cd-audio]
---

# Audio and Music Technology

<small style="color: gray">Last updated: May 12, 2026</small>

## Overview

From 1980 PC-speaker beeps to 1995 Hollywood-orchestra scores recorded on CD-ROM, Sierra On-Line drove computer-game audio forward harder than any other publisher of its era. The company's investment in music — at one point reportedly the second-largest music-licensing budget in the entertainment software industry — produced a soundscape that defined a generation of adventure games and trained a generation of composers (Mark Seibert, Ken Allen, Robert Holmes, Ben Houge, Aubrey Hodges) for AAA work to follow.[^ref-1][^ref-2]

This page traces the eight-generation audio-tech arc from the 1980 Apple II through the late-1990s SCI32 CD-ROM era. For per-game audio specifics, see the individual game pages' Development → Voice Cast and Technical Achievements sections.

---

## Generation 1: PC speaker and Apple II tone (1980–1985)

**Hardware:** IBM PC internal speaker; Apple II built-in audio.
**Resolution:** Single-voice square wave, no polyphony, no envelopes.

Sierra's earliest titles used the most primitive audio available on the host platforms. The Apple II's built-in speaker could produce single-voice tones via tight assembly-language timing loops; the IBM PC's internal speaker was similar. Music was almost nonexistent — short jingles for game-over screens or simple bleeps for inventory pickup.[^ref-3]

Notable: Apple II GS (1986+) had a 15-voice Ensoniq sound chip that supported high-quality music, but Sierra's Apple II catalog largely predated wide GS adoption.[^ref-4]

## Generation 2: Tandy 3-voice + IBM PCjr (1984–1988)

**Hardware:** Tandy 1000 / IBM PCjr SN76489 chip — 3 square-wave voices plus white noise.
**AGI engine support:** Native Tandy/PCjr playback.

The IBM PCjr ([[Adventure Game Interpreter|AGI]]'s launch platform for [[1984 - King's Quest - Quest for the Crown|King's Quest]] in 1984) had a 3-voice TI SN76489 chip — a dramatic step up from a single PC speaker. The Tandy 1000 used the same chip, and AGI was designed to take advantage of it. Adventures like [[1986 - King's Quest III - To Heir Is Human|King's Quest III]] and [[1988 - King's Quest IV - The Perils of Rosella|King's Quest IV]] (AGI) shipped with Tandy-tuned music tracks alongside PC-speaker fallbacks.[^ref-5]

## Generation 3: AdLib (1987–1992)

**Hardware:** AdLib Music Synthesizer Card (Yamaha YM3812 OPL2 chip) — 9 FM-synthesis voices.
**SCI0 engine support:** Full AdLib music playback with multi-voice composition.

The AdLib card (released 1987) was the first widely-adopted PC audio card and became the de facto sound standard until the early 1990s. Its 9-voice FM-synthesis chip enabled actual music composition with chords, harmonies, and instrument variety.[^ref-6]

Sierra was an early and aggressive AdLib supporter. [[1988 - King's Quest IV - The Perils of Rosella|King's Quest IV (SCI)]] (1988) was widely cited as the first home computer game with a "Hollywood-orchestra-style score" specifically arranged for AdLib's instrument capabilities. The score was composed by William Goldstein (the Hollywood composer behind *Fame* and *Beverly Hills Cop III*) — at the time a remarkable departure for a computer-game publisher.[^ref-7]

Through 1989–1991, virtually every Sierra SCI release shipped with AdLib-optimized music: SQ3, KQ4, KQ5, PQ2, PQ3, LSL3, GK1, etc.[^ref-8]

## Generation 4: Roland MT-32 (1989–1994)

**Hardware:** Roland MT-32 LA Multi-Timbral Sound Module — 32-voice sample-based synth, 128 preset instruments, 30 percussion sounds.
**SCI0/SCI1/SCI1.1 engine support:** Full multi-channel routing.

The Roland MT-32 (1987) was the high-end audio standard for serious computer-music enthusiasts. At $550 retail it was expensive — but the audio quality was a generational leap beyond AdLib, with rich sampled instruments and proper polyphony.[^ref-9]

Sierra was, alongside LucasArts, the most aggressive MT-32 adopter. Many Sierra titles from 1989–1993 shipped with composer-arranged MT-32 tracks alongside the AdLib versions. The MT-32 ports of [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest V]], [[1991 - Space Quest IV - Roger Wilco and the Time Rippers|Space Quest IV]], [[1992 - King's Quest VI - Heir Today, Gone Tomorrow|King's Quest VI]], and [[1993 - Gabriel Knight - Sins of the Fathers|Gabriel Knight: Sins of the Fathers]] are considered some of the high points of pre-CD-audio computer-game music.[^ref-10]

The vault's individual game pages frequently note "MT-32 / AdLib / General MIDI" as the audio support matrix; this generation defined that standard.

## Generation 5: General MIDI (1991–1995)

**Hardware:** Sound Blaster Pro / 16, Roland Sound Canvas, and any GM-compliant device.
**SCI1.1 engine support:** General MIDI routing via internal mapping tables.

General MIDI (1991) standardized instrument assignments (program 1 = Acoustic Grand Piano, etc.) across audio devices, allowing a single MIDI file to play recognizably on any GM-compliant hardware. Sierra adopted GM as the primary mid-tier audio target for SCI1.1 releases.[^ref-11]

[[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest V (1990 CD-ROM)]], [[1991 - Space Quest IV - Roger Wilco and the Time Rippers|Space Quest IV (CD)]], [[1992 - Space Quest V - The Next Mutation|Space Quest V]], and [[1992 - Leisure Suit Larry V - Passionate Patti Does a Little Undercover Work|Leisure Suit Larry V]] all shipped with GM, MT-32, and AdLib music banks.[^ref-12]

## Generation 6: CD-ROM digital speech and audio (1991–1996)

**Hardware:** Sound Blaster Pro+/16/AWE32 with CD-ROM drive; later AC-97 chipsets.
**SCI1.1 / SCI2 engine support:** Streaming Red Book / digital speech.

The CD-ROM era unlocked two transformative capabilities:

1. **Full digital speech for every character line.** [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest V CD-ROM (1991)]] was Sierra's first major release with full voice acting throughout — a genre-defining moment.[^ref-13]
2. **Streaming Red Book audio for music.** Pre-recorded CD-quality music tracks replaced MIDI synthesis for the highest production-value scenes. [[1993 - Gabriel Knight - Sins of the Fathers|Gabriel Knight: Sins of the Fathers]] used recorded orchestral music for several key cutscenes.[^ref-14]

Voice acting became a significant production cost — Sierra established in-house voice recording facilities in Oakhurst and hired full-time voice directors. The Hollywood-talent recruitment that followed (Tim Curry, Cam Clarke, Jennifer Hale, Mark Hamill, Robby Benson, Christopher Lloyd in the 2015 reboot) traces back to this era's voice-budget investments.[^ref-15]

## Generation 7: Hollywood-orchestra recordings (1993–1996)

**Hardware:** Live orchestra recorded to CD; SCI2 streaming.

For the highest-profile titles, Sierra commissioned live-orchestra recordings:

- **[[1993 - Gabriel Knight - Sins of the Fathers|Gabriel Knight: Sins of the Fathers]]** (1993) — Robert Holmes's score, the first Sierra title widely cited as having a "feature-film-quality" score.[^ref-16]
- **[[1995 - The Beast Within - A Gabriel Knight Mystery|The Beast Within]]** (1995) — Robert Holmes; live orchestra, opera vocalists recorded.
- **[[1995 - Phantasmagoria|Phantasmagoria]]** (1995) — Mark Seibert; recorded chorus from the Skywalker Sound facilities.[^ref-17]
- **[[1998 - King's Quest - Mask of Eternity|King's Quest: Mask of Eternity]]** (1998) — Ben Houge, Kevin Manthei, Mark Seibert; combined orchestral and electronic. Inspired a 12-minute "Daventry Suite" orchestral tribute composition by Donald M. Wilson of Bowling Green State University.[^ref-18]

This era produced soundtracks that achieved cult status independent of the games themselves — *KQ6* and *Gabriel Knight* soundtracks have been re-released on streaming services and remain influential.[^ref-19]

## Generation 8: Modern re-release audio (1998–present)

**Hardware:** PCM 16-bit audio, MP3-encoded music, AAC; ScummVM digital playback.

Modern re-releases (GOG, Steam, ScummVM) replay the original SCI music files via software synthesis. ScummVM emulates the MT-32 (via Munt) and AdLib (via DOSBox) at higher accuracy than the original hardware. CD-Red-Book music tracks are re-encoded as MP3/OGG for modern distribution.[^ref-20]

Notable preservation efforts:

- **Munt** — Open-source MT-32 emulator, integrated into ScummVM and DOSBox.
- **DOSBox-X AdLib emulation** — High-accuracy YM3812 emulation.
- **ScummVM SCI music routing** — Plays original SCI music files through emulated or modern audio.

For [[2015 - King's Quest|King's Quest (2015)]] (Unreal Engine 3), the audio reverted to fully modern game-audio middleware (Wwise) with original orchestral recording — a stylistic return to the Hollywood-orchestra era of the late 1990s.[^ref-21]

---

## Notable Sierra composers

- **William Goldstein** — *King's Quest IV* (1988). The first Hollywood-name composer to score a Sierra game.
- **Mark Seibert** — Multiple. Worked on KQ5, KQ6, Phantasmagoria, Mask of Eternity. Later became Sierra's audio director.
- **[[Ken Allen]]** — *King's Quest V/VI*, *Quest for Glory*, *Conquests of Camelot*. One of the most prolific Sierra composers of the early 1990s.
- **[[Robert Holmes]]** — *Gabriel Knight 1/2/3*, *Gray Matter*. Jane Jensen's husband and longtime musical collaborator.
- **Aubrey Hodges** — *Quest for Glory III/IV*. Dark atmospheric work for Aaron Lerner's environments.
- **Ben Houge, Kevin Manthei** — *Mask of Eternity* (1998).
- **Chance Thomas** — *King's Quest VIII* and later (Unreal-era).

Many Sierra composers went on to AAA careers (Aubrey Hodges to DOOM 64, Mark Seibert to Sony, Chance Thomas to *Lord of the Rings Online*).[^ref-22]

---

## Audio in modern preservation

For users running classic Sierra games today via [[ScummVM]] or DOSBox:

- **AGI titles** — PC speaker, Tandy, and AdLib renditions all supported; AdLib emulation is the recommended default.
- **SCI0–SCI1.1 titles** — All four audio modes (PC speaker, AdLib, MT-32, General MIDI) supported. MT-32 via Munt produces the highest audio quality; install Munt separately for ScummVM integration.[^ref-23]
- **SCI2/SCI32 titles** — Original MIDI + Red Book audio tracks supported.
- **CD-ROM games** — Original speech tracks supported in their original form.

The recommended setup for music-purist players: ScummVM + Munt + original MT-32 ROMs (legally extracted from hardware) for SCI music; original CD-ROM speech tracks for digital audio.[^ref-24]

---

## See Also

- [[Adventure Game Interpreter]] — AGI engine audio architecture
- [[Sierra Creative Interpreter]] — SCI engine audio architecture
- [[Technology/ScummVM|ScummVM]] — Modern audio playback for original game music
- [[Reference/Engine History|Engine History]] — Engine generations correlated to audio capabilities
- [[Ken Allen]], [[Mark Seibert]], [[Robert Holmes]] — Designer profiles for the major composers

## References

[^ref-1]: [The Digital Antiquarian — Sierra audio budgets](https://www.filfre.net/?s=Sierra+audio) — Music-licensing budget context
[^ref-2]: [Adventure Classic Gaming — Sierra music retrospective](http://www.adventureclassicgaming.com/index.php/site/features/sierra-music/) — Composer profiles
[^ref-3]: [Wikipedia — PC speaker](https://en.wikipedia.org/wiki/PC_speaker) — Technical limits
[^ref-4]: [Wikipedia — Apple IIGS](https://en.wikipedia.org/wiki/Apple_IIGS) — Ensoniq audio chip
[^ref-5]: [Wikipedia — Texas Instruments SN76489](https://en.wikipedia.org/wiki/Texas_Instruments_SN76489) — Tandy/PCjr audio chip
[^ref-6]: [Wikipedia — AdLib (audio card)](https://en.wikipedia.org/wiki/Ad_Lib,_Inc.) — OPL2 chip, market adoption
[^ref-7]: [Wikipedia — King's Quest IV: The Perils of Rosella](https://en.wikipedia.org/wiki/King%27s_Quest_IV) — William Goldstein score documentation
[^ref-8]: [VOGONS — Sierra AdLib title list](https://www.vogons.org) — Community-documented audio support
[^ref-9]: [Wikipedia — Roland MT-32](https://en.wikipedia.org/wiki/Roland_MT-32) — Specifications, retail price
[^ref-10]: [Sierra Help — Sierra Audio Setup](https://wiki.sierrahelp.com/index.php/Sierra_Audio) — Per-title audio support matrix
[^ref-11]: [Wikipedia — General MIDI](https://en.wikipedia.org/wiki/General_MIDI) — Standardization history
[^ref-12]: [MobyGames — Sierra music credits](https://www.mobygames.com/company/3/sierra-entertainment-inc/) — Composer credits across the catalog
[^ref-13]: [Wikipedia — King's Quest V](https://en.wikipedia.org/wiki/King%27s_Quest_V) — First Sierra CD-ROM speech
[^ref-14]: [Wikipedia — Gabriel Knight: Sins of the Fathers](https://en.wikipedia.org/wiki/Gabriel_Knight:_Sins_of_the_Fathers) — Music production details
[^ref-15]: [Sierra Gamers — Voice cast oral histories](https://www.sierragamers.com) — Voice-actor recruitment stories
[^ref-16]: [Robert Holmes — Official site](https://www.robertholmes.com) — Composer site (linked from Pinkerton Road)
[^ref-17]: [Wikipedia — Phantasmagoria](https://en.wikipedia.org/wiki/Phantasmagoria_(1995_video_game)) — Music production at Skywalker Sound
[^ref-18]: [GameSpot — Daventry Suite tribute composition](https://www.gamespot.com/articles/kings-quest-inspires-tune/1100-2446807/) — Donald M. Wilson orchestral tribute
[^ref-19]: [VGMdb — Sierra On-Line soundtracks](https://vgmdb.net) — Soundtrack release database
[^ref-20]: [Munt — MT-32 emulator](https://github.com/munt/munt) — Open-source MT-32 emulator project
[^ref-21]: [Wwise — King's Quest 2015 case study](https://www.audiokinetic.com/customers/the-odd-gentlemen-kings-quest/) — Modern audio middleware adoption
[^ref-22]: [MobyGames — Aubrey Hodges credits](https://www.mobygames.com/person/aubrey-hodges/) — Post-Sierra AAA career
[^ref-23]: [ScummVM Wiki — MT-32 setup](https://wiki.scummvm.org/index.php?title=MT-32) — Munt integration guide
[^ref-24]: [PCGamingWiki — Sierra audio fixes](https://www.pcgamingwiki.com/wiki/Roland_MT-32) — Modern setup guidance
[^ref-25]: [The Digital Antiquarian — King's Quest IV music](https://www.filfre.net/2018/01/sierra-at-the-cusp-of-the-multimedia-age/) — Music-budget and Hollywood-composer context
