---
title: "Adventure Game Interpreter (AGI)"
type: technology
developer: "Sierra On-Line"
years_active: "1984-1989"
total_games: 15
last_updated: "2026-01-12"
---

# Adventure Game Interpreter (AGI)

<small style="color: gray">Last updated: January 12, 2026</small>

## Overview

The Adventure Game Interpreter (AGI) was Sierra On-Line's first standardized game engine, developed in 1984 to power King's Quest: Quest for the Crown. Originally created as a showcase for IBM's PCjr computer, AGI established the template for graphic adventure games and powered Sierra's output through the late 1980s. The engine's ability to display animated characters moving through graphical environments was revolutionary for its time, effectively creating the graphic adventure genre.

AGI games are characterized by their 160×200 resolution, 16-color graphics, text parser interface, and distinctive pseudo-3D perspective that allowed characters to walk in front of and behind background objects.

## Technical Specifications

| Specification | Details |
|---------------|---------|
| Resolution | 160×200 pixels |
| Color Depth | 16 colors (EGA palette) |
| Graphics Modes | EGA, CGA, VGA, Hercules, MCGA, Tandy |
| Interface | Text parser (typed commands) |
| Audio | PC Speaker, Tandy 3-voice, Apple IIgs 15-voice |
| Memory Required | 256KB RAM |
| Distribution | Floppy disk (typically 3-6 disks) |

## Graphics System

### Pseudo-3D Environment
AGI created a distinctive visual style where characters could walk both horizontally and vertically, with the engine automatically determining whether objects appeared in front of or behind the character based on their Y-position on screen. This created an illusion of depth that was groundbreaking for 1984.

### Drawing Priority
The engine used a priority screen system where different colors represented different depth planes. Artists drew separate "visual" and "priority" screens, with the priority screen controlling which objects appeared in front of others.

### Character Animation
Sprites were limited to 3 frames of animation for each direction (left, right, front, back), creating the characteristic "puppet walk" motion familiar to players of classic Sierra games.

## Audio Capabilities

AGI's audio support varied significantly by platform:

| Platform | Audio Capability |
|----------|------------------|
| IBM PC | Single-voice PC Speaker (beeps and tones) |
| Tandy 1000 | 3-voice audio chip |
| Apple IIgs | 15-voice stereo soundtrack |
| Amiga | 4-channel stereo |
| Atari ST | 3-voice audio |
| Macintosh | Single-channel audio |

The Apple IIgs versions are often considered definitive due to their significantly enhanced soundtracks composed specifically for that platform's superior audio hardware.

## Interface Evolution

### Early Text Parser (1984-1986)
Players typed verb-noun combinations to interact:
- `LOOK TREE`
- `GET SWORD`
- `TALK MAN`
- `OPEN DOOR`

The parser understood approximately 1,000 words per game, with responses ranging from helpful to humorously sarcastic.

### Pull-Down Menus (1987)
Later AGI games added optional pull-down menus for common commands like Save, Restore, and Inventory, reducing reliance on memorizing keyboard shortcuts.

## Games Using AGI

### King's Quest Series
- [[1984 - King's Quest - Quest for the Crown]] - AGI debut
- [[1985 - King's Quest II - Romancing the Throne]]
- [[1986 - King's Quest III - To Heir Is Human]]
- [[1988 - King's Quest IV - The Perils of Rosella]] - Dual AGI/SCI release

### Space Quest Series
- [[1986 - Space Quest - The Sarien Encounter]]
- [[1987 - Space Quest II - Vohaul's Revenge]] - Last major AGI release

### Other AGI Games
- [[1987 - Police Quest - In Pursuit of the Death Angel]]
- [[1987 - Leisure Suit Larry in the Land of the Lounge Lizards]]
- [[1988 - Gold Rush]]
- [[1987 - Mixed-Up Mother Goose]]
- [[1989 - Manhunter - San Francisco]]
- [[1986 - The Black Cauldron]]
- [[1984 - Donald Duck's Playground]]
- [[1984 - Mickey's Space Adventure]]

## Technical Innovations

### First Digitized Speech
AGI was capable of basic digitized audio, used sparingly due to memory constraints. Space Quest's alarm klaxon was among the first digitized sounds in a Sierra game.

### Cross-Platform Architecture
The AGI interpreter was designed for portability, allowing Sierra to release games on multiple platforms with consistent gameplay. This business model became standard practice for Sierra throughout the 1980s and 1990s.

### Save/Restore System
AGI introduced Sierra's signature save game system, essential given the games' high difficulty and frequent player deaths.

## Limitations

### Resolution Constraints
The 160×200 resolution (doubled horizontally to display at 320×200) limited detail in character art and backgrounds, though artists like Mark Crowe and Douglas Herring achieved remarkable results within these constraints.

### Parser Frustrations
The text parser often failed to recognize synonyms or alternate phrasings, leading to the infamous "I don't understand" responses that frustrated many players. Sierra's SCI engine would address these issues with point-and-click interfaces.

### Memory Management
With only 256KB RAM available, AGI games couldn't store large amounts of data simultaneously, requiring frequent disk swapping and limiting soundtrack complexity.

## Transition to SCI

By 1988, AGI's limitations became apparent as competitors released more visually sophisticated games. Sierra developed the Sierra Creative Interpreter (SCI) to address these shortcomings:

| Feature | AGI | SCI |
|---------|-----|-----|
| Resolution | 160×200 | 320×200 |
| Colors | 16 | 256 |
| Interface | Text parser | Point-and-click |
| Audio | Limited | Sound card support |
| Sprites | 3 frames | Smooth animation |

King's Quest IV (1988) was released in both AGI and SCI versions, marking the transition period. After 1989, Sierra abandoned AGI for all new development.

## Legacy

### Fan Development
The AGI engine has been thoroughly documented by fans, leading to:
- **AGI Studio** - Fan tool for creating AGI games
- **NAGI** - Open-source AGI interpreter
- **ScummVM** - Full AGI support for modern systems

### Preservation
All AGI games are playable today through ScummVM, which provides accurate emulation across all modern platforms including Windows, macOS, Linux, iOS, and Android.

### Historical Significance
AGI established Sierra's dominance in the adventure game market and created design conventions that influenced the entire genre. The engine's text parser, death mechanics, and save system became industry standards.

## Playing AGI Games Today

### Recommended Method
- **ScummVM** - Best compatibility and quality-of-life features
- Available on GOG.com and Steam with ScummVM pre-configured

### Tips for Modern Players
- Save frequently (Sierra games are unforgiving)
- Keep notes on parser vocabulary that works
- Use walkthrough assistance sparingly - half the fun is experimentation
- Apple IIgs music patches available for enhanced audio

## See Also

- [[Sierra Creative Interpreter]] - AGI's successor engine
- [[King's Quest Series]] - Flagship AGI series
- [[Space Quest Series]] - Sci-fi comedy series
- [[Roberta Williams]] - AGI pioneer
