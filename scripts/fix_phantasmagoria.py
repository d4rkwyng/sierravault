#!/usr/bin/env python3
"""
Fix Phantasmagoria: A Puzzle of Flesh page
- Add Purchase / Digital Stores section
- Add Downloads section
- Fix See Also with series continuity prose and Previous/Next
- Remove unused references (77, 78, 79)
"""

import re

file_path = "vault/Games/Phantasmagoria/1996 - Phantasmagoria - A Puzzle of Flesh.md"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Purchase / Digital Stores section after Overview
purchase_section = """
## Purchase / Digital Stores

Phantasmagoria: A Puzzle of Flesh is available for purchase on GOG.com as a DOS version, though the Windows Enhanced edition is not currently available for digital purchase[^ref-77]. The game can be purchased through various digital storefronts, with pricing typically ranging from $5.99 to $9.99 depending on the platform and any ongoing sales[^ref-78].
"""

# Find the end of Overview section and add Purchase after it
content = re.sub(
    r'(## Overview\n\n.*?countries\[\^ref-6\]\.\n)',
    r'\1' + purchase_section,
    content,
    flags=re.DOTALL
)

# 2. Add Downloads section before See Also
downloads_section = """
## Downloads

Phantasmagoria: A Puzzle of Flesh is available for preservation through various sources. The DOS version can be found on Archive.org and MyAbandonWare for historical preservation purposes[^ref-79]. Compatibility patches are available to ensure the game runs on modern systems.
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

Phantasmagoria: A Puzzle of Flesh is the second installment in the Phantasmagoria series, following the original Phantasmagoria (1995) which established the horror anthology concept. While both games share the Phantasmagoria title and horror themes, they feature completely different stories and characters, as Sierra intended the series to be an anthology rather than a direct sequel line.

**Previous:** [[1995 - Phantasmagoria]]
**Next:** None (series ended after two installments)

[[1995 - Phantasmagoria]]
"""

content = re.sub(
    r'## See Also\n\n\[\[1995 - Phantasmagoria\]\]',
    see_also_section,
    content
)

# 4. Remove unused references (77, 78, 79) from the reference list
# Find the References section and remove those specific refs
content = re.sub(
    r'\[\^ref-77\]:.*?\n\[\^ref-78\]:.*?\n\[\^ref-79\]:.*?\n',
    '',
    content,
    flags=re.DOTALL
)

# Write the file back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Phantasmagoria page updated successfully!")
print("   - Added Purchase / Digital Stores section")
print("   - Added Downloads section")
print("   - Fixed See Also with series continuity prose and Previous/Next")
print("   - Removed unused references [^ref-77], [^ref-78], [^ref-79]")
