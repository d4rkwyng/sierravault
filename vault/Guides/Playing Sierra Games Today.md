---
title: "Playing Sierra Games Today"
type: guide
last_updated: "2026-10-26"
---
# Playing Sierra Games Today

<small style="color: gray">Last updated: October 26, 2026</small>

A guide to running Sierra's classic games on modern computers and handhelds. Whether you're revisiting childhood favorites or discovering these adventures for the first time, this guide will get you playing. Store contents, prices and ScummVM support levels below were checked on October 16, 2026 (GOG single titles on October 26, 2026), and can change.

---

## Quick Start: Which Method Should I Use?

| Game Type | Recommended Method | Difficulty |
|-----------|-------------------|------------|
| AGI adventures (1984–1989) | **ScummVM** | Easy ⭐ |
| SCI adventures (1988–1996) | **ScummVM** | Easy ⭐ |
| Dynamix adventures (Rise of the Dragon, etc.) | **ScummVM** | Easy ⭐ |
| Gobliiins 1–3 | **ScummVM** | Easy ⭐ |
| Flight sims (Red Baron, Aces) | **DOSBox Staging** | Medium ⭐⭐ |
| Strategy (Caesar, Lords of the Realm) | **DOSBox Staging** | Medium ⭐⭐ |
| Windows 95/98 games (QFG5, KQ:MoE, GK3) | **GOG/Steam + patches** (KQ:MoE is GOG-only: it is in GOG's King's Quest 7+8, and Steam's King's Quest Collection excludes it)[^ref-26][^ref-30] | Medium ⭐⭐ |
| Sports sims (NASCAR, Front Page Sports) | **DOSBox Staging** | Medium ⭐⭐ |
| 3D Ultra series | **Windows** (official updates on SierraHelp)[^ref-39] | Medium ⭐⭐ |

*Difficulty ratings are this guide's own rough estimate of setup effort.*

---

## Method 1: ScummVM (Recommended for Adventures)

ScummVM is a program that reimplements the game engines Sierra used, allowing their adventures to run natively on modern systems.

### Why ScummVM?

- **Simple setup** — Add game files and ScummVM detects the game
- **Enhanced audio** — Roland MT-32 (with your own MT-32 ROMs) and General MIDI support[^ref-9]
- **Cross-platform** — Windows, macOS, Linux and more[^ref-8]

### Supported Sierra Games

ScummVM's compatibility list for the current release (2026.4.0) rates most Sierra SCI games **Excellent** and the AGI games **Good**; a few SCI titles are also rated Good, as noted below.[^ref-1]

**AGI Engine Games (1984–1989), rated Good (King's Quest II: Excellent):**[^ref-1]
- King's Quest I–IV (original AGI versions)
- Space Quest I–II
- Leisure Suit Larry 1 (original)
- Police Quest 1 (original)
- Manhunter 1–2
- Gold Rush!
- Mixed-Up Mother Goose (original)
- Donald Duck's Playground
- The Black Cauldron

**SCI Engine Games (1988–1996), rated Excellent unless marked:**[^ref-1]
- King's Quest I SCI remake, King's Quest IV (SCI version), King's Quest V–VI, King's Quest VII (Good)
- Space Quest I VGA remake, Space Quest III–V, Space Quest 6 (Good)
- Leisure Suit Larry 1 VGA remake, Leisure Suit Larry 2, 3, 5, 6 and 7
- Police Quest 1 VGA remake, Police Quest 2–3, Police Quest IV (Good), Police Quest: SWAT (Good)
- Quest for Glory I–IV (including the QFG1 VGA remake)
- Gabriel Knight 1 and Gabriel Knight 2: The Beast Within
- Laura Bow 1–2
- Conquests of Camelot and Longbow
- EcoQuest 1–2
- Freddy Pharkas
- Pepper's Adventures in Time
- Phantasmagoria (Good) and Phantasmagoria 2: A Puzzle of Flesh
- Lighthouse (Good)
- Torin's Passage
- Shivers

**Dynamix Games (rated Good):**[^ref-1]
- Rise of the Dragon
- Heart of China
- The Adventures of Willy Beamish

**Coktel Vision Games (rated Excellent):**[^ref-1]
- Gobliiins trilogy
- Lost in Time
- Woodruff and the Schnibble
- Fascination
- Urban Runner
- Ween: The Prophecy

### Setting Up ScummVM

**Step 1: Download ScummVM**
Visit [scummvm.org/downloads](https://www.scummvm.org/downloads/) and download for your platform:[^ref-8]
- Windows
- macOS (10.13+, for Intel and Apple Silicon)
- Linux (Flatpak, Snap, or distribution packages)

**Step 2: Obtain Game Files**
You need the original game data files. Sources include:
- **GOG.com** — DRM-free, includes manuals
- **Steam** — Usually needs file extraction
- **Original discs** — Copy files from CD/floppy

**Step 3: Add Games**[^ref-41]
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
- **Roland MT-32 emulation** is built in, but "you must provide the original MT-32 ROMs"; they "are copyrighted, and are not provided by ScummVM."[^ref-9]

---

## Method 2: DOSBox Staging (For Simulations & Strategy)

DOSBox Staging is a modern, enhanced fork of DOSBox, useful for the many Sierra games ScummVM doesn't support.

### Why DOSBox Staging?

Highlights from the project's own feature list:[^ref-2]
- **Authentic CRT emulation** — "Authentic, zero-config CRT emulation" that auto-adjusts to your display resolution
- **Roland MT-32 emulation** — Integrated, but it "requires the original ROM data from the hardware itself"; the ROMs can't be bundled, so you install them yourself[^ref-10]
- **FluidSynth integration** — Built-in General MIDI synth
- **Modern controller support** — 10-axis controllers, real-time joystick calibration
- **Sensible defaults** — "minimal manual configuration is needed"
- **64-bit dynamic recompilation** — for both ARM and x64, so it runs natively on Apple Silicon Macs and on x86-64 machines such as the Steam Deck[^ref-12]

### Games That Need DOSBox

- Red Baron (1990)
- Aces of the Pacific, Aces Over Europe, Aces of the Deep
- A-10 Tank Killer
- Metaltech: Earthsiege (1994)
- Front Page Sports (DOS-era entries)
- [[1996 - NASCAR Racing 2|NASCAR Racing 2]] (1996)
- [[1995 - IndyCar Racing II|IndyCar Racing II]] (1995)
- Caesar I–II
- Lords of the Realm I–II
- The Incredible Machine (DOS entries)
- Many other DOS sports and simulation titles

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

- **Check SierraHelp** — [SierraHelp.com](https://sierrahelp.com/) offers game installers, patches and technical help for running Sierra games on modern PCs[^ref-4]
- **Joystick calibration** — Flight sims need calibration; use `[joystick]` section in config
- **CPU cycles** — Adjust `cpu_cycles=` if games run too fast or slow (since DOSBox Staging 0.82.0 the legacy `cycles=` setting still works "for backward compatibility")[^ref-47]
- **Sound configuration** — Run `INSTALL.EXE` or `SETUP.EXE` in games to configure audio

---

## Method 3: GOG.com (Easiest Option)

GOG.com sells Sierra classics DRM-free with emulators pre-configured; its Space Quest 1+2+3 pack, for example, ships with ScummVM, updated to version 2026.1.0 in February 2026.[^ref-14]

### What GOG Provides

- Pre-configured emulators
- Original manuals (PDF)
- DRM-free installers
- Mostly Windows-only: the Sierra products below are Windows-only except the Leisure Suit Larry titles, which also run on macOS and Linux[^ref-18][^ref-19]

### Available Sierra Collections on GOG

Prices are US list prices as of October 16, 2026; the single titles from The Colonel's Bequest down were checked on October 26, 2026.

| Collection | Games Included | Price |
|------------|----------------|-------|
| [King's Quest 1+2+3](https://www.gog.com/en/game/kings_quest_1_2_3) | Original KQ1 (not the 1990 SCI remake), KQ2, KQ3[^ref-5] | $9.99 |
| [King's Quest 4+5+6](https://www.gog.com/en/game/kings_quest_4_5_6) | KQ4, KQ5, KQ6[^ref-25] | $9.99 |
| [King's Quest 7+8](https://www.gog.com/en/game/kings_quest_7_8) | KQ7, Mask of Eternity[^ref-26] | $9.99 |
| [Space Quest 1+2+3](https://www.gog.com/en/game/space_quest_1_2_3) | SQ1 (EGA and, since February 2026, VGA), SQ2, SQ3[^ref-14] | $9.99 |
| [Space Quest 4+5+6](https://www.gog.com/en/game/space_quest_4_5_6) | SQ4, SQ5, SQ6[^ref-27] | $9.99 |
| [Quest for Glory 1-5](https://www.gog.com/en/game/quest_for_glory) | QFG1–5; "Includes both: VGA and original version of Quest for Glory 1"[^ref-15] | $9.99 |
| [Police Quest Collection](https://www.gog.com/en/game/police_quest_collection) | PQ1–4[^ref-16] | $9.99 |
| [Police Quest: SWAT 1+2](https://www.gog.com/en/game/police_quest_swat_1_2) | Police Quest: SWAT, SWAT 2[^ref-17] | $9.99 |
| [Leisure Suit Larry](https://www.gog.com/en/game/leisure_suit_larry) | *Greatest Hits and Misses*: "five complete adventures"[^ref-18] | $9.99 |
| [Leisure Suit Larry: Love for Sail!](https://www.gog.com/en/game/leisure_suit_larry_love_for_sail) | LSL7[^ref-19] | $5.99 |
| [Gabriel Knight: Sins of the Fathers](https://www.gog.com/en/game/gabriel_knight_sins_of_the_fathers) | GK1[^ref-20] | $5.99 |
| [Gabriel Knight 2: The Beast Within](https://www.gog.com/en/game/gabriel_knight_2_the_beast_within) | GK2[^ref-21] | $5.99 |
| [Gabriel Knight 3](https://www.gog.com/en/game/gabriel_knight_3_blood_of_the_sacred_blood_of_the_damned) | GK3[^ref-22] | $5.99 |
| [Phantasmagoria](https://www.gog.com/en/game/phantasmagoria) | Phantasmagoria[^ref-23] | $9.99 |
| [Phantasmagoria 2: A Puzzle of Flesh](https://www.gog.com/en/game/phantasmagoria_2) | Phantasmagoria 2[^ref-24] | $5.99 |
| [The Colonel's Bequest](https://www.gog.com/en/game/the_colonels_bequest) | Laura Bow 1[^ref-49] | $5.99 |
| [The Dagger of Amon Ra](https://www.gog.com/en/game/the_dagger_of_amon_ra) | Laura Bow 2[^ref-50] | $5.99 |
| [Conquests of Camelot: The Search for the Grail](https://www.gog.com/en/game/conquests_of_camelot) | Conquests of Camelot[^ref-51] | $5.99 |
| [Conquests of the Longbow: The Legend of Robin Hood](https://www.gog.com/en/game/conquests_of_the_longbow) | Conquests of the Longbow[^ref-52] | $5.99 |
| [Shivers](https://www.gog.com/en/game/shivers) | Shivers[^ref-53] | $5.99 |
| [Shivers II: Harvest of Souls](https://www.gog.com/en/game/shivers_ii_harvest_of_souls) | Shivers II[^ref-54] | $5.99 |
| [Torin's Passage](https://www.gog.com/en/game/torins_passage) | Torin's Passage[^ref-55] | $5.99 |

### GOG Caveats

- **King's Quest I remake missing** — GOG's King's Quest 1+2+3 "Includes the original King's Quest", not the 1990 SCI remake[^ref-5]
- **Windows-only installers** — For macOS, run the game data in ScummVM instead
- **Bundled emulator versions** — GOG may bundle an older ScummVM or DOSBox than the current release; update manually if needed

---

## Method 4: Steam

### King's Quest I remake on Steam

The King's Quest I in Steam's King's Quest Collection is the 1990 SCI remake, which GOG's pack lacks.[^ref-31] PCGamingWiki lists both the EGA and VGA versions of Space Quest I in the Space Quest Collection; GOG's Space Quest 1+2+3 now has both too.[^ref-29][^ref-14]

### Available on Steam

US prices as of October 16, 2026:[^ref-28]
- [King's Quest Collection](https://store.steampowered.com/app/10100/) — "Seven classic games in one collection" (KQ1–7; PCGamingWiki: all King's Quest games "excluding King's Quest 8")[^ref-30], $19.99
- [Space Quest Collection](https://store.steampowered.com/app/10110/) — SQ1–6, $19.99
- [Quest for Glory 1-5](https://store.steampowered.com/app/502750/) — $9.99
- [Police Quest Collection](https://store.steampowered.com/app/494740/) — $9.99
- [Gabriel Knight: Sins of the Fathers](https://store.steampowered.com/app/495700/), [The Beast Within](https://store.steampowered.com/app/496760/) and [Gabriel Knight 3](https://store.steampowered.com/app/497360/) — sold separately, $5.99 each
- [Phantasmagoria](https://store.steampowered.com/app/501990/) ($9.99) and [Phantasmagoria 2](https://store.steampowered.com/app/501970/) ($5.99) — sold separately

### Running Steam Games with ScummVM

Steam versions can be extracted and run with ScummVM for better features:
1. Right-click game in Steam library
2. Select "Manage" → "Browse local files"
3. In ScummVM, click **Add Game** and select the folder that holds the game's data files[^ref-41]

---

## Method 5: Windows 95/98 Era Games

Windows games from 1995–2000 often need special handling. (Gabriel Knight 2 and Phantasmagoria 2 are Windows-era games too, but ScummVM runs them; see Method 1.)[^ref-1]

### Games Requiring Windows Compatibility

- [[1995 - 3-D Ultra Pinball|3-D Ultra Pinball]] (1995)
- [[1995 - Trophy Bass|Trophy Bass]] (1995)
- [[1996 - Earthsiege 2|Earthsiege 2]] (1996)
- [[1997 - Red Baron II|Red Baron II]] (1997) and [[1998 - Red Baron 3D|Red Baron 3D]] (1998)
- Shivers 2 (1997)
- Quest for Glory V: Dragon Fire (1998)
- King's Quest: Mask of Eternity (1998)
- SWAT 2 (1998)
- Caesar III (1998)
- Gabriel Knight 3: Blood of the Sacred, Blood of the Damned (1999)
- Pharaoh (1999)
- [[1999 - Starsiege|Starsiege]] (1999)
- Zeus: Master of Olympus (2000)

### Running Windows 95/98 Games

**Option 1: dgVoodoo2 (for 3D games)**
[dgVoodoo2](http://dege.freeweb.hu/dgVoodoo2/) implements Glide 2.11–3.1 and DirectX 1–7 (plus Direct3D 8.1/9) on modern Direct3D:[^ref-6]
1. Download dgVoodoo2 (latest release as of October 2026: v2.87.6, released October 25)[^ref-46]
2. Copy the 32-bit DLLs from the `MS\x86` folder (D3D8, D3D9, D3DImm, DDraw), or from `3Dfx\x86` for Glide games, into the game folder; the DirectX DLLs only work as a local installation in the game's folder, never in a system folder[^ref-46][^ref-45][^ref-44]
3. Run dgVoodooCpl.exe (the dgVoodoo Control Panel) to configure[^ref-44]

**Option 2: Virtual Machine**
For stubborn titles, run Windows 98/XP in:
- VirtualBox
- VMware
- PCem (for period-accurate emulation)

### Common Windows 95/98 Issues

| Problem | Solution |
|---------|----------|
| 16-bit installer fails | Use [OTVDM](https://github.com/otya128/winevdm) (runs 16-bit Windows programs on 64-bit Windows)[^ref-7] or SierraHelp installers |

---

## Platform-Specific Guides

### Steam Deck

**For ScummVM Games:**
1. Install ScummVM from Flathub in Desktop Mode: `flatpak install flathub org.scummvm.ScummVM`[^ref-3]
2. In ScummVM's Launcher, click **Add Game** and select the folder that holds the game's data files[^ref-41]
3. To launch ScummVM from Gaming Mode, open the Steam client in Desktop Mode, click "add a game", then "add a Non-Steam game", and pick ScummVM from the list[^ref-40]
4. ScummVM's **Keymaps** tab (Global Options) can assign actions to keyboard keys, mouse buttons or joystick buttons[^ref-42]

**For DOSBox Games:**
- Install DOSBox Staging via Flathub (`io.github.dosbox-staging`)[^ref-38]
- RetroDECK runs DOS games through RetroArch's DOSBox Pure core[^ref-43]
- GOG/Steam installers work via Proton

### macOS

**Apple Silicon:**
- ScummVM: one macOS build for Intel and Apple Silicon[^ref-8]
- DOSBox Staging: ARM 64-bit dynamic recompilation[^ref-2]
- CrossOver: commercial Wine-based option for Windows games
- Boxer: the original Boxer DOS front end has an Apple Silicon fork by MaddTheSane, released as betas[^ref-13]

**Gatekeeper Issues:**
Since macOS Sequoia (15), Control-click → Open no longer overrides Gatekeeper for apps that aren't signed or notarized.[^ref-11] Try to open the app first, then open **System Settings > Privacy & Security**, scroll down and click **Open Anyway**.[^ref-48]

### Linux

- **ScummVM**: Available via Flatpak, Snap, or distribution packages[^ref-8]
- **DOSBox Staging**: Available on Flathub[^ref-38]
- **Wine/Proton**: For Windows 95/98 era games

---

## Troubleshooting Common Issues

### "I Don't Have the Manual"

Many Sierra games use copy protection requiring the physical manual.

**Solutions:**
- GOG versions include PDF manuals
- [ReplacementDocs](https://www.replacementdocs.com/) archives game manuals[^ref-37]
- [The Sierra Chest](https://web.archive.org/web/20250809090332/https://sierrachest.com/) has a "Manuals & inserts" section (live site currently blocks automated access; Wayback link)[^ref-36]
- In-game "look up word" protection can often be bypassed with online searches

### Sound Issues

**No Music:**
- Check sound driver configuration in DOS games
- Ensure ScummVM audio drivers are set correctly
- For MT-32 in ScummVM, put your own MT-32 ROMs in the game folder or extrapath and choose the MT-32 emulator as the music device; ScummVM enables True Roland MT-32 mode automatically[^ref-9]

**Crackling/Stuttering:**
- Increase audio buffer size in emulator settings
- Lower quality settings if using software synthesis

### Speed Problems

**Game Too Fast:**
- In DOSBox Staging: Lower the `cpu_cycles` value (try `cpu_cycles=10000`)[^ref-47]

**Game Too Slow:**
- In DOSBox Staging: Increase the `cpu_cycles` value or use `cpu_cycles=max`[^ref-47]
- Check that you're using 64-bit emulator versions

### Graphics Issues

**Stretched/Wrong Aspect Ratio:**
- Enable "Aspect ratio correction" in ScummVM
- DOSBox Staging already gives "Aspect ratio correct output" by default[^ref-2]

**Modern Monitor Issues:**
- Use ScummVM's built-in scalers
- DOSBox Staging has zero-config CRT emulation[^ref-2]

---

## Where to Buy Sierra Games

### Digital Storefronts

| Store | Pros | Cons |
|-------|------|------|
| **GOG.com** | DRM-free, includes manuals, pre-configured | KQ1 pack lacks the 1990 remake; mostly Windows-only |
| **Steam** | KQ Collection includes the 1990 KQ1 remake | May need Proton/extraction |
| **Xbox Game Pass** | Retro Classics app, made with Antstream Arcade, with Activision-owned classics including Space Quest titles[^ref-32][^ref-33] | Streaming only, limited selection |

### Physical Copies

- **eBay** — Big box originals, check disc condition
- **Local game stores** — Increasingly rare
- **Estate sales** — Occasional finds

See [[Buying Guide]] for detailed purchasing recommendations.

---

## Essential Resources

### Community Sites

- **[SierraHelp.com](https://sierrahelp.com/)** — Patches, installers, troubleshooting[^ref-4]
- **[The Sierra Chest](https://web.archive.org/web/20250809090332/https://sierrachest.com/)** — Manuals, documentation, history[^ref-36]
- **[SpaceQuest.net](https://spacequest.net/)** — Space Quest specific resources

### Technical Resources

- **[ScummVM Documentation](https://docs.scummvm.org/)** — Official setup guides
- **[DOSBox Staging Wiki](https://github.com/dosbox-staging/dosbox-staging/wiki)** — Configuration reference
- **[PCGamingWiki](https://www.pcgamingwiki.com/)** — Game-specific fixes

### Fan Remakes

If you want enhanced versions of classic games:
- **[AGD Interactive](https://www.agdinteractive.com/)** — King's Quest I, King's Quest II: Romancing the Stones, King's Quest III Redux, Quest for Glory II[^ref-34]
- **[Infamous Adventures](https://infamousadventures.itch.io/)** — King's Quest III and Space Quest II VGA remakes (infamous-adventures.com now redirects to itch.io)[^ref-35]

---

## See Also

- [[Compatibility Guide]] — Detailed technical reference
- [[Buying Guide]] — Where to purchase Sierra games
- [[Engine Index]] — Which engine each game uses
- [[Fan Resources]] — Community sites and fan projects

---

## References

[^ref-1]: [ScummVM Compatibility List – 2026.4.0](https://www.scummvm.org/compatibility/2026.4.0/) — Per-game support levels, e.g. "agi:kq1 Good", "sci:gk2 Excellent", "sci:phantasmagoria2 Excellent", "dgds:rise Good"
[^ref-2]: [DOSBox Staging](https://www.dosbox-staging.org/) — Feature list: "Authentic zero-config CRT emulation", "Integrated Roland MT-32 emulation", "Built-in FluidSynth MIDI synth", "Modern 10-axis controller support", "64-bit dynamic recompilation for improved performance (ARM & x64)"; "Aspect ratio correct output & image captures by default"
[^ref-3]: [Flathub – ScummVM](https://flathub.org/apps/org.scummvm.ScummVM) — Flatpak package org.scummvm.ScummVM
[^ref-4]: [The Sierra Help Pages](https://sierrahelp.com/) — "a collection of tips, help, tools and patches to get your games running on newer, faster computers"; game installers section
[^ref-5]: [GOG – King's Quest 1+2+3](https://www.gog.com/en/game/kings_quest_1_2_3) — "Includes the original King's Quest: Quest for the Crown, King's Quest II... and King's Quest III"; $9.99; Windows
[^ref-6]: [dgVoodoo2](http://dege.freeweb.hu/dgVoodoo2/) — Implements "Glide 2.11, Glide 2.45, Glide 3.1 and Glide 3.1 Napalm", "DirectX 1-7", Direct3D 8.1 and 9
[^ref-7]: [OTVDM / winevdm](https://github.com/otya128/winevdm) — "16-bit Windows (Windows 1.x, 2.x, 3.0, 3.1, etc.) on 64-bit Windows"
[^ref-8]: [ScummVM – Downloads](https://www.scummvm.org/downloads/) — Version 2026.4.0; "macOS 10.13+ for Intel and Apple Silicon"; Windows installer and zip; Flatpak, Snap and distribution packages
[^ref-9]: [ScummVM Documentation – Understanding the audio settings](https://docs.scummvm.org/en/latest/advanced_topics/understand_audio.html) — "you must provide the original MT-32 ROMs"; "You don't need to enable True Roland MT-32 in the MT-32 tab, ScummVM does this automatically"
[^ref-10]: [DOSBox Staging manual – Roland MT-32](https://www.dosbox-staging.org/0.83/manual/sound/sound-devices/roland-mt-32/) — "Emulating the Roland MT-32 requires the original ROM data from the hardware itself"
[^ref-11]: [Apple Developer – Updates to runtime protection in macOS Sequoia](https://developer.apple.com/news/?id=saqachfa) — August 6, 2024: "users will no longer be able to Control-click to override Gatekeeper... They'll need to visit System Settings > Privacy & Security"
[^ref-12]: [Steam Deck – Tech Specs](https://www.steamdeck.com/en/tech) — "AMD APU CPU: Zen 2 4c/8t" (x86-64)
[^ref-13]: [MaddTheSane/Boxer – Releases (GitHub)](https://github.com/MaddTheSane/Boxer/releases) — "Apple Silicon beta" through "Apple Silicon beta 4.1"
[^ref-14]: [GOG – Space Quest 1+2+3](https://www.gog.com/en/game/space_quest_1_2_3) — Changelog (20 February 2026): "Updated ScummVM to version 2026.1.0. Space Quest 1: Added VGA version of the game"; $9.99
[^ref-15]: [GOG – Quest for Glory 1-5](https://www.gog.com/en/game/quest_for_glory) — "Includes both: VGA and original version of Quest for Glory 1"; $9.99
[^ref-16]: [GOG – Police Quest Collection](https://www.gog.com/en/game/police_quest_collection) — Police Quest 1–4 (Pursuit of the Death Angel, The Vengeance, The Kindred, Open Season); $9.99
[^ref-17]: [GOG – Police Quest: SWAT 1+2](https://www.gog.com/en/game/police_quest_swat_1_2) — "Pack includes Darryl F. Gates' Police Quest: SWAT and Police Quest: SWAT 2"; $9.99
[^ref-18]: [GOG – Leisure Suit Larry](https://www.gog.com/en/game/leisure_suit_larry) — "Leisure Suit Larry's Greatest Hits and Misses features ... five complete adventures"; $9.99; Windows, macOS, Linux
[^ref-19]: [GOG – Leisure Suit Larry: Love for Sail!](https://www.gog.com/en/game/leisure_suit_larry_love_for_sail) — $5.99; Windows, macOS, Linux
[^ref-20]: [GOG – Gabriel Knight: Sins of the Fathers](https://www.gog.com/en/game/gabriel_knight_sins_of_the_fathers) — $5.99
[^ref-21]: [GOG – Gabriel Knight 2: The Beast Within](https://www.gog.com/en/game/gabriel_knight_2_the_beast_within) — $5.99
[^ref-22]: [GOG – Gabriel Knight 3: Blood of the Sacred, Blood of the Damned](https://www.gog.com/en/game/gabriel_knight_3_blood_of_the_sacred_blood_of_the_damned) — $5.99
[^ref-23]: [GOG – Phantasmagoria](https://www.gog.com/en/game/phantasmagoria) — $9.99 (first game only)
[^ref-24]: [GOG – Phantasmagoria 2: A Puzzle of Flesh](https://www.gog.com/en/game/phantasmagoria_2) — $5.99
[^ref-25]: [GOG – King's Quest 4+5+6](https://www.gog.com/en/game/kings_quest_4_5_6) — $9.99
[^ref-26]: [GOG – King's Quest 7+8](https://www.gog.com/en/game/kings_quest_7_8) — "Includes King's Quest 7: The Princeless Bride and King's Quest 8: Mask of Eternity"; $9.99
[^ref-27]: [GOG – Space Quest 4+5+6](https://www.gog.com/en/game/space_quest_4_5_6) — $9.99
[^ref-28]: [Steam – King's Quest Collection](https://store.steampowered.com/app/10100/) — "Seven classic games in one collection"; $19.99. Other prices from the Steam store pages linked in the list (Space Quest Collection $19.99; QFG 1-5 and Police Quest Collection $9.99; GK1–3 $5.99 each; Phantasmagoria $9.99; Phantasmagoria 2 $5.99)
[^ref-29]: [PCGamingWiki – Space Quest I: Roger Wilco in The Sarien Encounter](https://www.pcgamingwiki.com/wiki/Space_Quest_I:_Roger_Wilco_in_The_Sarien_Encounter) — Steam Space Quest Collection: "EGA and VGA versions"; GOG space_quest_1_2_3: EGA and VGA versions
[^ref-30]: [PCGamingWiki – King's Quest: Quest for the Crown](https://www.pcgamingwiki.com/wiki/King%27s_Quest) — Steam King's Quest Collection: "Comes bundled with all other King's Quest games (excluding King's Quest 8)"
[^ref-31]: [Gamezebo – King's Quest I review (Wayback, 2013)](http://web.archive.org/web/20131113034647/http://www.gamezebo.com:80/games/kings-quest-i-quest-crown/review) — "The version of King's Quest included in the King's Quest Collection is an updated version from 1990"
[^ref-32]: [IGN – Microsoft Announces Retro Classics With Game Pass](https://www.ign.com/articles/microsoft-announces-retro-classics-with-game-pass-kicks-things-off-with-over-50-activision-games-from-the-80s-and-90s) — May 21, 2025: "a collaboration with Antstream Arcade to bring a collection of over 50 classic Activision games"
[^ref-33]: [TrueAchievements – Retro Classics September 2025 update](https://www.trueachievements.com/news/xbox-game-pass-retro-classics-september-2025) — "adds four more games to the streaming service, including the two Space Quest titles"
[^ref-34]: [AGD Interactive – Games](https://www.agdinteractive.com/games/games.html) — "AGDI's King's Quest I remake was the first since 1990"; homepage news: "King's Quest III Redux Released", "Quest for Glory II v2.0 released", previous remake "King's Quest II: Romancing the Stones"
[^ref-35]: [Infamous Adventures – itch.io](https://infamousadventures.itch.io/) — "Space Quest II VGA Remake", "King's Quest III VGA Remake"
[^ref-36]: [The Sierra Chest (Wayback, 2025-08-09)](https://web.archive.org/web/20250809090332/https://sierrachest.com/) — Menu includes "Manuals & inserts"
[^ref-37]: [ReplacementDocs](https://www.replacementdocs.com/) — "The original web archive of game manuals"
[^ref-38]: [Flathub – DOSBox Staging](https://flathub.org/apps/io.github.dosbox-staging) — Flatpak package io.github.dosbox-staging
[^ref-39]: [SierraHelp – 3-D Ultra Series Updates](https://sierrahelp.com/Patches-Updates/Patches-Updates-Games/3-DUltraSeriesUpdates.html) — official updates, e.g. "This file will update Cool Pool to version 1.01"; "This file updates Lionel Train Town 1.0 to 1.1"
[^ref-40]: [Steam Support – Steam Deck and Steam Machine Desktop: FAQ](https://help.steampowered.com/en/faqs/view/671A-4453-E8D2-323C) — "click the 'add a game' button in the lower left corner, click 'add a Non-Steam game', then find the application you installed in the list"
[^ref-41]: [ScummVM Documentation – Adding and playing a game](https://docs.scummvm.org/en/latest/use_scummvm/add_play_games.html) — "In the Launcher window, click Add Game"; "highlight the game by clicking on it, and then click Start"
[^ref-42]: [ScummVM Documentation – Keymaps](https://docs.scummvm.org/en/latest/settings/keymaps.html) — "Use the Keymaps tab to assign actions to keyboard keys or shortcuts, or to mouse or joystick buttons"
[^ref-43]: [RetroDECK Wiki – RetroArch general guide](https://retrodeck.readthedocs.io/en/latest/wiki_multi_emulator_guides/retroarch/retroarch-guide/) — DOS system mapped to the DOSBox Pure core
[^ref-44]: [dgVoodoo2 – General Readme](http://dege.freeweb.hu/dgVoodoo2/ReadmeGeneral/) — "you can either use dgVoodoo Control Panel (dgVoodooCpl) or edit it manually"; "For native usage you always need the 32bit (x86) version dlls"
[^ref-45]: [dgVoodoo2 – DirectX Readme](http://dege.freeweb.hu/dgVoodoo2/ReadmeDirectX/index.html) — "NEVER COPY DDRAW.DLL, D3D8.DLL and D3D9.DLL INTO SYSTEM FOLDERS!! ALWAYS USE A LOCAL INSTALLATION FOR A GAME!"; dgVoodoo's d3dimm.dll holds Direct3D up to version 7
[^ref-46]: [dgVoodoo2 – Release 2.87.6 (GitHub)](https://github.com/dege-diosg/dgVoodoo2/releases/tag/2.87.6) — released 25 Oct 2026; the dgVoodoo2_87_6.zip archive holds dgVoodooCpl.exe, MS/x86 (D3D8.dll, D3D9.dll, D3DImm.dll, DDraw.dll) and 3Dfx/x86 (Glide DLLs)
[^ref-47]: [DOSBox Staging – 0.82.0 release notes](https://www.dosbox-staging.org/download/release-notes/0.82.0/) — "cpu_cycles — Global or real mode only cycles setting"; "The legacy cycles setting is still available for backward compatibility with existing configs"
[^ref-48]: [Apple Support – Safely open apps on your Mac](https://support.apple.com/en-us/102445) — "Open System Settings. Click Privacy & Security, scroll down, and click the Open Anyway button"
[^ref-49]: [GOG – The Colonel's Bequest](https://www.gog.com/en/game/the_colonels_bequest) — live store page; US price $5.99; Windows (GOG product and price API, checked 2026-10-26)
[^ref-50]: [GOG – The Dagger of Amon Ra](https://www.gog.com/en/game/the_dagger_of_amon_ra) — live store page; US price $5.99; Windows (GOG product and price API, checked 2026-10-26)
[^ref-51]: [GOG – Conquests of Camelot: The Search for the Grail](https://www.gog.com/en/game/conquests_of_camelot) — live store page; US price $5.99; Windows (GOG product and price API, checked 2026-10-26)
[^ref-52]: [GOG – Conquests of the Longbow: The Legend of Robin Hood](https://www.gog.com/en/game/conquests_of_the_longbow) — live store page; US price $5.99; Windows (GOG product and price API, checked 2026-10-26)
[^ref-53]: [GOG – Shivers](https://www.gog.com/en/game/shivers) — live store page; US price $5.99; Windows (GOG product and price API, checked 2026-10-26)
[^ref-54]: [GOG – Shivers II: Harvest of Souls](https://www.gog.com/en/game/shivers_ii_harvest_of_souls) — live store page; US price $5.99; Windows (GOG product and price API, checked 2026-10-26)
[^ref-55]: [GOG – Torin's Passage](https://www.gog.com/en/game/torins_passage) — live store page; US price $5.99; Windows (GOG product and price API, checked 2026-10-26)
