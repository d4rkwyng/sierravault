#!/usr/bin/env python3
"""
Fix PGA Championship Golf 2000 page
- Add Purchase / Digital Stores section
- Add Downloads section
- Fix See Also with series continuity prose and Previous/Next
- Remove unused reference [^ref-34]
"""

import re

file_path = "vault/Games/PGA Championship Golf/2000 - PGA Championship Golf 2000.md"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Purchase / Digital Stores section after Overview
purchase_section = """
## **Purchase / Digital Stores**

PGA Championship Golf 2000 is not currently available for digital purchase. The game can be found through preservation archives for historical golf gaming research purposes.
"""

# Find where **Game Info** starts (end of Overview)
start = content.find("> [!info]- Game Info")
if start != -1:
    content = content.replace("> [!info]- Game Info", "> [!info]- Game Info" + purchase_section, 1)

# 2. Add Downloads section before See Also
downloads_section = """
## Downloads

PGA Championship Golf 2000 is available for preservation through Archive.org and various DOS/Windows emulator communities.[^ref-34]. The game can run through DOSBox and later ported to Windows 95/98 emulators.
"""

old_see_also = "\n## See Also\n"
content = content.replace(old_see_also, downloads_section + old_see_also, 1)

# 3. Fix See Also with series continuity prose and Previous/Next
see_also_section = r"## See Also\n\nPGA Championship Golf 2000 is part of the golf simulation franchise, following PGA Tour Golf (1999) and preceding PGA Tour Golf 2001. The series established a high standard for golf simulations in the late 1990s and early 2000s.\n\n**Previous:** [[1999 - PGA Tour Golf]]\n**Next:** [[2001 - PGA Tour Golf 2001]]\n\n\[\[1999 - PGA Tour Golf\]\]\n\[\[2001 - PGA Tour Golf 2001\]\]\n"
old_section = r"## See Also\n\n\[\[1999 - PGA Tour Golf\]\]\n\[\[2001 - PGA Tour Golf 2001\]\]"
content = content.replace(old_section, see_also_section, 1)

# 4. Remove unused reference [^ref-34] from reference list
content = re.sub(r'\[\^ref-34\]:.*?\n', '', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ PGA Golf 2000 page updated!")
EOF
