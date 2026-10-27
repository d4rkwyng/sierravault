---
title: "Audio and Music Technology"
type: technology
last_updated: "2026-10-26"
description: "Sierra's audio and music technology evolution: PC speaker → Tandy → AdLib → Roland MT-32 → General MIDI → CD audio → recorded scores. The technical and creative arc behind Sierra's music program."
tags: [technology, audio, music, midi, mt-32, adlib, cd-audio]
---

# Audio and Music Technology

<small style="color: gray">Last updated: October 26, 2026</small>

## Overview

From Apple II tones in 1980 to live-recorded CD-ROM scores in the mid-1990s, Sierra On-Line invested heavily in game audio. It secured a deal to distribute the Roland MT-32 in the US and hired professional composers to write in-game music.[^ref-9] Its staff composers and music directors included Mark Seibert, Ken Allen, Robert Holmes, Aubrey Hodges and Chance Thomas;[^ref-32][^ref-36][^ref-16][^ref-37][^ref-31] Hodges and Thomas later went on to *Doom 64* and *The Lord of the Rings Online*.[^ref-22][^ref-31]

This page traces the audio-tech arc from the 1980 Apple II through the late-1990s CD-ROM era. For per-game audio specifics, see the individual game pages.

---

## Generation 1: PC speaker and Apple II tone (1980–1985)

**Hardware:** Apple II built-in audio; IBM PC internal speaker (the IBM PC was released in 1981).[^ref-41]
**Resolution:** On the PC, a single-voice square wave with no envelopes; Apple II multi-voice music had to be produced entirely in software.

Sierra's earliest titles used the most primitive audio available on the host platforms. The Apple II had only a "toggle circuit that could only emit a click through a built-in speaker"; any music, including two-, three- and eventually four-voice music, was "generated entirely by software that clicked the speaker at just the right times."[^ref-50] The IBM PC's internal speaker produced a square wave;[^ref-3] as Ken Williams put it in 1988, the PC buzzer could only "make one note at a time, which has no attack or decay."[^ref-26]

Notable: the Apple IIGS (1986) had a 15-voice Ensoniq sound chip that supported much richer music.[^ref-4]

## Generation 2: Tandy 3-voice + IBM PCjr (1984–1993)

**Hardware:** Tandy 1000 / IBM PCjr SN76489 chip — 3 square-wave voices plus white noise.[^ref-5] Ken Williams in 1988: "The Tandy 1000 is slightly better with three simultaneous notes."[^ref-26]
**AGI engine support:** Native Tandy/PCjr playback.

The IBM PCjr ([[Adventure Game Interpreter|AGI]]'s launch platform for [[1984 - King's Quest - Quest for the Crown|King's Quest]] in 1984) had a 3-voice TI SN76489 chip — a dramatic step up from a single PC speaker. The Tandy 1000 used the same chip.[^ref-5] AGI games such as [[1986 - King's Quest III - To Heir Is Human|King's Quest III]] supported Tandy/PCjr sound alongside the PC speaker.[^ref-35] Support continued well into the SCI era: MobyGames' DOS specs still list Tandy/PCjr sound for [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest V]], [[1991 - Space Quest IV - Roger Wilco and the Time Rippers|Space Quest IV]] and [[1993 - Space Quest V - The Next Mutation|Space Quest V]] (1993).[^ref-44][^ref-45][^ref-12]

## Generation 3: AdLib (1987–1992)

**Hardware:** AdLib Music Synthesizer Card (Yamaha YM3812 OPL2 chip) — 9 FM-synthesis voices.[^ref-6][^ref-48]
**SCI0 engine support:** AdLib music playback with multi-voice composition.

The AdLib card (released 1987) was the first add-on sound card for IBM compatibles to achieve widespread acceptance and became the first de facto standard for PC audio, until the Sound Blaster overshadowed it.[^ref-6] Sierra struck deals with both Roland and AdLib and wrote music for the AdLib and the MT-32 starting with *King's Quest IV*.[^ref-47] The card's chip offered nine melodic FM voices,[^ref-48] enough for chords, harmonies and varied instruments. The Digital Antiquarian gives its launch price as $245.[^ref-27]

The AdLib was not the card [[1988 - King's Quest IV - The Perils of Rosella|King's Quest IV (SCI)]]'s score was written for — that was the MT-32 (see below) — but Sierra "duly added Ad Lib support to King's Quest IV and all the other SCI games before they shipped."[^ref-27] From then on, SCI releases routinely listed AdLib among their supported devices.[^ref-10][^ref-34][^ref-12]

Creative's Sound Blaster, released in 1989, used the same YM3812 chip and "provided compatibility with the market leader AdLib sound card"; *Compute!* called the opening music of [[1989 - Space Quest III - The Pirates of Pestulon|Space Quest III]] on the card "extraordinary".[^ref-49]

## Generation 4: Roland MT-32 (1988–1993)

**Hardware:** Roland MT-32 Multi-Timbre Sound Module — LA synthesis (samples for attacks and drums, synthesis for the sustain), 32 partials giving 8 to 32 simultaneous notes, 128 preset synth sounds and 30 rhythm sounds.[^ref-9]
**SCI0/SCI1/SCI1.1 engine support:** Full multi-channel routing.

The Roland MT-32 (1987) had an original list price of $695; Sierra sold it bundled with the necessary MPU-401 interface for $550.[^ref-9]

[[1988 - King's Quest IV - The Perils of Rosella|King's Quest IV]] (1988) was the first Sierra title with a complete musical soundtrack scored on the MT-32.[^ref-9] Its composer was William Goldstein, "known for his previous work on the TV series Fame, the Touchstone Pictures film Hello Again," and Sierra's Winter 1988 newsletter promised "Forty minutes of original music."[^ref-26][^ref-7] The Digital Antiquarian calls it "a full-fledged musical score, arguably the first such ever to be written for a computer game," and notes that KQ4 "heralded the arrival of the new, more flexible SCI game engine, along with full orchestral soundtracks for those with the hardware to hear them."[^ref-27][^ref-25]

MobyGames' DOS tech specs list MT-32 support for [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest V]], [[1991 - Space Quest IV - Roger Wilco and the Time Rippers|Space Quest IV]], [[1992 - King's Quest VI - Heir Today, Gone Tomorrow|King's Quest VI]], and [[1993 - Gabriel Knight - Sins of the Fathers|Gabriel Knight: Sins of the Fathers]], among others.[^ref-44][^ref-45][^ref-33][^ref-34]

The vault's individual game pages frequently note "MT-32 / AdLib / General MIDI" as the audio support matrix.

## Generation 5: General MIDI (1991–1995)

**Hardware:** Roland Sound Canvas, a Sound Blaster 16 with the Wave Blaster wavetable daughterboard, and other GM-compliant devices. The Sound Blaster cards' own music chips were FM synthesizers (OPL2/OPL3), so MobyGames lists General MIDI separately from Sound Blaster.[^ref-11][^ref-49][^ref-24][^ref-33]

General MIDI, first published in 1991, standardized instrument assignments (program 1 = Acoustic Grand Piano, etc.) across audio devices, allowing a single MIDI file to play recognizably on any GM-compliant hardware. Roland's Sound Canvas line, introduced the same year, was its first General MIDI synth module.[^ref-11]

General MIDI appears in Sierra's tech specs from 1992: MobyGames lists GM alongside MT-32 and AdLib for [[1992 - King's Quest VI - Heir Today, Gone Tomorrow|King's Quest VI]] (1992), [[1993 - Space Quest V - The Next Mutation|Space Quest V]] (1993) and [[1993 - Gabriel Knight - Sins of the Fathers|Gabriel Knight]] (1993).[^ref-33][^ref-12][^ref-34] Earlier titles such as King's Quest V and Space Quest IV list MT-32 and AdLib but not General MIDI.[^ref-44][^ref-45]

## Generation 6: CD-ROM digital speech and audio (1991–1996)

**Hardware:** Sound Blaster Pro/16/AWE32 with CD-ROM drive.
**SCI1 onward:** Digital speech and CD audio; the CD versions of Mixed-Up Mother Goose and King's Quest V were SCI1 builds.[^ref-51]

The CD-ROM era unlocked two transformative capabilities:

1. **Digital speech for character lines.** [[1990 - King's Quest V - Absence Makes the Heart Go Yonder|King's Quest V]] was later released as a fully voiced "talkie" CD-ROM, voiced by members of the Sierra staff.[^ref-13]
2. **Red Book audio for music.** Composer Ken Allen recalled: "I'm fairly sure we were the first to use redbook audio in a CD-ROM game; it was Mixed Up Mother Goose" — the CD-ROM edition of the game's VGA update ("Previously we'd updated the game to VGA resolution").[^ref-43]

Voice acting became a significant production task. In 1992 Sierra's InterAction magazine described Mark Seibert as "Music Director and head of Sierra's professional in-house recording studio," in charge of "recruiting and recording all the vocal talent, in cooperation with the director of the specific game."[^ref-15] Professional actors followed: Robby Benson voiced Prince Alexander in King's Quest VI;[^ref-40] Tim Curry and Mark Hamill were in the CD-ROM cast of Gabriel Knight;[^ref-14] and Christopher Lloyd voiced King Graham in the 2015 reboot.[^ref-39]

## Generation 7: Recorded scores (1995–1998)

**Hardware:** Recorded music on CD; SCI2 streaming.

For some of its highest-profile CD-ROM titles, Sierra moved from computer-generated music toward recorded scores:

- **[[1995 - Phantasmagoria|Phantasmagoria]]** (1995) — Mark Seibert and Jay Usher; unlike previous Sierra games the score was recorded live, mixing real instruments with synthesized and sampled sounds. The opening theme's neo-Gregorian chant was performed by a 135-voice choir.[^ref-17]
- **[[1995 - The Beast Within - A Gabriel Knight Mystery|The Beast Within]]** (1995) — Robert Holmes with Jay Usher; Holmes also wrote the music for a scene from the game's fictional opera, "Der Fluch Des Engelhart."[^ref-29]
- **[[1998 - King's Quest - Mask of Eternity|King's Quest: Mask of Eternity]]** (1998) — Ben Houge, Kevin Manthei, Mark Seibert. Their soundtrack inspired the 12-minute *Daventry Suite* by Donald M. Wilson, premiered by the Bowling Green State University Fall Wind Ensemble.[^ref-18]
- **[[1998 - Quest for Glory V - Dragon Fire|Quest for Glory V: Dragon Fire]]** (1998) — Chance Thomas, hired as Sierra's full-time composer in 1996; the soundtrack was released on CD.[^ref-31][^ref-42]

Some of this music has since been revisited: *A Simple Refrain* presents Robert Holmes's themes from the Gabriel Knight games, Gray Matter and Moebius as solo-piano pieces performed by Roger Hooper.[^ref-46]

## Generation 8: Modern re-release audio (1998–present)

**Playback:** Emulated sound devices in ScummVM.[^ref-24]

ScummVM can emulate the MT-32, provided the player supplies the original MT-32 ROMs, and offers MAME, DOSBox and Nuked OPL emulators for AdLib music.[^ref-24]

Notable preservation efforts:

- **Munt** — Open-source library that emulates "(approximately)" the Roland MT-32, CM-32L and LAPC-I; the project also ships a patch for the official DOSBox 0.74 release.[^ref-20]
- **ScummVM SCI music routing** — Plays original SCI music files through emulated or modern audio.[^ref-24]

For [[2015 - King's Quest|King's Quest (2015)]] (Unreal Engine 3), The Odd Gentlemen's score was written by Ben and David Stanton; David Stanton described how the original games inspired it in a 2015 behind-the-scenes video.[^ref-21][^ref-39]

---

## Notable Sierra composers

- **William Goldstein** — *King's Quest IV* (1988). Known for the TV series *Fame* and the Touchstone film *Hello Again*.[^ref-26]
- **[[Mark Seibert]]** — Hired as a musician and music editor on *King's Quest IV*, promoted to music director after a few years, and to producer in 1992. Co-composed *Phantasmagoria* with Jay Usher; Mask of Eternity.[^ref-32][^ref-17]
- **[[Ken Allen]]** — *The Colonel's Bequest*, *King's Quest V*, *Space Quest IV*, *Conquests of the Longbow*, *Jones in the Fast Lane*, among others.[^ref-36]
- **[[Robert Holmes]]** — *Gabriel Knight: Sins of the Fathers*; *The Beast Within* with Jay Usher; his themes underpin David Henry's *Gabriel Knight 3* score. Later *Gray Matter*.[^ref-16][^ref-29][^ref-30]
- **Aubrey Hodges** — *Quest for Glory IV* and most of the *Freddy Pharkas* score.[^ref-37][^ref-38]
- **Ben Houge, Kevin Manthei** — *Mask of Eternity* (1998), with Seibert.[^ref-18]
- **Chance Thomas** — *Quest for Glory V* (1998).[^ref-31]

Several went on to long careers outside Sierra: Aubrey Hodges composed *Doom 64*, and Chance Thomas scored *The Lord of the Rings Online*.[^ref-22][^ref-31]

---

## Audio in modern preservation

For users running classic Sierra games today via [[ScummVM]] or DOSBox:

- **AGI titles** — Original DOS releases supported the PC speaker and Tandy/PCjr sound.[^ref-35]
- **SCI0–SCI1.1 titles** — PC speaker, AdLib and MT-32 are the common options; General MIDI appears only from about 1992 onward (see Generation 5).[^ref-10][^ref-33] ScummVM's built-in MT-32 emulation needs the original ROMs.[^ref-24]
- **SCI2/SCI32 titles** — Original MIDI + Red Book audio tracks supported.
- **CD-ROM games** — Original speech tracks supported in their original form.

The recommended setup for music-purist players: ScummVM's built-in MT-32 emulation, which requires the original MT-32 ROMs taken from the player's own module, for SCI music; original CD-ROM speech tracks for digital audio.[^ref-24]

---

## See Also

- [[Adventure Game Interpreter]] — AGI engine audio architecture
- [[Sierra Creative Interpreter]] — SCI engine audio architecture
- [[ScummVM|ScummVM]] — Modern audio playback for original game music
- [[Engine History|Engine History]] — Engine generations correlated to audio capabilities
- [[Ken Allen]], [[Mark Seibert]], [[Robert Holmes]] — Designer profiles for the major composers

## References

[^ref-3]: [Wikipedia — PC speaker](https://en.wikipedia.org/wiki/PC_speaker) — Technical limits
[^ref-4]: [Wikipedia — Apple IIGS](https://en.wikipedia.org/wiki/Apple_IIGS) — Ensoniq audio chip, "15-voice"
[^ref-5]: [Wikipedia — Texas Instruments SN76489](https://en.wikipedia.org/wiki/Texas_Instruments_SN76489) — Tandy/PCjr audio chip
[^ref-6]: [Wikipedia — Ad Lib, Inc.](https://en.wikipedia.org/wiki/Ad_Lib,_Inc.) — "The AdLib card consisted of a YM3812 chip"; widespread acceptance; overshadowed by the Sound Blaster
[^ref-7]: [Wikipedia — King's Quest IV: The Perils of Rosella](https://en.wikipedia.org/wiki/King%27s_Quest_IV) — William Goldstein score, 40 minutes of music
[^ref-9]: [Wikipedia — Roland MT-32](https://en.wikipedia.org/wiki/Roland_MT-32) — $695 list price; $550 from Sierra with MPU-401; 32 partials, 8–32 notes; Sierra US distribution deal; KQ4 first Sierra MT-32 score
[^ref-10]: [MobyGames — King's Quest IV tech specs](https://www.mobygames.com/game/129/kings-quest-iv-the-perils-of-rosella/specs/) — DOS: AdLib, Game Blaster, IBM Music Feature, PC speaker, MT-32, Tandy/PCjr; no General MIDI (MobyGames API, checked 2026-10-16)
[^ref-11]: [Wikipedia — General MIDI](https://en.wikipedia.org/wiki/General_MIDI) — "first published in 1991"; Sound Canvas as Roland's first GM module
[^ref-12]: [MobyGames — Space Quest V tech specs](https://www.mobygames.com/game/144/space-quest-v-the-next-mutation/specs/) — DOS (1993): AdLib, General MIDI, MT-32, Tandy/PCjr and others (read via the MobyGames API, checked 2026-10-26)
[^ref-13]: [Wikipedia — King's Quest V](https://en.wikipedia.org/wiki/King%27s_Quest_V) — "later released as a fully voiced 'talkie' CD-ROM, done by members of the Sierra staff"
[^ref-14]: [Wikipedia — Gabriel Knight: Sins of the Fathers](https://en.wikipedia.org/wiki/Gabriel_Knight:_Sins_of_the_Fathers) — CD-ROM voice cast (Tim Curry, Mark Hamill)
[^ref-15]: [InterAction Magazine, Vol. V No. 2, Summer 1992](https://archive.org/details/InterAction_Magazine_Vol._V_Number_2_Summer_1992_1992_Sierra_On-Line_US) — Period scan: "Mark Seibert, Music Director and head of Sierra's professional in-house recording studio"
[^ref-16]: [Robert Holmes — Biography](https://robertholmesmusic.com/biography/) — Joined Sierra's composer group; work included Gabriel Knight 1–3, Gray Matter, Moebius
[^ref-17]: [Wikipedia — Phantasmagoria (video game)](https://en.wikipedia.org/wiki/Phantasmagoria_(video_game)) — Seibert and Usher score, recorded live, 135-voice choir
[^ref-18]: [GameSpot — King's Quest Inspires Tune](https://www.gamespot.com/articles/kings-quest-inspires-tune/1100-2446807/) — 12-minute Daventry Suite by Donald M. Wilson, BGSU Fall Wind Ensemble; tribute to Manthei, Houge and Seibert
[^ref-20]: [Munt — MT-32 emulator](https://github.com/munt/munt) — Emulates "(approximately)" the MT-32; DOSBox-mt32-patch for DOSBox v.0.74
[^ref-21]: [Activision Blog — Behind-the-Scenes: The Music of King's Quest](https://blog.activision.com/more-games/archives/behind-the-scenes-the-music-of-kings-quest) — "composer David Stanton explains how the original games ... have inspired King's Quest's score"
[^ref-22]: [Wikipedia — Doom 64](https://en.wikipedia.org/wiki/Doom_64) — "music and sound effects were composed by Aubrey Hodges"
[^ref-24]: [ScummVM Documentation — Understanding the audio settings](https://docs.scummvm.org/en/latest/advanced_topics/understand_audio.html) — MT-32 emulation needs original ROMs; MAME, DOSBox and Nuked AdLib emulators
[^ref-25]: [The Digital Antiquarian — Sierra at the Cusp of the Multimedia Age](https://www.filfre.net/2018/01/sierra-at-the-cusp-of-the-multimedia-age/) — KQ4 "heralded ... full orchestral soundtracks for those with the hardware to hear them"
[^ref-26]: [Sierra Newsletter, Winter 1988 (mocagh)](https://www.mocagh.org/sierra/sierranews-winter88.pdf) — Period source: PC buzzer "one note at a time"; "The Tandy 1000 is slightly better with three simultaneous notes"; Goldstein "known for his previous work on the TV series Fame, the Touchstone Pictures film Hello Again"; "Forty minutes of original music"
[^ref-27]: [The Digital Antiquarian — Sierra Gets Creative](https://www.filfre.net/2016/08/sierra-gets-creative/) — KQ4 score "arguably the first such"; Ad Lib at $245; "added Ad Lib support to King's Quest IV and all the other SCI games"
[^ref-29]: [Wikipedia — The Beast Within: A Gabriel Knight Mystery](https://en.wikipedia.org/wiki/The_Beast_Within:_A_Gabriel_Knight_Mystery) — Soundtrack by Holmes "alongside Jay Usher"; music for the fictional opera
[^ref-30]: [Wikipedia — Gabriel Knight 3](https://en.wikipedia.org/wiki/Gabriel_Knight_3:_Blood_of_the_Sacred,_Blood_of_the_Damned) — "score was composed by David Henry, based on themes created by ... Robert Holmes"
[^ref-31]: [Wikipedia — Chance Thomas](https://en.wikipedia.org/wiki/Chance_Thomas) — Joined Sierra as full-time composer in 1996; Quest for Glory V; later The Lord of the Rings Online
[^ref-32]: [Wikipedia — Mark Seibert](https://en.wikipedia.org/wiki/Mark_Seibert) — Musician and music editor on KQ IV; music director; producer from 1992
[^ref-33]: [MobyGames — King's Quest VI tech specs](https://www.mobygames.com/game/131/kings-quest-vi-heir-today-gone-tomorrow/specs/) — DOS: AdLib, General MIDI, MT-32 and others (MobyGames API, checked 2026-10-16)
[^ref-34]: [MobyGames — Gabriel Knight: Sins of the Fathers tech specs](https://www.mobygames.com/game/116/gabriel-knight-sins-of-the-fathers/specs/) — DOS: AdLib, General MIDI, MT-32, Gravis Ultrasound and others (MobyGames API, checked 2026-10-16)
[^ref-35]: [MobyGames — King's Quest III tech specs](https://www.mobygames.com/game/126/kings-quest-iii-to-heir-is-human/specs/) — DOS: PC Speaker, Tandy/PCjr (MobyGames API, checked 2026-10-16)
[^ref-36]: [MobyGames — Ken Allen credits (Wayback, February 2024)](https://web.archive.org/web/20240213112141/https://www.mobygames.com/person/273/ken-allen/credits/) — Colonel's Bequest, KQ V, SQ IV, Conquests of the Longbow, Jones in the Fast Lane
[^ref-37]: [Wikipedia — Quest for Glory IV: Shadows of Darkness](https://en.wikipedia.org/wiki/Quest_for_Glory_IV:_Shadows_of_Darkness) — Composer Aubrey Hodges
[^ref-38]: [Al Lowe — Music from Freddy Pharkas](https://allowe.com/games/fpfp/music-freddy.html) — "All the rest of the rather extensive musical score was written by Aubrey Hodges"
[^ref-39]: [Wikipedia — King's Quest (2015 video game)](https://en.wikipedia.org/wiki/King%27s_Quest_(2015_video_game)) — Christopher Lloyd as King Graham; composers Ben and David Stanton; Unreal Engine 3
[^ref-40]: [Wikipedia — King's Quest VI](https://en.wikipedia.org/wiki/King%27s_Quest_VI) — "Robby Benson provided the voice for Prince Alexander"
[^ref-41]: [Wikipedia — IBM Personal Computer](https://en.wikipedia.org/wiki/IBM_Personal_Computer) — Released August 12, 1981
[^ref-42]: [Wikipedia — Quest for Glory V: Dragon Fire](https://en.wikipedia.org/wiki/Quest_for_Glory_V:_Dragon_Fire) — Soundtrack by Chance Thomas, "released on CD"
[^ref-43]: [Guys from Andromeda Podcast — Ken Allen](https://guysfromandromeda.com/blog/podcast-episode-3-guest-host-ken-allen/) — "fairly sure we were the first to use redbook audio in a CD-ROM game; it was Mixed Up Mother Goose"
[^ref-44]: [MobyGames — King's Quest V tech specs](https://www.mobygames.com/game/130/kings-quest-v-absence-makes-the-heart-go-yonder/specs/) — DOS: AdLib, MT-32, Sound Blaster, Tandy/PCjr and others; no General MIDI (read via the MobyGames API, checked 2026-10-26)
[^ref-45]: [MobyGames — Space Quest IV tech specs](https://www.mobygames.com/game/143/space-quest-iv-roger-wilco-and-the-time-rippers/specs/) — DOS: AdLib, MT-32, Sound Blaster, Tandy/PCjr and others; no General MIDI (read via the MobyGames API, checked 2026-10-26)
[^ref-47]: [Quest Studios — The History of PC Game MIDI, by Eric Wing (Wayback, September 2014)](https://web.archive.org/web/20140904211309/http://queststudios.com/quest/midi.html) — "They would compose music for these units starting with King's Quest 4"
[^ref-48]: [Wikipedia — Yamaha OPL](https://en.wikipedia.org/wiki/Yamaha_OPL) — YM3812 (OPL2): "Melody polyphony is limited to nine voices in melodic mode"
[^ref-49]: [Wikipedia — Sound Blaster](https://en.wikipedia.org/wiki/Sound_Blaster) — Released 1989 with the YM3812; "compatibility with the market leader AdLib"; Compute! on Space Quest III: "extraordinary"; Wave Blaster wavetable daughterboard
[^ref-50]: [Wikipedia — Apple II](https://en.wikipedia.org/wiki/Apple_II) — "toggle circuit that could only emit a click"; multi-voice music "generated entirely by software"
[^ref-51]: [ScummVM Wiki — Sierra Game Versions (Wayback, May 2024)](http://web.archive.org/web/20240518064410/https://wiki.scummvm.org/index.php/Sierra_Game_Versions) — Mixed-Up Mother Goose (CD Version) under SCI1 (early); King's Quest V (CD Version) under SCI1 (late)
[^ref-46]: [Bandcamp — A Simple Refrain: The Game Themes of Robert Holmes](https://robertholmessoundtracks.bandcamp.com/album/a-simple-refrain-the-game-themes-of-robert-holmes) — Solo-piano versions by Roger Hooper of GK1–3, Gray Matter and Moebius themes
