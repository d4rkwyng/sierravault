#!/usr/bin/env python3
"""
Page Quality Scorer

Scores generated wiki pages based on quality criteria:
- Reference count and distribution (25 points)
- Section completeness (25 points)
- Content depth (25 points)
- Formatting and structure (25 points)

Usage:
    python3 score_page.py page.md
    python3 score_page.py /tmp/output/*.md  # Score multiple files
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Company name aliases - these are the same entity at different times
COMPANY_ALIASES = {
    'sierra': [
        'Sierra On-Line', 'Sierra On-Line, Inc.', 'Sierra On-Line Inc.',
        'Sierra Entertainment', 'Sierra Entertainment, Inc.', 'Sierra Entertainment Inc.',
        'Sierra', 'Sierra Studios',
    ],
    'activision': [
        'Activision', 'Activision Blizzard', 'Activision Publishing',
    ],
    'vivendi': [
        'Vivendi', 'Vivendi Universal', 'Vivendi Games', 'VU Games',
    ],
    'encore': [
        'Encore', 'Encore Software', 'Encore, Inc.', 'Encore Software, Inc.',
    ],
}

# Non-narrative genres that don't need Story Summary, Puzzles, or Structure sections
NON_NARRATIVE_GENRES = [
    # Card/Casino/Board games
    'casino', 'card', 'poker', 'blackjack', 'solitaire', 'board game', 'mahjong',
    'chess', 'crossword', 'word game', 'puzzle game', 'trivia',
    # Sports/Racing/Simulation
    'sports', 'racing', 'golf', 'football', 'baseball', 'basketball', 'soccer',
    'fishing', 'hunting', 'flight simulation', 'flight sim', 'driving',
    'pinball', 'pool', 'billiards',
    # City Building/Strategy/Management
    'city building', 'city-building', 'city builder', 'construction simulation',
    'tycoon', 'management simulation', 'business simulation', 'god game',
    'real-time strategy', 'rts', 'turn-based strategy', '4x',
    # Other non-narrative
    'screensaver', 'utility', 'educational', 'typing', 'math',
    'minigolf', 'mini golf', 'radio control', 'train', 'slot',
    # Multiplayer-only games
    'deathmatch', 'multiplayer', 'arena',
    # Arcade games
    'shooter', 'fixed shooter', 'arcade', 'action arcade',
]

# Series that are inherently non-narrative
NON_NARRATIVE_SERIES = [
    'hoyle', '3d ultra', '3-d ultra', 'front page sports', 'sierra pro pilot',
    'driver\'s education', 'pga championship', 'nascar', 'trophy bass',
    'you don\'t know jack', 'after dark', 'incredible machine',
    'crazy nick', 'jumpstart', 'dr. brain', 'power chess',
    # City builders / strategy (Impressions Games)
    'caesar', 'pharaoh', 'zeus', 'emperor', 'cleopatra', 'poseidon',
    'lords of the realm', 'lords of magic', 'robert e. lee',
    'outpost', 'earthsiege', 'starsiege', 'cyberstorm',
]


def detect_game_type(content: str, filepath: str = "") -> dict:
    """Detect game type for scoring adjustments.

    Returns dict with:
        - is_cancelled: True if CXL prefix
        - is_unreleased: True if TBD/TBA prefix
        - is_non_narrative: True if non-narrative genre
        - game_type: 'cancelled', 'unreleased', 'non_narrative', or 'standard'
    """
    result = {
        'is_cancelled': False,
        'is_unreleased': False,
        'is_non_narrative': False,
        'game_type': 'standard',
    }

    # Check filename for CXL/TBD/TBA prefixes
    if filepath:
        filename = Path(filepath).stem.lower()
        if filename.startswith('cxl ') or filename.startswith('cxl-'):
            result['is_cancelled'] = True
            result['game_type'] = 'cancelled'
        elif filename.startswith('tbd ') or filename.startswith('tbd-'):
            result['is_unreleased'] = True
            result['game_type'] = 'unreleased'
        elif filename.startswith('tba ') or filename.startswith('tba-'):
            result['is_unreleased'] = True
            result['game_type'] = 'unreleased'

    # Check series field in YAML
    series_match = re.search(r'series:\s*["\']?([^"\'\n]+)', content[:1000], re.IGNORECASE)
    if series_match:
        series = series_match.group(1).lower().strip()
        if series == 'cancelled':
            result['is_cancelled'] = True
            result['game_type'] = 'cancelled'

    # Check genre in YAML
    genre_match = re.search(r'genre:\s*["\']?([^"\'\n]+)', content[:1000], re.IGNORECASE)
    genre = genre_match.group(1).lower().strip() if genre_match else ''

    # Check title for series indicators
    title_match = re.search(r'title:\s*["\']?([^"\'\n]+)', content[:500], re.IGNORECASE)
    title = title_match.group(1).lower() if title_match else ''

    # Also check the filename for series indicators
    filename_lower = Path(filepath).stem.lower() if filepath else ''

    # Check for non-narrative genres
    for ng in NON_NARRATIVE_GENRES:
        if ng in genre:
            result['is_non_narrative'] = True
            if result['game_type'] == 'standard':
                result['game_type'] = 'non_narrative'
            break

    # Check for non-narrative series (in title or filename)
    if not result['is_non_narrative']:
        combined_text = f"{title} {filename_lower}"
        for ns in NON_NARRATIVE_SERIES:
            if ns in combined_text:
                result['is_non_narrative'] = True
                if result['game_type'] == 'standard':
                    result['game_type'] = 'non_narrative'
                break

    return result

def normalize_company_name(name: str) -> str:
    """Normalize company name to canonical form for comparison."""
    name_lower = name.lower().strip()
    for canonical, aliases in COMPANY_ALIASES.items():
        for alias in aliases:
            if alias.lower() == name_lower:
                return canonical
    return name_lower


def normalize_url(url: str) -> str:
    """Normalize URL for duplicate detection.
    
    Handles:
    - http/https variations
    - www/non-www variations
    - Trailing slashes
    - URL fragments
    - Common tracking parameters
    """
    url = url.strip()
    
    # Remove protocol differences
    url = re.sub(r'^https?://', '', url)
    
    # Remove www prefix
    url = re.sub(r'^www\.', '', url)
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    # Remove URL fragments
    url = url.split('#')[0]
    
    # Remove common tracking parameters
    if '?' in url:
        base, params = url.split('?', 1)
        # Parse and filter params
        param_list = params.split('&')
        filtered_params = []
        tracking_prefixes = ('utm_', 'ref', 'source', 'campaign', 'fbclid', 'gclid')
        for p in param_list:
            param_name = p.split('=')[0].lower()
            if not any(param_name.startswith(prefix) for prefix in tracking_prefixes):
                filtered_params.append(p)
        if filtered_params:
            url = base + '?' + '&'.join(filtered_params)
        else:
            url = base
    
    return url.lower()


def detect_series_folder(filepath: str) -> tuple:
    """Detect if a file is in a series folder.
    
    Returns:
        (is_in_series: bool, series_name: str or None, folder_path: str or None)
    """
    path = Path(filepath)
    
    # Folders that are NOT game series (studios, categories, misc)
    non_series_folders = {
        # Category/collection folders
        'standalone', 'arcade', 'education', 'fan games', 
        'spiritual successors', 'cancelled',
        # Developer/studio folders (not series)
        'dynamix', 'coktel', 'impressions', 'valve', 'monolith',
        # Category folders  
        'strategy', 'hi-res', 'after dark', 'sierra sports',
        # Non-narrative collections that don't need continuity
        'hoyle', '3d ultra', 'crazy nicks',
        # Single-game folders (not true series)
        'wizard of id',
    }
    
    # Check if in Games/SeriesName/ structure
    parts = path.parts
    try:
        games_idx = parts.index('Games')
        if games_idx < len(parts) - 2:  # Has subfolder after Games
            series_folder = parts[games_idx + 1]
            if series_folder.lower() not in non_series_folders:
                return (True, series_folder, str(Path(*parts[:games_idx + 2])))
    except ValueError:
        pass
    
    return (False, None, None)


def score_series_continuity(content: str, filepath: str) -> tuple:
    """Score series continuity and cross-references (max 10 bonus points).
    
    Checks:
    - See Also section exists for series games (with continuity prose)
    - Previous/Next links are present where applicable
    - At least one cross-reference to another game in series
    
    Returns:
        (score: int, issues: list)
    """
    score = 0
    issues = []
    
    is_in_series, series_name, folder_path = detect_series_folder(filepath)
    
    if not is_in_series:
        return (0, [])  # Not in a series, no bonus/penalty
    
    # Check for See Also section with continuity prose
    has_see_also = '## See Also' in content
    
    if has_see_also:
        score += 3
        
        # Extract See Also section content
        continuity_section = content.split('## See Also')[1]
        continuity_section = continuity_section.split('\n## ')[0] if '\n## ' in continuity_section else continuity_section[:2000]
        
        # Check for prose paragraph (not just navigation links)
        # Prose lines are non-empty, non-link lines (don't start with -)
        prose_lines = [l.strip() for l in continuity_section.split('\n')
                       if l.strip() and not l.strip().startswith('-') and not l.strip().startswith('[')]
        has_prose = any(len(l) > 50 for l in prose_lines)
        
        if not has_prose:
            issues.append("See Also section missing series continuity prose")
        
        has_previous = 'Previous' in continuity_section or '**←**' in continuity_section or '← ' in continuity_section
        has_next = 'Next' in continuity_section or '**→**' in continuity_section or '→ ' in continuity_section
        
        if has_previous or has_next:
            score += 2
        elif 'First game' not in continuity_section and 'final game' not in continuity_section.lower():
            issues.append("See Also section missing Previous/Next navigation")
    else:
        issues.append(f"Missing See Also section (game is in {series_name} folder)")
        score -= 5  # Penalty for missing See Also in series game
    
    # Check for wiki links to other games in the same series
    wiki_links = re.findall(r'\[\[([^\]|]+)', content)
    series_keywords = series_name.lower().replace("'", "").replace("'", "").split()
    
    series_references = 0
    for link in wiki_links:
        link_lower = link.lower()
        if any(kw in link_lower for kw in series_keywords if len(kw) > 2):
            series_references += 1
    
    if series_references >= 3:
        score += 3
    elif series_references >= 1:
        score += 1
    else:
        issues.append(f"No cross-references to other {series_name} games")
    
    return (score, issues)


def score_references(content: str, game_type: dict = None) -> Tuple[int, List[str]]:
    """Score reference usage (max 25 points).

    Args:
        content: Page content
        game_type: Dict from detect_game_type() with is_cancelled, is_unreleased, is_non_narrative
    """
    score = 0
    issues = []

    if game_type is None:
        game_type = {'is_cancelled': False, 'is_unreleased': False, 'is_non_narrative': False}

    # Count reference definitions
    ref_definitions = re.findall(r'^\[\^ref-(\d+)\]:', content, re.MULTILINE)
    ref_count = len(ref_definitions)

    # Count inline citations
    inline_refs = re.findall(r'\[\^ref-(\d+)\]', content)
    unique_inline = set(inline_refs)

    # Adjust thresholds for cancelled/unreleased games (limited info available)
    if game_type.get('is_cancelled') or game_type.get('is_unreleased'):
        # Lower thresholds: 10+ is great, 5+ is acceptable
        if ref_count >= 10:
            score += 10
        elif ref_count >= 5:
            score += 7
        elif ref_count >= 3:
            score += 4
            issues.append(f"Low reference count for cancelled/unreleased: {ref_count} (target: 5+)")
        else:
            score += 2
            issues.append(f"Very few references: {ref_count}")
    else:
        # Standard thresholds
        # Reference count scoring (max 10 points)
        if ref_count >= 20:
            score += 10
        elif ref_count >= 15:
            score += 7
            issues.append(f"Only {ref_count} references (target: 20+)")
        elif ref_count >= 10:
            score += 4
            issues.append(f"Low reference count: {ref_count} (target: 20+)")
        else:
            score += 1
            issues.append(f"Very few references: {ref_count} (target: 20+)")

    # Citation distribution (max 10 points)
    citation_count = len(inline_refs)
    if citation_count >= 30:
        score += 10
    elif citation_count >= 20:
        score += 8
    elif citation_count >= 10:
        score += 5
        issues.append(f"Low citation count: {citation_count} inline citations")
    else:
        score += 2
        issues.append(f"Very few citations: {citation_count}")

    # Citation diversity (max 5 points)
    diversity = len(unique_inline)
    if diversity >= 10:
        score += 5
    elif diversity >= 6:
        score += 3
    else:
        score += 1
        issues.append(f"Low citation diversity: only {diversity} unique refs cited")

    # Check for unused references (defined but never cited in body text)
    # Split content at ## References to only look at body
    body_content = content.split('## References')[0] if '## References' in content else content
    body_inline_refs = re.findall(r'\[\^ref-(\d+)\]', body_content)
    body_inline_nums = set(body_inline_refs)
    ref_def_nums = set(ref_definitions)
    unused_refs = ref_def_nums - body_inline_nums
    if unused_refs:
        score -= min(3, len(unused_refs))  # Max -3 penalty
        issues.append(f"Unused references: {', '.join(f'[^ref-{r}]' for r in sorted(unused_refs, key=int)[:3])}")

    # Check for duplicate reference definitions
    if len(ref_definitions) != len(set(ref_definitions)):
        from collections import Counter
        ref_counts = Counter(ref_definitions)
        duplicates = [f'[^ref-{r}]' for r, c in ref_counts.items() if c > 1]
        score -= min(3, len(duplicates))  # Max -3 penalty
        issues.append(f"Duplicate reference definitions: {', '.join(duplicates[:3])}")

    # Check for references without proper URLs (major quality issue)
    ref_section = content.split('## References')[-1] if '## References' in content else ''
    ref_lines = re.findall(r'^\[\^ref-\d+\]:\s*(.*)$', ref_section, re.MULTILINE)
    refs_without_urls = 0
    for ref_content in ref_lines:
        if ref_content.strip():
            # Should have either a markdown link or http URL
            has_url = 'http' in ref_content.lower() or re.search(r'\[.*?\]\(.*?\)', ref_content)
            if not has_url:
                refs_without_urls += 1
    if refs_without_urls > 0:
        penalty = min(10, refs_without_urls)  # Max -10 penalty
        score -= penalty
        issues.append(f"References without URLs (-{penalty}pts): {refs_without_urls} refs need proper links")

    # Check for duplicate source URLs in references (same source cited multiple times)
    ref_section = content.split('## References')[-1] if '## References' in content else ''
    ref_urls = re.findall(r'\]\((https?://[^\s\)]+)\)', ref_section)

    # Normalize URLs for comparison using enhanced normalization
    normalized_urls = [normalize_url(url) for url in ref_urls]

    from collections import Counter
    url_counts = Counter(normalized_urls)
    duplicate_urls = [(url, count) for url, count in url_counts.items() if count > 1]

    if duplicate_urls:
        # Penalty: -2 points per duplicate source (max -10)
        total_extra_refs = sum(count - 1 for _, count in duplicate_urls)
        penalty = min(10, total_extra_refs * 2)
        score -= penalty

        # Show top duplicate domains
        dupe_domains = []
        for url, count in sorted(duplicate_urls, key=lambda x: -x[1])[:3]:
            domain = url.split('/')[2] if len(url.split('/')) > 2 else url
            dupe_domains.append(f"{domain} ({count}x)")
        issues.append(f"Duplicate source URLs (-{penalty}pts): {', '.join(dupe_domains)}")

    return score, issues


def score_sections(content: str, game_type: dict = None) -> Tuple[int, List[str]]:
    """Score section completeness (max 25 points).

    Args:
        content: Page content
        game_type: Dict from detect_game_type() with is_cancelled, is_unreleased, is_non_narrative
    """
    score = 0
    issues = []

    if game_type is None:
        game_type = {'is_cancelled': False, 'is_unreleased': False, 'is_non_narrative': False}

    # Base required sections for all games
    required_sections = [
        ('## Overview', 3),
        ('## Story Summary', 3),
        ('## Gameplay', 3),
        ('### Interface', 2),
        ('### Structure', 2),
        ('### Puzzles', 2),
        ('## Reception', 3),
        ('## Legacy', 3),
        ('## Downloads', 2),
        ('## References', 2),
    ]

    # Sections to skip for non-narrative games (casino, sports, pinball, etc.)
    non_narrative_skip = ['## Story Summary', '### Puzzles', '### Structure']

    # Sections to skip for cancelled/unreleased games
    cancelled_skip = ['## Downloads', '### Interface', '### Structure', '### Puzzles']
    unreleased_skip = ['## Downloads', '## Reception', '### Interface', '### Structure', '### Puzzles']

    # Determine which sections to skip
    skip_sections = set()
    if game_type.get('is_non_narrative'):
        skip_sections.update(non_narrative_skip)
    if game_type.get('is_cancelled'):
        skip_sections.update(cancelled_skip)
    if game_type.get('is_unreleased'):
        skip_sections.update(unreleased_skip)

    for section, points in required_sections:
        if section in skip_sections:
            # Give full points for skipped sections (they don't apply)
            score += points
        elif section in content:
            score += points
        else:
            issues.append(f"Missing section: {section}")

    # Check for thin sections (section exists but has minimal content)
    sections_to_check = ['## Overview', '## Reception', '## Development', '## Legacy']
    for section in sections_to_check:
        if section in content:
            # Find section content (between this header and next ## header)
            section_start = content.find(section)
            next_section = content.find('\n## ', section_start + len(section))
            if next_section == -1:
                next_section = len(content)
            section_content = content[section_start:next_section]

            # Count words in section (excluding header)
            section_words = len(section_content.split()) - 2  # subtract header words
            if section_words < 50:
                score -= 2
                issues.append(f"Thin section: {section} has only ~{section_words} words")

    # Check that Reception section has citations
    if '## Reception' in content:
        reception_start = content.find('## Reception')
        next_section = content.find('\n## ', reception_start + 12)
        if next_section == -1:
            next_section = len(content)
        reception_content = content[reception_start:next_section]
        reception_citations = len(re.findall(r'\[\^ref-\d+\]', reception_content))
        if reception_citations < 3:
            score -= 2
            issues.append(f"Reception section needs more citations (has {reception_citations})")

    return score, issues


def score_content_depth(content: str) -> Tuple[int, List[str]]:
    """Score content depth and specificity (max 25 points)."""
    score = 0
    issues = []

    # Word count (max 5 points)
    words = len(content.split())
    if words >= 2500:
        score += 5
    elif words >= 1500:
        score += 4
    elif words >= 1000:
        score += 3
        issues.append(f"Short content: {words} words (target: 2500+)")
    else:
        score += 1
        issues.append(f"Very short: {words} words")

    # Specific details - years (max 3 points)
    years = re.findall(r'\b(19[0-9]{2}|20[0-2][0-9])\b', content)
    if len(years) >= 10:
        score += 3
    elif len(years) >= 5:
        score += 2
    else:
        score += 1
        issues.append("Few specific years mentioned")

    # Specific details - names/proper nouns (max 3 points)
    # Look for capitalized multi-word names
    names = re.findall(r'[A-Z][a-z]+ [A-Z][a-z]+', content)
    if len(names) >= 15:
        score += 3
    elif len(names) >= 8:
        score += 2
    else:
        score += 1
        issues.append("Few proper names mentioned")

    # Publication/magazine names (max 3 points)
    publications = [
        # Major gaming sites
        'GameSpot', 'IGN', 'PC Gamer', 'Eurogamer', 'Polygon', 'Kotaku',
        'Rock Paper Shotgun', 'Giant Bomb', 'Destructoid', 'GamesRadar',
        # Adventure game specific
        'Adventure Gamers', 'Just Adventure', 'Adventure Classic Gaming',
        'The Adventurers Guild', 'Old Man Murray',
        # Classic/vintage publications
        'Computer Gaming World', 'Dragon', 'Electronic Games', 'PC Format',
        'Computer and Video Games', 'ACE', 'Amiga Power', 'Zzap!64',
        'Compute!', 'Antic', 'ST Format', 'Your Sinclair',
        # Databases/archives
        'MobyGames', 'GameFAQs', 'Metacritic', 'PCGamingWiki',
        # Modern retro coverage
        'Hardcore Gaming 101', 'The Digital Antiquarian', 'CRPG Addict',
        'The Adventure Gamer', 'Sierra Gamers', 'AGD Interactive',
        # General tech
        'Ars Technica', 'Wired', 'The Verge',
        # Print magazines
        'Edge', 'GamesTM', 'Retro Gamer', 'GamePro', 'Next Generation',
    ]
    pub_count = sum(1 for p in publications if p in content)
    if pub_count >= 4:
        score += 3
    elif pub_count >= 2:
        score += 2
    else:
        score += 1
        issues.append("Few publication names in reception")

    # Bullet points for gameplay details (max 3 points)
    bullets = content.count('•') + content.count('- ')
    if bullets >= 15:
        score += 3
    elif bullets >= 8:
        score += 2
    else:
        score += 1
        issues.append(f"Few bullet points: {bullets}")

    # Ratings mentioned (max 3 points)
    ratings = re.findall(r'\d+(?:\.\d+)?/[510]|\d+%', content)
    if len(ratings) >= 5:
        score += 3
    elif len(ratings) >= 3:
        score += 2
    else:
        score += 1
        issues.append("Few specific ratings mentioned")

    # Review table completeness - check for missing data (dashes)
    review_tables = re.findall(r'\|[^\n]*\|[^\n]*\|[^\n]*\|', content)
    dash_only_cells = sum(1 for t in review_tables if re.search(r'\|\s*[—–-]\s*\|', t))
    if dash_only_cells > 3:
        score -= 1
        issues.append(f"Review table has {dash_only_cells} empty cells (use actual data or remove rows)")

    # Quote presence (max 2 points)
    quotes = content.count('"')
    if quotes >= 6:
        score += 2
    elif quotes >= 2:
        score += 1
    else:
        issues.append("No direct quotes")

    # Multi-citation sentences (max 3 points)
    multi_cite = re.findall(r'\[\^ref-\d+\]\[\^ref-\d+\]', content)
    if len(multi_cite) >= 5:
        score += 3
    elif len(multi_cite) >= 2:
        score += 2
    else:
        score += 1
        issues.append("Few multi-source citations")

    return score, issues


def score_formatting(content: str, filepath: str = "") -> Tuple[int, List[str]]:
    """Score formatting and structure (max 25 points)."""
    score = 0
    issues = []

    # YAML frontmatter (max 5 points)
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        if yaml_end > 0:
            yaml = content[3:yaml_end]
            required_fields = ['title:', 'release_year:', 'developer:', 'publisher:', 'platforms:']
            found = sum(1 for f in required_fields if f in yaml)
            score += min(5, found)
            if found < 5:
                issues.append(f"YAML missing fields: {5-found} missing")

            # Check for wiki links in YAML (not allowed)
            if '[[' in yaml:
                score -= 3
                issues.append("Wiki links in YAML (not allowed) - use plain text")

            # Check filename-YAML year mismatch
            if filepath:
                filename = Path(filepath).stem
                year_in_filename = re.search(r'\b(19\d{2}|20[0-2]\d)\b', filename)
                year_in_yaml = re.search(r'release_year:\s*["\']?(\d{4})', yaml)
                if year_in_filename and year_in_yaml:
                    if year_in_filename.group(1) != year_in_yaml.group(1):
                        score -= 5
                        issues.append(f"Filename year ({year_in_filename.group(1)}) != YAML year ({year_in_yaml.group(1)})")

            # Check for placeholder overuse in YAML
            placeholders = yaml.lower().count('unknown') + yaml.lower().count('null') + yaml.count('N/A') + yaml.count('TBD')
            if placeholders >= 4:
                score -= 2
                issues.append(f"Too many YAML placeholders ({placeholders}): consider researching missing data")
        else:
            issues.append("Malformed YAML frontmatter")
    else:
        issues.append("Missing YAML frontmatter")

    # Game Info callout (max 3 points)
    if '> [!info]- Game Info' in content:
        score += 3
    else:
        issues.append("Missing Game Info callout")

    # H1 title (max 2 points)
    if re.search(r'^# [^\n]+$', content, re.MULTILINE):
        score += 2
    else:
        issues.append("Missing H1 title")

    # Last updated timestamp (max 2 points)
    if 'Last updated:' in content:
        score += 2
    else:
        issues.append("Missing last updated timestamp")

    # Purchase section has links (max 3 points)
    if '**Purchase / Digital Stores**' in content:
        purchase_section = content.split('**Purchase / Digital Stores**')[1].split('**')[0] if '**Purchase / Digital Stores**' in content else ''
        if 'GOG' in purchase_section or 'Steam' in purchase_section or 'Not currently available' in purchase_section:
            score += 3
        else:
            score += 1
            issues.append("Purchase section incomplete")
    else:
        issues.append("Missing Purchase section")

    # GOG link validation - check for common mistakes
    gog_links = re.findall(r'https?://(?:www\.)?gog\.com/[^\s\)]+', content)
    for link in gog_links:
        # Note: wishlist/dreamlist links are OK - they show the game exists on GOG
        # Check for mismatched game slugs (common copy-paste errors)
        # e.g., linking to kings_quest_4_5_6 when page is about KQ7
        if 'kings_quest' in link:
            # Extract the game numbers from the link
            link_nums = re.findall(r'kings_quest[_\-]?(\d+)', link)
            # Try to get the game number from YAML title
            title_match = re.search(r'title:.*?([IVXLC]+|\d+)', content[:500])
            if title_match and link_nums:
                # Simple check - if link mentions specific numbers, they should match
                roman_to_num = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5',
                               'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10'}
                title_num = title_match.group(1)
                if title_num in roman_to_num:
                    title_num = roman_to_num[title_num]
                # Check if title number appears in link numbers
                if title_num not in link_nums and title_num.isdigit():
                    score -= 5
                    issues.append(f"GOG link may be wrong game: {link} (expected game {title_num})")
                    break

    # Wiki links format (max 3 points)
    wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
    bad_links = [l for l in wiki_links if '.md' in l or '/' in l.split('|')[0]]
    if len(bad_links) == 0:
        score += 3
    elif len(bad_links) <= 2:
        score += 2
        issues.append(f"Some wiki links have paths/extensions: {bad_links[:2]}")
    else:
        issues.append(f"Multiple malformed wiki links")

    # Check for backslash-pipe issue in wiki links (Obsidian rendering problem)
    # Pattern: [[Page\|Display]] should be [[Page|Display]]
    # EXCEPTION: Inside markdown tables, backslash-pipe is valid/required
    backslash_pipes = re.findall(r'\[\[[^\]]*\\\|[^\]]*\]\]', content)
    if backslash_pipes:
        # Filter out those that appear inside table rows (lines starting with |)
        non_table_backslash_pipes = []
        for line in content.split('\n'):
            if not line.strip().startswith('|'):  # Not a table row
                line_matches = re.findall(r'\[\[[^\]]*\\\|[^\]]*\]\]', line)
                non_table_backslash_pipes.extend(line_matches)
        if non_table_backslash_pipes:
            score -= min(5, len(non_table_backslash_pipes))
            issues.append(f"Backslash-pipe in wiki links ({len(non_table_backslash_pipes)}x): use | not \\|")

    # Reference definitions at end (max 2 points)
    lines = content.strip().split('\n')
    last_lines = '\n'.join(lines[-20:])
    if '[^ref-' in last_lines and '## References' in content:
        score += 2
    else:
        issues.append("References section not at end")

    # No duplicate headers (max 2 points)
    headers = re.findall(r'^#{1,3} .+$', content, re.MULTILINE)
    if len(headers) == len(set(headers)):
        score += 2
    else:
        issues.append("Duplicate section headers found")

    # Collections section if applicable (max 3 points - bonus)
    if '### Collections' in content or 'This game has been included' in content:
        score += 3

    # Version History format check (for games with multiple versions)
    # Should be under Development with proper table format
    dev_start = content.find('## Development')
    dev_end = content.find('\n## ', dev_start + 10) if dev_start >= 0 else -1
    if dev_start >= 0:
        dev_section = content[dev_start:dev_end] if dev_end > dev_start else content[dev_start:]

        # Check if Version History subsection exists when versions are mentioned
        has_version_mentions = bool(re.search(r'version\s+\d+\.\d+|v\d+\.\d+', content, re.IGNORECASE))
        has_version_section = '### Version History' in dev_section

        if has_version_mentions and not has_version_section:
            score -= 3
            issues.append("Version mentions without ### Version History subsection")

        # Check for interpreter table in Sierra games (SCI/AGI engines)
        if 'SCI' in content or 'AGI' in content:
            has_interpreter_table = bool(re.search(r'\*\*(?:SCI|AGI) Interpreter Versions:\*\*', dev_section))
            has_version_table = bool(re.search(r'\| Version \| Date \||\| Game Version \|', dev_section))
            if has_version_section and not has_version_table:
                score -= 3
                issues.append("Version History section missing version table")

    return score, issues


def score_page(filepath: str) -> Dict:
    """Score a single page and return results."""
    with open(filepath) as f:
        content = f.read()

    # Detect game type for scoring adjustments
    game_type = detect_game_type(content, filepath)

    ref_score, ref_issues = score_references(content, game_type)
    section_score, section_issues = score_sections(content, game_type)
    depth_score, depth_issues = score_content_depth(content)
    format_score, format_issues = score_formatting(content, filepath)
    
    # Series continuity scoring (bonus/penalty for series games)
    series_score, series_issues = score_series_continuity(content, filepath)

    # Base total (capped at 100)
    base_total = ref_score + section_score + depth_score + format_score
    
    # Add series bonus (can push above 100 for exceptional series pages)
    # or apply penalty (negative series_score for missing continuity)
    total = base_total + series_score
    
    # Cap at 100 for percentage calculation, but show actual in breakdown
    capped_total = min(100, max(0, total))

    result = {
        'file': filepath,
        'total': capped_total,
        'max': 100,
        'percentage': round(capped_total / 100 * 100, 1),
        'breakdown': {
            'references': {'score': ref_score, 'max': 25, 'issues': ref_issues},
            'sections': {'score': section_score, 'max': 25, 'issues': section_issues},
            'content_depth': {'score': depth_score, 'max': 25, 'issues': depth_issues},
            'formatting': {'score': format_score, 'max': 25, 'issues': format_issues},
        }
    }
    
    # Add series continuity info if applicable
    if series_score != 0 or series_issues:
        result['breakdown']['series_continuity'] = {
            'score': series_score,
            'max': 8,
            'issues': series_issues
        }

    # Add game type info for transparency
    if game_type['game_type'] != 'standard':
        result['game_type'] = game_type['game_type']

    return result


def print_results(results: Dict, verbose: bool = False):
    """Print scoring results."""
    name = Path(results['file']).stem
    pct = results['percentage']

    # Status - aligned with project 90% threshold
    if pct >= 90:
        status = "PASS"
    elif pct >= 80:
        status = "REVIEW"
    else:
        status = "FAIL"

    # Add game type indicator if not standard
    type_indicator = ""
    if results.get('game_type'):
        type_map = {
            'cancelled': ' [CXL]',
            'unreleased': ' [TBD]',
            'non_narrative': ' [non-narr]',
        }
        type_indicator = type_map.get(results['game_type'], '')

    print(f"{status} {name}{type_indicator}: {results['total']}/{results['max']} ({pct}%)")

    if verbose or pct < 90:
        for category, data in results['breakdown'].items():
            print(f"  {category}: {data['score']}/{data['max']}")
            for issue in data['issues']:
                print(f"    - {issue}")


SCORE_HISTORY_FILE = Path(__file__).parent / "score_history.json"


def load_score_history() -> Dict:
    """Load score history from file."""
    if SCORE_HISTORY_FILE.exists():
        import json
        with open(SCORE_HISTORY_FILE) as f:
            return json.load(f)
    return {"scores": {}, "runs": []}


def save_score_history(history: Dict):
    """Save score history to file."""
    import json
    with open(SCORE_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def record_scores(results: List[Dict], history: Dict):
    """Record scores to history."""
    from datetime import datetime
    timestamp = datetime.now().isoformat()

    run_summary = {
        "timestamp": timestamp,
        "files_scored": len(results),
        "average": round(sum(r['percentage'] for r in results) / len(results), 1) if results else 0,
        "passing": sum(1 for r in results if r['percentage'] >= 90),
    }

    # Update per-file scores
    for result in results:
        filename = Path(result['file']).name
        if filename not in history["scores"]:
            history["scores"][filename] = []

        # Keep last 10 scores per file
        history["scores"][filename].append({
            "timestamp": timestamp,
            "score": result['percentage'],
            "total": result['total'],
        })
        history["scores"][filename] = history["scores"][filename][-10:]

    # Keep last 50 runs
    history["runs"].append(run_summary)
    history["runs"] = history["runs"][-50:]

    save_score_history(history)
    return run_summary


def main():
    parser = argparse.ArgumentParser(description="Score wiki page quality")
    parser.add_argument("files", nargs='+', help="Markdown files to score")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed breakdown")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--no-save", action="store_true", help="Don't save scores to history")

    args = parser.parse_args()

    all_results = []
    for filepath in args.files:
        if Path(filepath).exists():
            results = score_page(filepath)
            all_results.append(results)
            if not args.json:
                print_results(results, args.verbose)
        else:
            print(f"File not found: {filepath}", file=sys.stderr)

    if args.json:
        import json
        print(json.dumps(all_results, indent=2))
    elif len(all_results) > 1:
        avg = sum(r['percentage'] for r in all_results) / len(all_results)
        passing = sum(1 for r in all_results if r['percentage'] >= 90)
        print(f"\n=== SUMMARY ===")
        print(f"Average: {avg:.1f}%")
        print(f"Passing (90%+): {passing}/{len(all_results)}")

    # Save scores to history (unless --no-save)
    if all_results and not args.no_save:
        history = load_score_history()
        run_summary = record_scores(all_results, history)
        if not args.json:
            print(f"Scores saved to {SCORE_HISTORY_FILE.name}")


if __name__ == "__main__":
    main()
