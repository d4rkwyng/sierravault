#!/bin/bash
# Re-crawl files that need render=true
# Generated: 2026-01-08

source .venv/bin/activate
source .env

echo "Re-crawling 163 files with render=true..."


# === wiki.scummvm.org (45 files) ===
python3 crawl_with_render.py "https://wiki.scummvm.org/index.php/Gabriel_Knight_3_Blood_Of_The_Sacred_Blood_Of_The_Damned" --game "gabriel-knight-3-blood-of-the-sacred-blood-of-the-damned"
sleep 2
python3 crawl_with_render.py "https://wiki.scummvm.org/index.php/Gabriel_Knight_Sins_Of_The_Fathers" --game "gabriel-knight-sins-of-the-fathers"
sleep 2
python3 crawl_with_render.py "https://wiki.scummvm.org/index.php/Gabriel_Knight_Sins_Of_The_Fathers_20Th_Anniversary_Edition" --game "gabriel-knight-sins-of-the-fathers-20th-anniversary-edition"
sleep 2
python3 crawl_with_render.py "https://wiki.scummvm.org/index.php/King's_Quest_I" --game "kings-quest-i-vga-remake"
sleep 2
python3 crawl_with_render.py "https://wiki.scummvm.org/index.php/King's_Quest_II" --game "kings-quest-ii-romancing-the-throne"
sleep 2

# === www.gamesdatabase.org (36 files) ===
python3 crawl_with_render.py "https://www.gamesdatabase.org/game/commodore-amiga/african-raiders-01" --game "african-raiders-01"
sleep 2
python3 crawl_with_render.py "https://www.gamesdatabase.org/game/arcade/koukuu-kihei-monogatari-the-legend-of-air-cavalry" --game "air-cavalry"
sleep 2
python3 crawl_with_render.py "https://www.gamesdatabase.org/game/commodore-64/arcticfox" --game "arcticfox"
sleep 2
python3 crawl_with_render.py "https://www.gamesdatabase.org/game/atari-st/asterix-operation-getafix" --game "asterix-operation-getafix"
sleep 2
python3 crawl_with_render.py "https://www.gamesdatabase.org/game/microsoft-dos/bargon-attack" --game "bargon-attack"
sleep 2

# === kingsquest.fandom.com (20 files) ===
python3 crawl_with_render.py "https://kingsquest.fandom.com/wiki/King's_Quest_I" --game "kings-quest-i-vga-remake"
sleep 2
python3 crawl_with_render.py "https://kingsquest.fandom.com/wiki/King's_Quest_II" --game "kings-quest-ii-romancing-the-throne"
sleep 2
python3 crawl_with_render.py "https://kingsquest.fandom.com/wiki/Kings_Quest_Iii_Redux_To_Heir_Is_Human" --game "kings-quest-iii-redux-to-heir-is-human"
sleep 2
python3 crawl_with_render.py "https://kingsquest.fandom.com/wiki/Kings_Quest_V_Manual" --game "kings-quest-v-absence-makes-the-heart-go-yonder"
sleep 2
python3 crawl_with_render.py "https://kingsquest.fandom.com/wiki/Sales_data" --game "kings-quest-v-absence-makes-the-heart-go-yonder"
sleep 2

# === spacequest.fandom.com (20 files) ===
python3 crawl_with_render.py "https://spacequest.fandom.com/wiki/Space_Quest_0_Replicated" --game "space-quest-0-replicated"
sleep 2
python3 crawl_with_render.py "https://spacequest.fandom.com/wiki/Space_Quest_II" --game "space-quest-ii-vohauls-revenge"
sleep 2
python3 crawl_with_render.py "https://spacequest.fandom.com/wiki/The_Official_Guide_To_Roger_Wilco's_Space_Adventures" --game "space-quest-iii-the-pirates-of-pestulon"
sleep 2
python3 crawl_with_render.py "https://spacequest.fandom.com/wiki/Speech-enabled_Space_Quest" --game "space-quest-iii-the-pirates-of-pestulon"
sleep 2
python3 crawl_with_render.py "https://spacequest.fandom.com/wiki/Space_Quest_Collection" --game "space-quest-iii-the-pirates-of-pestulon"
sleep 2

# === wiki.sierrahelp.com (14 files) ===
python3 crawl_with_render.py "http://wiki.sierrahelp.com/index.php?title=King%27s_Quest_V:_Absence_Makes_the_Heart_Go_Yonder" --game "kings-quest-v-absence-makes-the-heart-go-yonder"
sleep 2
python3 crawl_with_render.py "https://wiki.sierrahelp.com/index.php/King's_Quest_V" --game "kings-quest-v-absence-makes-the-heart-go-yonder"
sleep 2
python3 crawl_with_render.py "http://wiki.sierrahelp.com/index.php?title=King's_Quest_7&redirect=no" --game "kings-quest-vii-the-princeless-bride"
sleep 2
python3 crawl_with_render.py "http://wiki.sierrahelp.com/index.php/King's_Quest_VII:_The_Princeless_Bride_Manual" --game "kings-quest-vii-the-princeless-bride"
sleep 2
python3 crawl_with_render.py "https://wiki.sierrahelp.com/index.php/King's_Quest_VII" --game "kings-quest-vii-the-princeless-bride"
sleep 2

# === policequest.fandom.com (5 files) ===
python3 crawl_with_render.py "https://policequest.fandom.com/wiki/Police_Quest_Iii_The_Kindred" --game "police-quest-iii-the-kindred"
sleep 2
python3 crawl_with_render.py "https://policequest.fandom.com/wiki/Police_Quest_In_Pursuit_Of_The_Death_Angel" --game "police-quest-in-pursuit-of-the-death-angel"
sleep 2
python3 crawl_with_render.py "https://policequest.fandom.com/wiki/PQ4CD_transcript" --game "police-quest-open-season"
sleep 2
python3 crawl_with_render.py "https://policequest.fandom.com/wiki/Police_Quest_Sci_Remake" --game "police-quest-sci-remake"
sleep 2
python3 crawl_with_render.py "https://policequest.fandom.com/wiki/Police_Quest_Swat_2" --game "police-quest-swat-2"
sleep 2

# === gamegrumps.fandom.com (3 files) ===
python3 crawl_with_render.py "https://gamegrumps.fandom.com/wiki/King's_Quest_V:_Absence_Makes_the_Heart_Go_Yonder!" --game "kings-quest-v-absence-makes-the-heart-go-yonder"
sleep 2
python3 crawl_with_render.py "https://gamegrumps.fandom.com/wiki/Space_Quest_III:_The_Pirates_of_Pestulon" --game "space-quest-iii-the-pirates-of-pestulon"
sleep 2
python3 crawl_with_render.py "https://gamegrumps.fandom.com/wiki/Space_Quest_IV:_Roger_Wilco_and_The_Time_Rippers" --game "space-quest-iv-roger-wilco-and-the-time-rippers"
sleep 2

# === tropedia.fandom.com (2 files) ===
python3 crawl_with_render.py "https://tropedia.fandom.com/wiki/King%27s_Quest_V" --game "kings-quest-v-absence-makes-the-heart-go-yonder"
sleep 2
python3 crawl_with_render.py "https://tropedia.fandom.com/wiki/King's_Quest_VII" --game "kings-quest-vii-the-princeless-bride"
sleep 2

# === sierra.fandom.com (2 files) ===
python3 crawl_with_render.py "https://sierra.fandom.com/wiki/King's_Quest_V:_Absence_Makes_the_Heart_Go_Yonder" --game "kings-quest-v-absence-makes-the-heart-go-yonder"
sleep 2
python3 crawl_with_render.py "https://sierra.fandom.com/wiki/King's_Quest_VII" --game "kings-quest-vii-the-princeless-bride"
sleep 2

# === questforglory.fandom.com (2 files) ===
python3 crawl_with_render.py "https://questforglory.fandom.com/wiki/Quest_For_Glory_Iii_Wages_Of_War" --game "quest-for-glory-iii-wages-of-war"
sleep 2
python3 crawl_with_render.py "https://questforglory.fandom.com/wiki/Space_Quest" --game "space-quest-iv-roger-wilco-and-the-time-rippers"
sleep 2

# === superfriends.fandom.com (1 files) ===
python3 crawl_with_render.py "https://superfriends.fandom.com/wiki/20,000_Leagues_Under_the_Sea" --game "20000-leagues-under-the-sea"
sleep 2

# === onceuponatime.fandom.com (1 files) ===
python3 crawl_with_render.py "https://onceuponatime.fandom.com/wiki/20,000_Leagues_Under_the_Sea" --game "20000-leagues-under-the-sea"
sleep 2

# === movies.fandom.com (1 files) ===
python3 crawl_with_render.py "https://movies.fandom.com/wiki/20,000_Leagues_Under_the_Sea_(1954_film)" --game "20000-leagues-under-the-sea"
sleep 2

# === disney.fandom.com (1 files) ===
python3 crawl_with_render.py "https://disney.fandom.com/wiki/Giant_Squid_(20,000_Leagues_Under_the_Sea)" --game "20000-leagues-under-the-sea"
sleep 2

# === bayonetta.fandom.com (1 files) ===
python3 crawl_with_render.py "https://bayonetta.fandom.com/wiki/Abracadabra" --game "abracadabra"
sleep 2

# === culture.fandom.com (1 files) ===
python3 crawl_with_render.py "https://culture.fandom.com/wiki/Abracadabra_(Steve_Miller_Band_song)" --game "abracadabra"
sleep 2

# === hi5tv.fandom.com (1 files) ===
python3 crawl_with_render.py "https://hi5tv.fandom.com/wiki/Abracadabra" --game "abracadabra"
sleep 2

# === justdance.fandom.com (1 files) ===
python3 crawl_with_render.py "https://justdance.fandom.com/wiki/Abracadabra" --game "abracadabra"
sleep 2

# === occult-resources.fandom.com (1 files) ===
python3 crawl_with_render.py "https://occult-resources.fandom.com/wiki/Abracadabra" --game "abracadabra"
sleep 2

# === gabrielknight.fandom.com (1 files) ===
python3 crawl_with_render.py "https://gabrielknight.fandom.com/wiki/Gabriel_Knight_Sins_Of_The_Fathers_20Th_Anniversary_Edition" --game "gabriel-knight-sins-of-the-fathers-20th-anniversary-edition"
sleep 2

# === sciwiki.sierrahelp.com (1 files) ===
python3 crawl_with_render.py "https://sciwiki.sierrahelp.com/index.php/King's_Quest_V:_Absence_Makes_the_Heart_Go_Yonder" --game "kings-quest-v-absence-makes-the-heart-go-yonder"
sleep 2

# === dynamix.fandom.com (1 files) ===
python3 crawl_with_render.py "https://dynamix.fandom.com/wiki/King's_Quest_VII" --game "kings-quest-vii-the-princeless-bride"
sleep 2

# === amiga.fandom.com (1 files) ===
python3 crawl_with_render.py "https://amiga.fandom.com/wiki/Space_Quest_III" --game "space-quest-iii-the-pirates-of-pestulon"
sleep 2

# === agiwiki.sierrahelp.com (1 files) ===
python3 crawl_with_render.py "http://agiwiki.sierrahelp.com/index.php?title=Space_Quest_Series" --game "space-quest-iii-the-pirates-of-pestulon"
sleep 2
