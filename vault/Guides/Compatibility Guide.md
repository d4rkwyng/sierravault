---
title: "Patch & Compatibility Guide"
type: guide
last_updated: "2026-10-16"
---
# Patch & Compatibility Guide

<small style="color: gray">Last updated: October 16, 2026</small>

This guide highlights essential fixes, installers, and configuration tips for running Sierra-era games on modern systems. Combine these with the [[Platform Guide|Platform Guide]] and [[Buying Guide|Buying Guide]] for best results.

## Essential Sources
- [SierraHelp.com](https://sierrahelp.com/) – Community-made installers that set games up in DOSBox or ScummVM, plus official and third-party patch mirrors for a long list of Sierra releases.[^ref-18][^ref-20]
- [ScummVM](https://www.scummvm.org/) – Preferred runtime for AGI/SCI games; includes fixes for original game bugs.[^ref-1][^ref-4]
- [DOSBox Staging](https://www.dosbox-staging.org/) – Modern DOSBox fork with enhanced features for games not supported by ScummVM.[^ref-11]
- [SpaceQuest.net](https://spacequest.net/) – Series-specific fixes for *Space Quest* releases.
- [QuestForMoreGlory.com (archived)](https://web.archive.org/web/20240322150642/http://www.questformoreglory.com/) – *Quest for Glory* game help, downloads, new installers, and 64-bit patches for *Quest for Glory V*.[^ref-29]

## Steam Deck Compatibility

The Steam Deck provides excellent compatibility for Sierra games through multiple methods:

### ScummVM on Steam Deck
The **recommended approach** for most Sierra adventure games. ScummVM is available through:
- **Flathub** (Desktop Mode): `flatpak install flathub org.scummvm.ScummVM`[^ref-12]
- **Discover Store**: Search "ScummVM" in Desktop Mode's Discover app
- **EmuDeck**: Includes ScummVM as part of its retro gaming suite[^ref-14]

**Setup tips:**
1. Install ScummVM via Flatpak in Desktop Mode
2. Copy game files to `/home/deck/Games/ScummVM/` or similar accessible location
3. Add games to ScummVM, then add ScummVM as a non-Steam game
4. Configure controller mappings in Steam Input (ScummVM supports gamepad natively)
5. Use ScummVM's built-in "Stretch to fit" for proper display on the Deck's 1280×800 screen[^ref-17]

### DOSBox on Steam Deck
For DOS-based Sierra games not supported by ScummVM (flight sims, strategy games):
- **DOSBox Staging** – Available via Flathub (`io.github.dosbox-staging`)[^ref-13]
- **RetroDECK** – Runs DOS games through RetroArch's DOSBox Pure core[^ref-15]
- GOG and Steam installers generally work through Proton

### Proton/Wine for Windows Versions
For Windows 95/98 Sierra titles:
- Most SierraHelp installers work with **Proton Experimental** or **GE-Proton**
- Use the `PROTON_USE_WINED3D=1 %command%` launch option to switch from DXVK to the OpenGL-based wined3d renderer for older DirectX games[^ref-16]
- *3-D Ultra* series and Dynamix Windows games often need dgVoodoo2 bundled

### Sierra Game Compatibility Summary (Steam Deck)

| Game Type | Method | Notes |
|-----------|--------|-------|
| AGI Games (KQ I–IV, SQ I–II, LSL 1) | ScummVM | Rated "Good" (KQ II "Excellent")[^ref-1] |
| SCI16 Games (KQ V–VI, SQ III–V) | ScummVM | Rated "Excellent"[^ref-1] |
| SCI32 Games (KQ VII, GK1, Phantasmagoria) | ScummVM | GK1 "Excellent"; KQ VII and Phantasmagoria "Good"[^ref-1] |
| DOS Simulations (Aces, Red Baron) | DOSBox Staging | Joystick config needed |
| Windows 95/98 Titles | Proton + dgVoodoo2 | Varies by title |

## ScummVM Version & Engine Support

**Current stable version:** Check [scummvm.org](https://www.scummvm.org/) for the latest release
- [Download page](https://www.scummvm.org/downloads/)
- [Compatibility list](https://www.scummvm.org/compatibility/)

### Sierra-Specific Engines
ScummVM provides dedicated engines for Sierra games, with compatibility ratings of **Good** to **Excellent** on its compatibility list:[^ref-1]

**AGI Engine** – Sierra's Adventure Game Interpreter (1984–1989; 14 games)[^ref-9] – all rated "Good" except *King's Quest II* ("Excellent"):[^ref-1]
- *King's Quest I–IV*
- *Space Quest I–II*
- *Leisure Suit Larry 1* (original)
- *Police Quest 1* (original)
- *Manhunter 1–2*
- *Gold Rush!*
- *Mixed-Up Mother Goose* (original)

**SCI Engine** – Sierra's Creative Interpreter (1988–1996):[^ref-10]
- *King's Quest I* SCI remake, *King's Quest IV* (SCI version), *King's Quest V–VII* (KQ7 rated "Good")
- *Space Quest I* VGA remake, *Space Quest III–VI* (SQ6 rated "Good")
- *Leisure Suit Larry 1* VGA remake, *Leisure Suit Larry 2–7*
- *Police Quest 1* VGA remake, *Police Quest 2–4* (PQ4 rated "Good")
- *Police Quest: SWAT* (Good rating)
- *Quest for Glory I–IV* (including the QFG1 VGA remake)
- *Gabriel Knight 1* and *The Beast Within: A Gabriel Knight Mystery* (GK2)
- *Laura Bow 1–2*
- *Conquests of Camelot/Longbow*
- *EcoQuest 1–2*
- *Freddy Pharkas*
- *Pepper's Adventures in Time*
- *Phantasmagoria 1* (Good rating) and *Phantasmagoria 2: A Puzzle of Flesh*
- *Lighthouse* (Good rating)
- *Torin's Passage*
- *Shivers 1*[^ref-1]

### Recent ScummVM Releases

Since 2026.1.0, ScummVM uses year-based version numbers and releases more often, roughly every three months: 2026.1.0 "Like a Version" (Jan 31), 2026.2.0 "Railmonicon" (Mar 28), 2026.3.0 "Carousels & Killer Whales" (Jun 20) and 2026.4.0 "Never-slop" (Oct 2026).[^ref-2][^ref-5][^ref-6][^ref-4]

**Sierra-relevant additions:**
- **Dynamix DGDS engine** — *Rise of the Dragon* added in 2.9.0 (Dec 2024); *Heart of China* and *The Adventures of Willy Beamish* added in 2026.1.0. All three are rated "Good".[^ref-3][^ref-4][^ref-1]
- 2026.1.0 added **12 new engines** and "at least 194 titles", optional SDL3 builds, and Android/iOS upgrades[^ref-2]

**Previous SCI fixes (2.9.1, May 2025):**[^ref-4]
- Fixed QFG4 v1.0 crash in Thieves' Guild
- Fixed GK1 day 5 phone lockup
- Fixed KQ6 CD crash when talking to Rotten Tomato from the inventory window in high-resolution mode
- Fixed LSL1 lockup when entering casino
- Fixed SQ5 introduction comets not appearing on machines faster than a 386

### Games NOT in ScummVM (Use DOSBox or Windows)
These titles do not appear on ScummVM's compatibility list:[^ref-1]
- *Quest for Glory V: Dragon Fire* (3D engine)
- *Gabriel Knight 3* (3D engine)
- *King's Quest: Mask of Eternity* (3D engine)
- *Shivers Two* (its game logic lives in native DLLs, not SCI scripts, so ScummVM lists it as not implemented)[^ref-8]
- All Dynamix flight/mech sims
- *SWAT 2* and *SWAT 3* (*Police Quest: SWAT* is supported)
- *3-D Ultra* series

## DOSBox Staging

**Current version:** Check [dosbox-staging.org](https://www.dosbox-staging.org/) for the latest release[^ref-11]
- [Download page](https://www.dosbox-staging.org/download/)
- Modern fork with improved accuracy, pixel shaders, and built-in MIDI support

### Key Features for Sierra Games
- **MT-32 emulation** – Integrated Roland MT-32 emulation, no hardware needed[^ref-11]
- **FluidSynth integration** – Built-in FluidSynth MIDI synth for General MIDI via soundfonts[^ref-11]
- **CRT shaders** – Zero-config CRT emulation[^ref-11]
- **Dynamic recompilation** – 64-bit dynamic recompilation on ARM and x64[^ref-11]
- **Mouse improvements** – Advanced built-in mouse driver[^ref-11]

Use SierraHelp's DOSBox installers when available; they set the game up to start in DOSBox from a Windows shortcut and download DOSBox if it is missing.[^ref-18]

## Windows 11 Compatibility

### Known Issues
- **16-bit installers fail** – Windows 11 has no 16-bit subsystem. Use:
  - [OTVDM (winevdm)](https://github.com/otya128/winevdm) – a 16-bit Windows emulator ported to 64-bit Windows, for running `SETUP.EXE`[^ref-24]
  - SierraHelp's modern installers (they download and install DOSBox or ScummVM if needed)[^ref-18]
  - Extract directly with 7-Zip, configure manually
- **High DPI scaling** – Some SCI32 games have UI issues at 4K. Set compatibility mode to "System (Enhanced)" DPI settings
- **SmartScreen warnings** – Community installers may trigger antivirus false positives; allow through Windows Security[^ref-18]
- **Defender folder exclusions** – DOSBox can be slow if Windows is scanning; exclude your games folder

### Windows 95/98 Titles on Windows 11
- Use a current dgVoodoo2 release (v2.87.5 as of September 2026) for DirectDraw/Direct3D games[^ref-25]
- Run in Windows XP SP3 compatibility mode
- For stubborn titles, consider a Windows 98 VM via VirtualBox or PCem

## macOS Compatibility (Sonoma/Sequoia/Tahoe)

### macOS 14 Sonoma, macOS 15 Sequoia & macOS 26 Tahoe
Apple Silicon Macs require specific approaches:

**ScummVM** – Native Apple Silicon version available
- Download the macOS 10.13+ build for Intel and Apple Silicon from [scummvm.org](https://www.scummvm.org/downloads/)[^ref-7]
- Works natively on M1/M2/M3/M4 Macs
- No Rosetta 2 required for ScummVM itself

**DOSBox Staging** – Native Apple Silicon support
- 64-bit dynamic recompilation on ARM[^ref-11]

**CrossOver** (v26.3.0, July 2026) – For Windows Sierra games
- CrossOver 26 is based on Wine 11.0 and added UI updates for macOS Tahoe[^ref-26]
- Based on Wine; good for Windows 95/98 Sierra titles
- [CrossOver compatibility database](https://www.codeweavers.com/compatibility)

**Boxer** – macOS-native DOSBox wrapper
- The original Boxer has had no commits since October 2021;[^ref-31] the MaddTheSane fork on GitHub offers beta builds with Apple Silicon support[^ref-28]
- Drag-and-drop game installation

### macOS-Specific Issues
- **Gatekeeper**: Right-click → Open for unsigned apps (most community installers)
- **App Translocation**: Move apps out of Downloads before first run
- **32-bit apps**: No longer work on macOS 10.15+ (use ScummVM/DOSBox instead of original Mac ports)[^ref-27]

### Classic Mac Games (68k/PPC)
For original Macintosh Sierra games:
- **Basilisk II** – 68k Mac emulator (for early Sierra Mac ports)
- **SheepShaver** – PowerPC Mac emulator (for later Mac ports)
- Extract disk images and watch for QuickDraw patch requirements

## AGI/SCI Adventures
- Use ScummVM for *King's Quest*, *Space Quest*, *Leisure Suit Larry*, *Police Quest*, *Quest for Glory*, and *Gabriel Knight 1*; it resolves timing bugs and adds autosave options.
- If you prefer DOSBox, SierraHelp provides NewRisingSun's fan-made timer-bug patches and DOSBox installers for Windows.[^ref-19][^ref-18]
- SCI32 titles (*Phantasmagoria*, *Torin's Passage*, *Shivers*) often require CD-to-hard drive copies; SierraHelp installers automate this.

## Dynamix Sims & 3-D Ultra
- *Aces*/*Red Baron* – Needs joystick calibration in DOSBox. SierraHelp hosts updates for both the Aces and Red Baron series.[^ref-20]
- *Earthsiege / Starsiege* – Windows versions run on modern OSes with compatibility modes; fan patches add widescreen and multiplayer fixes.
- *3-D Ultra Pinball/MiniGolf* – Seek out DirectX wrappers (dgVoodoo2) or SierraHelp's 3-D Ultra series updates to fix missing FMV and audio on Windows 10+.[^ref-20]

## Windows 95/98 Releases
- Many Win95 titles rely on 16-bit installers; use SierraHelp or *OTVDM* (a 16-bit Windows emulator) to run setup programs.[^ref-24]
- SierraHelp hosts the official updates for *Phantasmagoria: A Puzzle of Flesh* (including DOS support and a sound-driver update), *Lighthouse* (2.0/2.0a patches), *Torin's Passage* and *SWAT 3*.[^ref-21][^ref-23][^ref-22][^ref-20]
- For CD-heavy titles, copy all discs to HDD and edit INI files to point to the local path (SierraHelp scripts automate this).

## Fan Remakes & Spiritual Successors
- AGDI/Infamous Adventures remakes ship with modern installers but occasionally require compatibility mode on Windows 11; check their forums for hotfixes.
- *SpaceVenture* (released December 2025) updates roll out through Steam and itch.io; watch the Guys from Andromeda site for news.[^ref-30]
- *Hero-U* and other Unity-based successors receive ongoing bug fixes—enable automatic updates on Steam/GOG.

## Console & VR Ports
- *Colossal Cave 3D Adventure* – Keep Meta Quest/console firmware current; updates arrive via platform storefronts. The PC version receives patch notes on Steam.
- Later Larry entries (*Wet Dreams Don't Dry/Dry Twice*) patch through console stores; check CrazyBunch's official site for changelog posts.

## Recovery Tips
- Always back up GOG/Steam installers; some Activision-era titles temporarily leave storefronts.
- For disk-based releases, create ISO images and use DOSBox `imgmount` to avoid CD swapping.
- Keep a dedicated compatibility folder with DOSBox capture configs, ScummVM builds, and patch readme files for future reference.

## External References
- [ScummVM Downloads](https://www.scummvm.org/downloads/) – Official builds for all platforms
- [ScummVM Compatibility](https://www.scummvm.org/compatibility/) – Full game support list with ratings
- [DOSBox Staging](https://www.dosbox-staging.org/) – Modern DOSBox fork
- [SierraHelp.com](https://sierrahelp.com/) – Community patches and installers
- [CrossOver](https://www.codeweavers.com/crossover) – Wine-based Windows compatibility layer for macOS/Linux
- [dgVoodoo2](http://dege.freeweb.hu/dgVoodoo2/) – DirectX wrapper for older Windows games
- [OTVDM (winevdm)](https://github.com/otya128/winevdm) – 16-bit Windows app compatibility layer

## References

[^ref-1]: [ScummVM – Compatibility list](https://www.scummvm.org/compatibility/) – per-game ratings checked 2026-10-16: AGI titles "Good" except KQ2 "Excellent"; GK2, Phantasmagoria 2 "Excellent"; PQ: SWAT, PQ4, SQ6, KQ7, Phantasmagoria, Lighthouse, DGDS games "Good"; QFG5, GK3, KQ8, SWAT 2/3, Shivers Two absent
[^ref-2]: [ScummVM – 2026.1.0 "Like a Version" is finally released (Jan 31, 2026)](https://www.scummvm.org/news/20260131/) – new version numbering, "more frequent releases", 12 new engines, "at least 194 titles", optional SDL3, Android/iOS upgrades
[^ref-3]: [ScummVM – 2.9.0 release news (Dec 22, 2024)](https://www.scummvm.org/news/20241222/) – Rise of the Dragon newly supported
[^ref-4]: [ScummVM – NEWS.md](https://github.com/scummvm/scummvm/blob/master/NEWS.md) – release dates for 2.9.0, 2.9.1, 2026.1.0–2026.4.0; 2026.1.0 "Added support for The Adventures of Willy Beamish… Heart of China"; 2.9.1 SCI fixes
[^ref-5]: [ScummVM – 2026.2.0 "Railmonicon" (Mar 28, 2026)](https://www.scummvm.org/news/20260328/) – "Three months have passed since the last release… with our new release approach"
[^ref-6]: [ScummVM – 2026.4.0 "Never-slop" (Oct 2026)](https://www.scummvm.org/news/20261011/) – latest release at time of writing; "we continue to follow our new release cadence"
[^ref-7]: [ScummVM – Downloads](https://www.scummvm.org/downloads/) – "macOS 10.13+ for Intel and Apple Silicon"; Flatpak package on flathub.org; daily builds
[^ref-8]: [ScummVM source – engines/sci/detection_tables.h](https://github.com/scummvm/scummvm/blob/master/engines/sci/detection_tables.h) – "Shivers 2 doesn't contain SCI scripts… classifies Shivers 2 as 'not SCI'"; marked GAME_NOT_IMPLEMENTED
[^ref-9]: [Wikipedia – Adventure Game Interpreter](https://en.wikipedia.org/wiki/Adventure_Game_Interpreter) – used "in 14 of their games between 1984 and 1989"
[^ref-10]: [Wikipedia – Sierra Creative Interpreter](https://en.wikipedia.org/wiki/Sierra_Creative_Interpreter) – introduced 1988 (King's Quest IV); latest release 1996 (SCI3)
[^ref-11]: [DOSBox Staging – Home](https://www.dosbox-staging.org/) – "Integrated Roland MT-32 emulation", "Built-in FluidSynth MIDI synth", "zero-config CRT emulation", "64-bit dynamic recompilation… (ARM & x64)", "Advanced built-in mouse driver"
[^ref-12]: [Flathub – ScummVM](https://flathub.org/apps/org.scummvm.ScummVM) – Flatpak ID org.scummvm.ScummVM
[^ref-13]: [Flathub – DOSBox Staging](https://flathub.org/apps/io.github.dosbox-staging) – Flatpak ID io.github.dosbox-staging
[^ref-14]: [EmuDeck – Supported emulators (SteamOS)](https://emudeck.github.io/emulators/steamos/supported-emulators/) – ScummVM listed
[^ref-15]: [RetroDECK Wiki – RetroArch general guide](https://retrodeck.readthedocs.io/en/latest/wiki_multi_emulator_guides/retroarch/retroarch-guide/) – DOS system mapped to the DOSBox Pure core
[^ref-16]: [Valve – Proton README](https://github.com/ValveSoftware/Proton/blob/proton_10.0/README.md) – "PROTON_USE_WINED3D=1 %command%" to use the OpenGL-based wined3d renderer
[^ref-17]: [Steam Deck – Tech specs](https://www.steamdeck.com/en/tech) – display 1280 x 800
[^ref-18]: [SierraHelp – New Sierra Installers](https://sierrahelp.com/Patches-Updates/NewSierraInstallers.html) – installers set games up in DOSBox from a Windows shortcut; download DOSBox if missing; check online for current DOSBox/ScummVM; antivirus false positives noted
[^ref-19]: [SierraHelp – New Timer Bug Updates](https://sierrahelp.com/Patches-Updates/NewTimerBugUpdates.html) – "fan made patches that fix these bugs, most notably from NewRisingSun"
[^ref-20]: [SierraHelp – Sierra Game Updates index](https://sierrahelp.com/Patches-Updates/Patches-Updates.html) – entries for 3-D Ultra, Aces, Red Baron, Phantasmagoria, Lighthouse, SWAT, Torin's Passage; no Shivers, Hunter Hunted or CyberGladiators entry
[^ref-21]: [SierraHelp – Phantasmagoria Updates](https://sierrahelp.com/Patches-Updates/Patches-Updates-Games/PhantasmagoriaSeriesUpdates.html) – Phantasmagoria II DOS support patches and sound driver update
[^ref-22]: [SierraHelp – SWAT Updates](https://sierrahelp.com/Patches-Updates/Patches-Updates-Games/SWATUpdates.html) – SWAT 3 patches and data updaters
[^ref-23]: [SierraHelp – Lighthouse Patches](https://sierrahelp.com/Patches-Updates/Patches-Updates-Games/LighthouseUpdates.html) – Lighthouse 2.0 and 2.0a patches
[^ref-24]: [otya128/winevdm – README](https://github.com/otya128/winevdm) – "16-bit Windows (Windows 1.x, 2.x, 3.0, 3.1, etc.) on 64-bit Windows… a 16-bit Windows emulator, ported to 64-bit Windows"
[^ref-25]: [dgVoodoo2 – GitHub releases](https://github.com/dege-diosg/dgVoodoo2/releases) – latest release v2.87.5 (Sep 15, 2026); [project site](http://dege.freeweb.hu/dgVoodoo2/): "implementation of old graphics API's for Windows 7 and later"
[^ref-26]: [CodeWeavers – CrossOver Change Log](https://www.codeweavers.com/crossover/changelog) – 26.3.0 (July 21, 2026); CrossOver 26 "includes Wine 11.0… UI updates for macOS Tahoe"
[^ref-27]: [Apple Support – 32-bit app compatibility with macOS](https://support.apple.com/en-us/103076) – "Starting with macOS Catalina 10.15, 32-bit apps are no longer compatible with macOS"
[^ref-28]: [MaddTheSane/Boxer – Releases](https://github.com/MaddTheSane/Boxer/releases) – "This is a beta release that adds Apple Silicon support" (AS-beta-4.1, Apr 2022)
[^ref-29]: [QuestForMoreGlory.com – news box (archived Mar 22, 2024)](https://web.archive.org/web/20240322150642if_/http://www.questformoreglory.com/sections/menu-textbox7.html) – "Collector's New Quest for Glory Installers… Quest for Glory V Patches x64-bit… Our Downloads Section… Our Game Help Section"
[^ref-30]: [Steam – SpaceVenture](https://store.steampowered.com/app/1374960/) – released Dec 23, 2025, developer Guys from Andromeda; also on [itch.io](https://guysfromandromeda.itch.io/spaceventure)
[^ref-31]: [alinebee/Boxer – GitHub](https://github.com/alinebee/Boxer) – original Boxer repository; last push October 24, 2021

