---
title: "Patch & Compatibility Guide"
type: guide
updated: 2025-01-30
---
# Patch & Compatibility Guide

This guide highlights essential fixes, installers, and configuration tips for running Sierra-era games on modern systems. Combine these with the [[Platform Guide\|Platform Guide]] and [[Buying Guide\|Buying Guide]] for best results.

## Essential Sources
- [SierraHelp.com](https://www.sierrahelp.com/) – Community-made installers, DOSBox/ScummVM wrappers, and patch mirrors for nearly every Sierra release.
- [ScummVM](https://www.scummvm.org/) – Preferred runtime for AGI/SCI games; includes bug fixes, mouse enhancements, and digital audio support.
- [DOSBox Staging](https://dosbox-staging.github.io/) – Modern DOSBox fork with enhanced features for games not supported by ScummVM.
- [SpaceQuest.net](https://spacequest.net/) – Series-specific fixes for *Space Quest* releases.
- [QuestForMoreGlory.com](https://www.questformoreglory.com/) – Hero import utilities and fan fixes for *Quest for Glory*.

## Steam Deck Compatibility

The Steam Deck provides excellent compatibility for Sierra games through multiple methods:

### ScummVM on Steam Deck
The **recommended approach** for most Sierra adventure games. ScummVM is available through:
- **Flathub** (Desktop Mode): `flatpak install flathub org.scummvm.ScummVM`
- **Discover Store**: Search "ScummVM" in Desktop Mode's Discover app
- **EmuDeck**: Includes ScummVM as part of its retro gaming suite

**Setup tips:**
1. Install ScummVM via Flatpak in Desktop Mode
2. Copy game files to `/home/deck/Games/ScummVM/` or similar accessible location
3. Add games to ScummVM, then add ScummVM as a non-Steam game
4. Configure controller mappings in Steam Input (ScummVM supports gamepad natively)
5. Use ScummVM's built-in "Stretch to fit" for proper display on the Deck's 1280×800 screen

### DOSBox on Steam Deck
For DOS-based Sierra games not supported by ScummVM (flight sims, strategy games):
- **DOSBox Staging** – Available via Flathub with improved performance and modern features
- **RetroDECK/EmuDeck** – Pre-configured DOSBox setups with controller support
- GOG and Steam installers generally work through Proton

### Proton/Wine for Windows Versions
For Windows 95/98 Sierra titles:
- Most SierraHelp installers work with **Proton Experimental** or **GE-Proton**
- Use `PROTON_USE_WINED3D=1` launch option for older DirectX games
- *3-D Ultra* series and Dynamix Windows games often need dgVoodoo2 bundled

### Sierra Game Compatibility Summary (Steam Deck)

| Game Type | Method | Notes |
|-----------|--------|-------|
| AGI Games (KQ I–IV, SQ I–II, LSL 1) | ScummVM | Native controller support, excellent |
| SCI16 Games (KQ V–VI, SQ III–V) | ScummVM | Excellent, all features work |
| SCI32 Games (KQ VII, GK1, Phantasmagoria) | ScummVM | Good; some minor issues in Phantasmagoria |
| DOS Simulations (Aces, Red Baron) | DOSBox Staging | Joystick config needed |
| Windows 95/98 Titles | Proton + dgVoodoo2 | Varies by title |

## ScummVM Version & Engine Support

**Current stable version:** Check [scummvm.org](https://www.scummvm.org/) for the latest release
- [Download page](https://www.scummvm.org/downloads/)
- [Compatibility list](https://www.scummvm.org/compatibility/)

### Sierra-Specific Engines
ScummVM provides dedicated engines for Sierra games with **Excellent** compatibility ratings:

**AGI Engine** – Sierra's Adventure Game Interpreter (1984–1989):
- *King's Quest I–IV* (including SCI remake of KQ1)
- *Space Quest I–II*
- *Leisure Suit Larry 1* (original)
- *Police Quest 1* (original)
- *Manhunter 1–2*
- *Gold Rush!*
- *Mixed-Up Mother Goose* (original)

**SCI Engine** – Sierra's Creative Interpreter (1988–1999):
- *King's Quest V–VII* (KQ7 rated "Good")
- *Space Quest III–VI*
- *Leisure Suit Larry 2–7*
- *Police Quest 2–4*
- *Quest for Glory I–IV* (including VGA remakes)
- *Gabriel Knight 1* (CD and floppy versions)
- *Laura Bow 1–2*
- *Conquests of Camelot/Longbow*
- *EcoQuest 1–2*
- *Freddy Pharkas*
- *Pepper's Adventures in Time*
- *Phantasmagoria 1* (Good rating)
- *Lighthouse* (Good rating)
- *Torin's Passage*
- *Shivers 1*

### ScummVM v2026.1.0 "Like a Version" (Jan 31, 2026)

**Major Sierra-relevant additions:**
- **Dynamix DGDS engine** — Full support for *Rise of the Dragon*, *Heart of China*, *Willy Beamish*
- **12 new engines** with 190+ new games total
- New quarterly release schedule for faster updates
- SDL3 support, improved Android/iOS builds

**Previous fixes (2.9.x):**
- Fixed QFG4 v1.0 crash in Thieves' Guild
- Fixed GK1 day 5 phone lockup
- Fixed KQ6 CD crash in high-resolution mode
- Fixed LSL1 lockup when entering casino
- Fixed SQ5 intro comet timing on modern CPUs

### Games NOT in ScummVM (Use DOSBox)
- *Quest for Glory V: Dragon Fire* (3D engine)
- *Gabriel Knight 2: The Beast Within* (FMV-heavy)
- *Gabriel Knight 3* (3D engine)
- *King's Quest: Mask of Eternity* (3D engine)
- *Phantasmagoria 2*
- All Dynamix flight/mech sims
- *SWAT* series
- *3-D Ultra* series

## DOSBox Staging

**Current version:** Check [dosbox-staging.github.io](https://dosbox-staging.github.io/) for the latest release
- [Download page](https://dosbox-staging.github.io/)
- Modern fork with improved accuracy, pixel shaders, and built-in MIDI support

### Key Features for Sierra Games
- **MT-32 emulation** – Authentic Roland sound without hardware
- **FluidSynth integration** – High-quality General MIDI via soundfonts
- **CRT shaders** – Period-appropriate display filters
- **Dynamic CPU cycles** – Better timing for speed-sensitive games
- **Mouse capture improvements** – Smoother control in adventure games

Use SierraHelp's pre-configured DOSBox profiles when available.

## Windows 11 Compatibility

### Known Issues
- **16-bit installers fail** – Windows 11 has no 16-bit subsystem. Use:
  - [OTVDM](https://github.com/nicfab/otvdm) – 16-bit thunking layer for running `SETUP.EXE`
  - SierraHelp's modern installers (bundle DOSBox/ScummVM)
  - Extract directly with 7-Zip, configure manually
- **High DPI scaling** – Some SCI32 games have UI issues at 4K. Set compatibility mode to "System (Enhanced)" DPI settings
- **SmartScreen warnings** – Community patches may trigger false positives; allow through Windows Security
- **Defender folder exclusions** – DOSBox can be slow if Windows is scanning; exclude your games folder

### Windows 95/98 Titles on Windows 11
- Use dgVoodoo2 (v2.84.1 or later) for DirectDraw/Direct3D games
- Run in Windows XP SP3 compatibility mode
- For stubborn titles, consider a Windows 98 VM via VirtualBox or PCem

## macOS Compatibility (Sonoma/Sequoia)

### macOS 14 Sonoma & macOS 15 Sequoia
Apple Silicon Macs require specific approaches:

**ScummVM** – Native Apple Silicon version available
- Download universal binary from [scummvm.org](https://www.scummvm.org/downloads/)
- Works natively on M1/M2/M3/M4 Macs
- No Rosetta 2 required for ScummVM itself

**DOSBox Staging** – Native Apple Silicon support
- Native ARM64 builds available
- Excellent performance on Apple Silicon

**CrossOver** (v25.1.1) – For Windows Sierra games
- Full support for macOS 15 Sequoia and 14 Sonoma
- Based on Wine; good for Windows 95/98 Sierra titles
- [CrossOver compatibility database](https://www.codeweavers.com/compatibility)

**Boxer/Boxer-CE** – macOS-native DOSBox wrapper
- Now maintained as Boxer-CE for Apple Silicon
- Drag-and-drop game installation

### macOS-Specific Issues
- **Gatekeeper**: Right-click → Open for unsigned apps (most community installers)
- **App Translocation**: Move apps out of Downloads before first run
- **32-bit apps**: No longer work on macOS 10.15+ (use ScummVM/DOSBox instead of original Mac ports)

### Classic Mac Games (68k/PPC)
For original Macintosh Sierra games:
- **Basilisk II** – 68k Mac emulator (for early Sierra Mac ports)
- **SheepShaver** – PowerPC Mac emulator (for later Mac ports)
- Extract disk images and watch for QuickDraw patch requirements

## AGI/SCI Adventures
- Use ScummVM for *King's Quest*, *Space Quest*, *Leisure Suit Larry*, *Police Quest*, *Quest for Glory*, and *Gabriel Knight 1*; it resolves timing bugs and adds autosave options.
- If you prefer DOSBox, SierraHelp provides "NewRisingSun" timing patches and high-res icon installers for Windows.
- SCI32 titles (*Phantasmagoria*, *Torin's Passage*, *Shivers*) often require CD-to-hard drive copies; SierraHelp installers automate this.

## Dynamix Sims & 3-D Ultra
- *Aces*/*Red Baron* – Needs 640×480 VGA and joystick calibration; apply community patches to fix sound and high CPU usage. SierraHelp's installers package DOSBox profiles.
- *Earthsiege / Starsiege* – Windows versions run on modern OSes with compatibility modes; fan patches add widescreen and multiplayer fixes.
- *3-D Ultra Pinball/MiniGolf* – Seek out fan-made DirectX wrappers (dgVoodoo2) or the SierraHelp installers to fix missing FMV and audio on Windows 10+.
- *Hunter Hunted / CyberGladiators* – Use the latest executable from the patch collections to avoid startup crashes on modern GPUs.

## Windows 95/98 Releases
- Many Win95 titles rely on 16-bit installers; use SierraHelp or *OTVDM* (16-bit thunking layer) to run setup programs.
- Apply official patches for *Phantasmagoria 2*, *Shivers 2*, *SWAT 2*, *Lighthouse*, and *Torin's Passage* to fix script bugs and missing video.
- For CD-heavy titles, copy all discs to HDD and edit INI files to point to the local path (SierraHelp scripts automate this).

## Fan Remakes & Spiritual Successors
- AGDI/Infamous Adventures remakes ship with modern installers but occasionally require compatibility mode on Windows 11; check their forums for hotfixes.
- *SpaceVenture* updates roll out through Steam/Itch; watch the Two Guys blog for Unity patches addressing audio/video desync.
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
- [DOSBox Staging](https://dosbox-staging.github.io/) – Modern DOSBox fork
- [SierraHelp.com](https://www.sierrahelp.com/) – Community patches and installers
- [CrossOver](https://www.codeweavers.com/crossover) – Wine-based Windows compatibility layer for macOS/Linux
- [dgVoodoo2](http://dege.freeweb.hu/dgVoodoo2/dgVoodoo2/) – DirectX wrapper for older Windows games
- [OTVDM](https://github.com/nicfab/otvdm) – 16-bit Windows app compatibility layer
