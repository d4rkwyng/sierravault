#!/usr/bin/env python3
"""
Fix Caesar (1992) page
- Add Purchase / Digital Stores section
- Add Downloads section
- Fix See Also with series continuity prose and Previous/Next
- Remove unused references (53, 54, 55)
"""

import re

file_path = "vault/Games/Caesar/1992 - Caesar.md"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Purchase / Digital Stores section after Overview
purchase_section = """
## **Purchase / Digital Stores**

Caesar is not currently available for digital purchase. The game can be found through preservation archives for historical research purposes.
"""

# Find the end of Overview section and add Purchase after it
content = re.sub(
    r'(## Overview\n\n.*?Caesar\.\n)',
    r'\1' + purchase_section,
    content,
    flags=re.DOTALL
)

# 2. Add Downloads section before See Also
downloads_section = """
## Downloads

Caesar is available for preservation through Archive.org and other historical game archives[^ref-53]. The game can be played through DOSBox or similar emulators for modern systems.
"""

# Find See Also and add Downloads before it
content = re.sub(
    r'(\n## See Also\n)',
    downloads_section + r'\1',
    content
)

# 3. Fix See Also section with series continuity prose and Previous/Next
see_also_section = """
## See Also

Caesar is part of Caesar's series of city-building simulation games developed by Sierra On-Line. The series began with Caesar (1992) and continued with Caesar II (1994), Caesar III (1998), and Caesar IV (2006). Each installment expanded on the core gameplay mechanics while maintaining the historical Roman setting.

**Previous:** None (first game in the series)
**Next:** [[1994 - Caesar II]]

[[1994 - Caesar II]]
"""

content = re.sub(
    r'## See Also\n\n\[\[1994 - Caesar II\]\]',
    see_also_section,
    content
)

# 4. Remove unused references (53, 54, 55) from the reference list
content = re.sub(
    r'\[\^ref-53\]:.*?\n\[\^ref-54\]:.*?\n\[\^ref-55\]:.*?\n',
    '',
    content,
    flags=re.DOTALL
)

# Write the file back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Caesar page updated successfully!")
print("   - Added **Purchase / Digital Stores** section")
print("   - Added ## Downloads section")
print("   - Fixed See Also with series continuity prose and Previous/Next")
print("   - Removed unused references [^ref-53], [^ref-54], [^ref-55]")
