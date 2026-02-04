---
title: "Playing Sierra Games Today"
type: guide
last_updated: "2026-01-31"
---
# Playing Sierra Games Today

<small style="color: gray">Last updated: January 31, 2026</small>

A comprehensive guide to running Sierra's classic games on modern computers, consoles, and handhelds. Whether you're revisiting childhood favorites or discovering these adventures for the first time, this guide will get you playing.

---

## Quick Start: Which Method Should I Use?

| Game Type | Recommended Method | Difficulty |
|-----------|-------------------|------------|
| AGI adventures (1984–1989) | **ScummVM** | Easy ⭐ |
| SCI adventures (1988–1998) | **ScummVM** | Easy ⭐ |
| Dynamix adventures (Rise of the Dragon, etc.) | **ScummVM** | Easy ⭐ |
| Gobliiins series | **ScummVM** | Easy ⭐ |
| Flight sims (Red Baron, Aces) | **DOSBox Staging** | Medium ⭐⭐ |
| Strategy (Caesar, Lords of the Realm) | **DOSBox Staging** | Medium ⭐⭐ |
| Windows 95/98 games (QFG5, KQ:MoE, GK3) | **GOG/Steam + patches** | Medium ⭐⭐ |
| Sports sims (NASCAR, Front Page Sports) | **DOSBox Staging** | Medium ⭐⭐ |
| 3D Ultra series | **Windows + dgVoodoo2** | Hard ⭐⭐⭐ |

---

## Method 1: ScummVM (Recommended for Adventures)

ScummVM is a program that reimplements the game engines Sierra used, allowing their adventures to run natively on modern systems with enhanced features.

### Why ScummVM?

- **Zero configuration** — Add game files, start playing
- **Save anywhere** — Modern save/load system with autosave
- **Enhanced audio** — Roland MT-32 and General MIDI support
- **Cross-platform** — Windows, macOS, Linux, Android, iOS, Steam Deck
- **Bug fixes** — Many original game bugs are fixed
- **Quality of life** — Smooth scrolling, mouse wheel support, subtitles

### Supported Sierra Games

ScummVM supports nearly all Sierra adventure games with **Excellent** compatibility:[^ref-1]

**AGI Engine Games (1984–1989):**
- King's Quest I–IV (including SCI remake of KQ1)
- Space Quest I–II
- Leisure Suit Larry 1 (original)
- Police Quest 1 (original)
- Manhunter 1–2
- Gold Rush!
- Mixed-Up Mother Goose (original)
- Donald Duck's Playground
- The Black Cauldron

**SCI Engine Games (1988–1998):**
- King's Quest V–VII
- Space Quest III–VI
- Leisure Suit Larry 2–7
- Police Quest 2–4
- Quest for Glory I–IV (including VGA remakes)
- Gabriel Knight 1 (both floppy and CD versions)
- Laura Bow 1–2
- Conquests of Camelot and Longbow
- EcoQuest 1–2
- Freddy Pharkas
- Pepper's Adventures in Time
- Phantasmagoria 1
- Lighthouse
- Torin's Passage
- Shivers 1

**Dynamix Games:**
- Rise of the Dragon
- Heart of China
- The Adventures of Willy Beamish

**Coktel Vision Games:**
- Gobliiins trilogy
- Lost in Time
- Woodruff and the Schnibble
- Fascination
- Urban Runner
- Ween: The Prophecy

### Setting Up ScummVM

**Step 1: Download ScummVM**
Visit [scummvm.org/downloads](https://www.scummvm.org/downloads/) and download for your platform:
- Windows (32/64-bit)
- macOS (Universal Binary for Intel/Apple Silicon)
- Linux (Flatpak, Snap, or distribution packages)

**Step 2: Obtain Game Files**
You need the original game data files. Sources include:
- **GOG.com** — Pre-packaged, DRM-free, includes manuals
- **Steam** — Usually needs file extraction
- **Original discs** — Copy files from CD/floppy

**Step 3: Add Games**
1. Launch ScummVM
2. Click "Add Game"
3. Navigate to folder containing game files
4. ScummVM auto-detects the game
5. Configure options if desired
6. Click "Start" to play

### Tips for ScummVM

- **Enable subtitles** in games with voice acting for clarity
- **Use original game manuals** for copy protection answers (included in GOG versions)
- **Check game-specific notes** on the [ScummVM compatibility page](https://www.scummvm.org/compatibility/)
- **Roland MT-32 emulation** is built-in for authentic 1988–1993 era sound

---

## Method 2: DOSBox Staging (For Simulations & Strategy)

DOSBox Staging is a modern, enhanced fork of DOSBox that's ideal for games ScummVM doesn't support.

### Why DOSBox Staging?

DOSBox Staging is the recommended DOSBox variant for 2024+:[^ref-2]
- **Authentic CRT emulation** — Built-in shaders that auto-adjust
- **Roland MT-32 emulation** — No extra ROMs needed for most use cases
- **FluidSynth integration** — High-quality General MIDI
- **Modern controller support** — 10-axis controllers, real-time calibration
- **Zero-config defaults** — Sensible settings out of the box
- **ARM64 support** — Native on Apple Silicon and Steam Deck

### Games That Need DOSBox

- Red Baron, Red Baron II/3D
- Aces of the Pacific, Aces Over Europe, Aces of the Deep
- A-10 Tank Killer
- Earthsiege series
- Starsiege
- Front Page Sports series
- Trophy Bass
- NASCAR Racing (early entries)
- IndyCar Racing
- Caesar I–II
- Lords of the Realm I–II
- The Incredible Machine series
- 3-D Ultra Pinball (DOS versions)
- Most sports and simulation titles

### Setting Up DOSBox Staging

**Step 1: Download DOSBox Staging**
Visit [dosbox-staging.org](https://www.dosbox-staging.org/) for your platform.

**Step 2: Create a Games Folder**
Organize your DOS games:
```
C:\DOSGames\
├── RedBaron\
├── Aces\
└── NASCAR\
```

**Step 3: Mount and Run**
From DOSBox Staging command prompt:
```
mount c c:\DOSGames
c:
cd redbaron
install
```

### DOSBox Tips for Sierra Games

- **Use SierraHelp installers** — [SierraHelp.com](https://www.sierrahelp.com/) provides pre-configured DOSBox profiles
- **Joystick calibration** — Flight sims need calibration; use `[joystick]` section in config
- **CPU cycles** — Adjust `cycles=` if games run too fast or slow
- **Sound configuration** — Run `INSTALL.EXE` or `SETUP.EXE` in games to configure audio

---

## Method 3: GOG.com (Easiest Option)

GOG.com packages Sierra classics with pre-configured DOSBox or ScummVM, requiring minimal setup.

### What GOG Provides

- Pre-configured emulators
- Original manuals (PDF)
- Hint books (when available)
- Bonus content (soundtracks, artwork)
- DRM-free installers
- Windows and Mac support

### Available Sierra Collections on GOG

| Collection | Games Included | Price |
|------------|----------------|-------|
| [King's Quest 1+2+3](https://www.gog.com/game/kings_quest_1_2_3) | KQ1 AGI, KQ2, KQ3 | $9.99 |
| [King's Quest 4+5+6](https://www.gog.com/game/kings_quest_4_5_6) | KQ4, KQ5, KQ6 | $9.99 |
| [King's Quest 7+8](https://www.gog.com/game/kings_quest_7_8) | KQ7, Mask of Eternity | $9.99 |
| [Space Quest 1+2+3](https://www.gog.com/game/space_quest_1_2_3) | SQ1 EGA, SQ2, SQ3 | $9.99 |
| [Space Quest 4+5+6](https://www.gog.com/game/space_quest_4_5_6) | SQ4, SQ5, SQ6 | $9.99 |
| [Quest for Glory Collection](https://www.gog.com/game/quest_for_glory) | QFG1–5 + VGA remake | $9.99 |
| [Police Quest Collection](https://www.gog.com/game/police_quest_1_2_3_4) | PQ1–4 + SWAT | $9.99 |
| [Leisure Suit Larry Collection](https://www.gog.com/game/leisure_suit_larry) | LSL1–7 + remakes | $9.99 |
| [Gabriel Knight trilogy](https://www.gog.com/game/gabriel_knight_sins_of_the_fathers) | GK1, GK2, GK3 | Various |
| [Phantasmagoria 1+2](https://www.gog.com/game/phantasmagoria) | Both games | $9.99 |

### GOG Caveats

- **Missing VGA remakes** — Some collections omit the SCI remakes; Steam versions include them
- **Windows-only installers** — macOS support is limited; use ScummVM instead
- **Dated ScummVM builds** — GOG may bundle older ScummVM versions; update manually if needed

---

## Method 4: Steam (For VGA Remakes)

Steam's Sierra collections often include VGA remakes that GOG lacks.

### Steam Exclusive Content

- **King's Quest I SCI Remake (1990)** — Only in Steam collection
- **Space Quest I VGA Remake (1991)** — Only in Steam collection
- Both original AND remake versions included since 2016 updates

### Available on Steam

- [King's Quest Collection](https://store.steampowered.com/app/10100/) — KQ1–7 + SCI remake
- [Space Quest Collection](https://store.steampowered.com/app/10110/) — SQ1–6 + VGA remake
- [Quest for Glory 1-5](https://store.steampowered.com/app/502750/)
- [Police Quest Collection](https://store.steampowered.com/app/494740/)
- [Gabriel Knight trilogy](https://store.steampowered.com/app/495700/)
- [Phantasmagoria 1+2](https://store.steampowered.com/app/501990/)

### Running Steam Games with ScummVM

Steam versions can be extracted and run with ScummVM for better features:
1. Right-click game in Steam library
2. Select "Manage" → "Browse local files"
3. Copy game folders to your ScummVM games directory
4. Add to ScummVM as usual

---

## Method 5: Windows 95/98 Era Games

Games from 1995–1999 often need special handling.

### Games Requiring Windows Compatibility

- Quest for Glory V: Dragon Fire (1998)
- Gabriel Knight 2: The Beast Within (1995)
- Gabriel Knight 3: Blood of the Sacred, Blood of the Damned (1999)
- King's Quest: Mask of Eternity (1998)
- Phantasmagoria 2: A Puzzle of Flesh (1996)
- SWAT 2 (1998)
- Shivers 2 (1997)
- Caesar III (1998)
- Pharaoh (1999)
- Zeus: Master of Olympus (2000)

### Running Windows 95/98 Games

**Option 1: Compatibility Mode (Windows 10/11)**
1. Right-click game executable
2. Properties → Compatibility tab
3. Check "Run this program in compatibility mode"
4. Select Windows XP SP3 or Windows 98
5. Check "Run as administrator" if needed

**Option 2: dgVoodoo2 (for 3D games)**
[dgVoodoo2](http://dege.freeweb.hu/dgVoodoo2/) wraps old DirectX/Glide calls for modern GPUs:
1. Download dgVoodoo2
2. Copy D3D*.dll and DDraw.dll to game folder
3. Run dgCpl.exe to configure

**Option 3: Virtual Machine**
For stubborn titles, run Windows 98/XP in:
- VirtualBox
- VMware
- PCem (for period-accurate emulation)

### Common Windows 95/98 Issues

| Problem | Solution |
|---------|----------|
| 16-bit installer fails | Use [OTVDM](https://github.com/nicfab/otvdm) or SierraHelp installers |
| CD-ROM not detected | Copy all CDs to hard drive, edit INI files |
| Videos don't play | Install Windows Media Player codecs |
| Colors are wrong | Run in 256-color mode, use dgVoodoo2 |
| Game runs too fast | Use CPU limiter or frame rate cap |

---

## Platform-Specific Guides

### Steam Deck

Steam Deck provides excellent Sierra game compatibility:[^ref-3]

**For ScummVM Games:**
1. Install ScummVM from Flathub in Desktop Mode: `flatpak install flathub org.scummvm.ScummVM`
2. Copy game files to `/home/deck/Games/ScummVM/`
3. Add games in ScummVM
4. Add ScummVM as non-Steam game for controller support

**For DOSBox Games:**
- Install DOSBox Staging via Flathub
- Or use EmuDeck/RetroDECK for pre-configured setup
- GOG/Steam installers work via Proton

### macOS (Sonoma/Sequoia)

**Apple Silicon (M1/M2/M3/M4):**
- ScummVM: Native ARM64 build available
- DOSBox Staging: Native ARM64 build available
- CrossOver: Version 25+ for Windows games
- Boxer-CE: macOS-native DOSBox wrapper

**Gatekeeper Issues:**
Right-click applications and select "Open" to bypass unsigned app warnings.

### Linux

- **ScummVM**: Available via Flatpak, Snap, or distribution packages
- **DOSBox Staging**: Flatpak recommended for latest version
- **Wine/Proton**: For Windows 95/98 era games

---

## Troubleshooting Common Issues

### "I Don't Have the Manual"

Many Sierra games use copy protection requiring the physical manual.

**Solutions:**
- GOG versions include PDF manuals
- [ReplacementDocs](https://www.replacementdocs.com/) archives game manuals
- [The Sierra Chest](https://www.sierrachest.com/) has manual scans
- In-game "look up word" protection can often be bypassed with online searches

### Sound Issues

**No Music:**
- Check sound driver configuration in DOS games
- Ensure ScummVM audio drivers are set correctly
- For MT-32, enable "True Roland MT-32" in ScummVM options

**Crackling/Stuttering:**
- Increase audio buffer size in emulator settings
- Lower quality settings if using software synthesis

### Speed Problems

**Game Too Fast:**
- In DOSBox: Lower `cycles` value (try `cycles=10000`)
- In ScummVM: Use built-in game speed options

**Game Too Slow:**
- In DOSBox: Increase `cycles` value or use `cycles=max`
- Check that you're using 64-bit emulator versions

### Graphics Issues

**Stretched/Wrong Aspect Ratio:**
- Enable "Aspect ratio correction" in ScummVM
- In DOSBox: Set `aspect=true` in config

**Modern Monitor Issues:**
- Use ScummVM's built-in scalers
- DOSBox Staging has automatic CRT shaders

---

## Where to Buy Sierra Games

### Digital Storefronts

| Store | Pros | Cons |
|-------|------|------|
| **GOG.com** | DRM-free, includes manuals, pre-configured | Missing some VGA remakes |
| **Steam** | VGA remakes included, sales | May need Proton/extraction |
| **Xbox Game Pass** | Sierra classics via Antstream Arcade | Streaming only, limited selection |

### Physical Copies

- **eBay** — Big box originals, check disc condition
- **Local game stores** — Increasingly rare
- **Estate sales** — Occasional finds

See [[Buying Guide]] for detailed purchasing recommendations.

---

## Essential Resources

### Community Sites

- **[SierraHelp.com](https://www.sierrahelp.com/)** — Patches, installers, troubleshooting
- **[The Sierra Chest](https://www.sierrachest.com/)** — Manuals, documentation, history
- **[SpaceQuest.net](https://spacequest.net/)** — Space Quest specific resources
- **[Quest for More Glory](https://www.questformoreglory.com/)** — QFG tools and guides

### Technical Resources

- **[ScummVM Documentation](https://docs.scummvm.org/)** — Official setup guides
- **[DOSBox Staging Wiki](https://github.com/dosbox-staging/dosbox-staging/wiki)** — Configuration reference
- **[PCGamingWiki](https://www.pcgamingwiki.com/)** — Game-specific fixes

### Fan Remakes

If you want enhanced versions of classic games:
- **[AGD Interactive](https://www.agdinteractive.com/)** — King's Quest I, KQ2+, Quest for Glory II VGA
- **[Infamous Adventures](https://www.infamous-adventures.com/)** — King's Quest III, Space Quest II VGA

---

## See Also

- [[Compatibility Guide]] — Detailed technical reference
- [[Buying Guide]] — Where to purchase Sierra games
- [[Engine Index]] — Which engine each game uses
- [[Fan Resources]] — Community sites and fan projects

---

## References

[^ref-1]: [ScummVM Compatibility List](https://www.scummvm.org/compatibility/) — Official game support status
[^ref-2]: [DOSBox Staging](https://www.dosbox-staging.org/) — Modern DOSBox fork features
[^ref-3]: [ScummVM on Steam Deck](https://docs.scummvm.org/en/latest/other_platforms/steamdeck.html) — Installation guide
[^ref-4]: [SierraHelp.com](https://www.sierrahelp.com/) — Community patches and installers
[^ref-5]: [GOG.com Sierra Collections](https://www.gog.com/games?publishers=sierra-entertainment) — Digital storefronts
[^ref-6]: [dgVoodoo2](http://dege.freeweb.hu/dgVoodoo2/) — DirectX wrapper for old games
[^ref-7]: [OTVDM](https://github.com/nicfab/otvdm) — 16-bit Windows app compatibility layer
