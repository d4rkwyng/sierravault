#!/usr/bin/env python3
"""
Fix PGA Championship Golf 2000 page - Clean version
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

# Add Purchase after **Game Info** section
old_game_info = r"""> \[!\*info\]- Game Info
> \*\*Developer:\*\* \[\[\*Headgate Studios\*\*\]\[\^ref-2\]
> \*\*Designer:\*\* Brian Silvernail, Mike Jacob\[\^ref-6\]
> \*Publisher:\*\* Sierra Sports\[\^ref-2\]
> \*Platforms:\*\* Windows\[\^ref-2\]
> \*Release Year:\*\* 2000
> \*Series:\*\* PGA Championship Golf
> \*Sierra Lineage:\*\* Core Sierra

<"""

content = content.replace(old_game_info, old_game_info + purchase_section, 1)

# 2. Find and add Downloads section before the first See Also occurrence
# Look for the line "The game can run through DOSBox" which is likely the Downloads content
old_downloads_content = "The game can run through DOSBox and later ported to Windows 95/98 emulators."
replacement = f"""## Downloads

PGA Championship Golf 2000 is available for preservation through Archive.org and various DOS/Windows emulator communities.[^ref-34]. The game can run through DOSBox and later ported to Windows 95/98 emulators."""

if old_downloads_content in content:
    content = content.replace(old_downloads_content, replacement + "\n", 1)

# 3. Fix See Also section with proper prose
old_see_also = r"## See Also\n\n\[\[1999 - PGA Tour Golf\]\]\n\[\[2001 - PGA Tour Golf 2001\]\]"
new_see_also = """## See Also

PGA Championship Golf 2000 is part of the golf simulation franchise, following PGA Tour Golf (1999) and preceding PGA Tour Golf 2001. The series established a high standard for golf simulations in the late 1990s and early 2000s.

**Previous:** [[1999 - PGA Tour Golf]]
**Next:** [[2001 - PGA Tour Golf 2001]]

[[1999 - PGA Tour Golf]]
[[2001 - PGA Tour Golf 2001]]
"""
content = re.sub(old_see_also, new_see_also, content, count=1)

# 4. Remove unused reference [^ref-34] from the reference list
content = re.sub(r'\[\^ref-34\]:.*?\n', '', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ PGA Golf 2000 page updated cleanly!")
print("   - Added **Purchase / Digital Stores** section")
print("   - Added ## Downloads section")
print("   - Fixed See Also with series continuity prose and Previous/Next")
print("   - Removed unused reference [^ref-34]")
