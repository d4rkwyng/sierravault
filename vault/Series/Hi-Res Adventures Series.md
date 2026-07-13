---
title: "Hi-Res Adventures Series"
type: series_overview
created_by: "Roberta Williams"
developer: "On-Line Systems / Sierra On-Line"
first_release: 1980
last_release: 1984
total_games: 12
genre: "Adventure (pre-AGI)"
last_updated: "2026-07-13"
---

# Hi-Res Adventures Series

<small style="color: gray">Last updated: July 13, 2026</small>

## Overview

The Hi-Res Adventures series is the foundational catalog of [[Roberta Williams|Roberta Williams's]] adventure-game design career and the original release line that built **On-Line Systems** (later [[Sierra On-Line]]) from a Williams-family side project into the dominant adventure-game publisher of the early 1980s.[^ref-1] Spanning 1980 to 1983, the series produced **seven numbered Hi-Res Adventures** plus a handful of sibling Hi-Res-branded sports/casino titles and one franchise-licensed entry. Mystery House (1980) is widely cited as the **first home computer adventure game with graphics** — predating the AGI engine, the [[Adventure Game Interpreter|AGI]]-era *King's Quest*, and effectively founding the graphic-adventure genre.[^ref-2]

The Hi-Res Adventures predated Sierra's [[Adventure Game Interpreter|AGI]] standardized engine — each title was a hand-crafted BASIC + 6502 assembly program with custom vector-drawing routines for the Apple II's high-resolution graphics mode (hence "Hi-Res").[^ref-3] This meant slower development, more platform-specific quirks, and no walking character — but the visual leap from text-only adventures (Adventure, Zork) was the genre-defining moment. By 1983 the engine model had outgrown the format, leading directly to AGI and *King's Quest* in 1984.[^ref-4]

## Series Timeline

### Numbered Hi-Res Adventures (1980–1983)

| Year | Number | Title | Designer | Notes |
|------|--------|-------|----------|-------|
| 1980 | 0 | [[1980 - Hi-Res Adventure 0 - Mission Asteroid\|Mission Asteroid]] | Roberta Williams | Originally numbered 0; intended as beginner-level intro |
| 1980 | 1 | [[1980 - Hi-Res Adventure 1 - Mystery House\|Mystery House]] | Roberta Williams | **Founding entry — first computer adventure with graphics** |
| 1980 | 2 | [[1980 - Hi-Res Adventure 2 - The Wizard and the Princess\|The Wizard and the Princess]] | Roberta Williams | First color-graphics adventure; the company's first major hit |
| 1981 | 3 | [[1981 - Hi-Res Adventure 3 - Cranston Manor\|Cranston Manor]] | Bob Davis | Williams gave the engine reins to another designer |
| 1981 | 4 | [[1981 - Hi-Res Adventure 4 - Ulysses and the Golden Fleece\|Ulysses and the Golden Fleece]] | Bob Davis | Greek mythology setting |
| 1982 | 5 | [[1982 - Hi-Res Adventure 5 - Time Zone\|Time Zone]] | Roberta Williams | Six-disk magnum opus — the most ambitious Hi-Res entry |
| 1983 | 6 | [[1983 - Hi-Res Adventure 6 - The Dark Crystal\|The Dark Crystal]] | Roberta Williams | Final numbered entry; licensed from Henson |

### Hi-Res-branded sibling titles (1980–1984)

| Year | Title | Designer | Type |
|------|-------|----------|------|
| 1980 | [[1980 - Hi-Res Cribbage\|Hi-Res Cribbage]] | Warren Schwader | Card game (Schwader's hire-bait) |
| 1980 | [[1980 - Hi-Res Football\|Hi-Res Football]] | Bob Davis | Sports |
| 1980 | [[1980 - Hi-Res Soccer\|Hi-Res Soccer]] | Bob Davis | Sports |
| 1982 | [[1982 - Adventure in Serenia\|Adventure in Serenia]] | Roberta Williams | Wizard and the Princess SNES/IBM port (renamed for legal reasons) |
| 1984 | [[1984 - Gelfling Adventure\|Gelfling Adventure]] | Roberta Williams (writing) | Dark Crystal licensed follow-up (educational/kids) |

## Mystery House (1980) — the founding entry

[[1980 - Hi-Res Adventure 1 - Mystery House|Mystery House]] is the most historically significant entry in the entire Sierra catalog. Roberta Williams designed it in early 1980 after playing *Colossal Cave Adventure* on the family Apple II and recognizing the genre's potential. Ken Williams programmed the engine. The game shipped in May 1980 on cassette tapes Ken hand-duplicated.[^ref-5]

**Key innovations:**
- **First adventure game with graphics** — line-art illustrations of each room accompanied the text parser interface.
- **Mystery genre** — Inspired by Agatha Christie's *And Then There Were None* (eight characters trapped in a haunted Victorian mansion, picked off one by one).
- **Self-published distribution** — Williams family sold copies via the original Sierra catalog and mail-order.
- **~10,000 copies sold in its first year** at $24.95 retail, generating ~$167,000 in revenue — enough to capitalize what became On-Line Systems / Sierra.[^ref-6]

The game's commercial success enabled the Williams to scale up: rent office space, hire Warren Schwader and Bob Davis, and build the Hi-Res Adventures product line.

## The Wizard and the Princess (1980)

Roberta Williams's second adventure and the company's first major commercial hit. Set in the fairy-tale kingdom of Serenia, the game added **color graphics** and a much more expansive world than Mystery House. Sold approximately 60,000 copies and was the title that funded Sierra's mid-1981 office relocation from the Williams home to Coarsegold/Oakhurst.[^ref-7]

Notably, the IBM PC port of *Wizard and the Princess* was renamed [[1982 - Adventure in Serenia|Adventure in Serenia]] (1982) to avoid trademark issues with IBM's own "wizard" branding.[^ref-8]

## Time Zone (1982) — the magnum opus

[[1982 - Hi-Res Adventure 5 - Time Zone|Time Zone]] (1982) was Roberta Williams's most ambitious Hi-Res Adventure. Spanning **39 game regions across multiple historical periods and the future**, the game shipped on **six 5.25-inch floppy disks** — the largest single computer game ever released at the time. The design called for traveling through Ancient Egypt, Medieval Europe, the American Wild West, and a far-future space-faring civilization, all interconnected via a time-travel mechanic.[^ref-9]

The game was ahead of its time technically (it pushed the Apple II's storage to its limits) but commercially less successful than its predecessors — too sprawling and difficult for the audience that had loved Wizard and the Princess. Time Zone marked the practical limit of the per-title custom-engine approach and pushed Sierra toward the standardized [[Adventure Game Interpreter|AGI]] development model.[^ref-10]

## The Dark Crystal (1983) and franchise licensing

[[1983 - Hi-Res Adventure 6 - The Dark Crystal|The Dark Crystal]] (1983) — the final numbered Hi-Res Adventure — adapted Jim Henson's 1982 film to interactive format under a Henson Studios license. The game was followed by the more child-oriented [[1984 - Gelfling Adventure|Gelfling Adventure]] (1984), expanding the Dark Crystal property.[^ref-11]

After *The Dark Crystal* and the 1983-1984 industry crash, Sierra ended the Hi-Res Adventures branding. The team began work on the new [[Adventure Game Interpreter|AGI]] engine that would launch with [[1984 - King's Quest - Quest for the Crown|King's Quest]] in 1984 — and the Hi-Res name was retired.

## Technical innovations and limitations

Each Hi-Res Adventure was a custom Apple II program. The engine model had distinctive characteristics:

- **Vector-drawn graphics** — Each room's illustration was stored as a sequence of drawing commands (move, draw, fill) rather than a bitmap. This kept storage small (typically <1KB per room) but rendered slowly.
- **Text parser interface** — Two-word commands ("go north", "take key"). No character on screen — the player observed each room as a static illustration.
- **6502 assembly + Applesoft BASIC** — Per-title custom code; no shared engine.
- **No animation** — Static scenes only.
- **Apple II + later Apple II GS, Atari 8-bit, IBM PC ports** — though each port required substantial rewrites.[^ref-12]

The lack of a standardized engine was both the era's strength (each title could push Apple II hardware in unique ways) and its limitation (no code reuse meant new games took 6-12 months per release). The arrival of [[Adventure Game Interpreter|AGI]] in 1984 — a virtual-machine engine that abstracted platform-specific graphics and audio — was the direct successor to the Hi-Res approach.

## Critical reception and legacy

The Hi-Res Adventures were critically acclaimed in their era. Mystery House and Wizard and the Princess won "Game of the Year" recognition from Softalk magazine (the leading Apple II publication of the time).[^ref-13] By 1982, every Hi-Res entry to date had received favorable reviews in Softalk, Computer Gaming World, and Compute! Magazine.[^ref-14]

The series's lasting legacy:

1. **Founding the graphic-adventure genre** — Mystery House (1980) is universally cited as the first; Wizard and the Princess (1980) demonstrated commercial viability.
2. **Capitalizing Sierra** — The series's revenue funded the company's growth from a Williams home business to a major publisher.
3. **Establishing Roberta Williams's design career** — Her 1980-1983 Hi-Res output is what made her possible as a designer through the AGI/SCI eras.
4. **Pre-establishing series-thinking** — Hi-Res Adventures were numbered 0-6, an early example of franchise-style sequential branding that would carry into King's Quest, Space Quest, etc.

Mystery House was inducted into [[Awards|various retrospective Hall of Fame]] recognitions; Roberta Williams was specifically honored at The Game Awards 2014 (Industry Icon Award) for her Hi-Res Adventures founding work alongside her later catalog.[^ref-15]

## See Also

- [[Roberta Williams]] — Series creator (5 of 7 numbered entries)
- [[Ken Williams]] — Original programmer; co-founder of On-Line Systems
- **Bob Davis** — Hi-Res Adventure 3 and 4 designer; early On-Line employee
- [[Warren Schwader]] — Cribbage designer; On-Line's first hired programmer
- [[Sierra On-Line]] — Successor company name
- [[Adventure Game Interpreter]] — The engine that succeeded the per-title approach
- [[Timeline 1980-1999]] — Year-by-year founding-era context
- [[Corporate Lineage|Corporate Lineage]] — On-Line Systems → Sierra On-Line transition

## References

[^ref-1]: [Wikipedia — Hi-Res Adventures](https://en.wikipedia.org/wiki/Hi-Res_Adventure) — Series overview
[^ref-2]: [Smithsonian Magazine — Roberta Williams](https://www.smithsonianmag.com/smart-news/1980s-roberta-williams-brought-graphic-adventure-games-home-180962160/) — Mystery House as founding adventure-with-graphics
[^ref-3]: [The Digital Antiquarian — Hi-Res Adventures](https://www.filfre.net/2011/12/sierras-launch/) — Engine architecture history
[^ref-4]: [Wikipedia — Adventure Game Interpreter](https://en.wikipedia.org/wiki/Adventure_Game_Interpreter) — AGI as Hi-Res successor
[^ref-5]: [Adventure Classic Gaming — Mystery House](http://www.adventureclassicgaming.com/index.php/site/reviews/mystery_house/) — Founding-entry analysis
[^ref-6]: Ken Williams, *Not All Fairy Tales Have Happy Endings* (2020) — Sales figures and revenue context
[^ref-7]: [The Digital Antiquarian — Wizard and the Princess](https://www.filfre.net/2011/12/sierras-launch/) — Sales and office-move context
[^ref-8]: [MobyGames — Adventure in Serenia](https://www.mobygames.com/game/3242/adventure-in-serenia/) — IBM port renaming
[^ref-9]: [Wikipedia — Time Zone (video game)](https://en.wikipedia.org/wiki/Time_Zone_(video_game)) — Six-disk production details
[^ref-10]: [Hardcore Gaming 101 — Sierra On-Line](http://www.hardcoregaming101.net/sierra-on-line/) — Time Zone retrospective
[^ref-11]: [Wikipedia — The Dark Crystal (video game)](https://en.wikipedia.org/wiki/The_Dark_Crystal_(video_game)) — Henson license
[^ref-12]: [Sierra Help Wiki — Hi-Res era engines](https://wiki.sierrahelp.com/index.php/Hi-Res_Adventures) — Technical reference
[^ref-13]: [Softalk Magazine archives](https://archive.org/details/softalkv01-v04) — Era reviews
[^ref-14]: [Computer Gaming World Museum](https://www.cgwmuseum.org) — Era CGW review collection
[^ref-15]: [The Game Awards 2014 — Industry Icon](https://thegameawards.com) — Williams recognition
[^ref-16]: [The Strong Museum — Mystery House Hall of Fame](https://www.museumofplay.org) — Museum recognition
[^ref-17]: [Halcyon Days — Warren Schwader interview](https://dadgum.com/halcyon/BOOK/SCHWADER.HTM) — Era context from a contemporary
