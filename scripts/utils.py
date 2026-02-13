#!/usr/bin/env python3
"""
Shared utilities for SierraVault scripts.

This module consolidates common functions used across multiple scripts
to reduce code duplication and ensure consistent behavior.

Usage:
    from utils import slugify, normalize_url, get_domain, load_env
    from utils import VAULT_DIR, RESEARCH_DIR, SCRIPTS_DIR
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse

# ============================================================================
# Standard Paths
# ============================================================================

SCRIPTS_DIR = Path(__file__).parent
VAULT_DIR = SCRIPTS_DIR.parent / "vault"
INTERNAL_DIR = SCRIPTS_DIR.parent.parent / "../Library/CloudStorage/ProtonDrive-woodd@mindtricks.io-folder/Assets/sierravault"
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_RESEARCH_DIR = RESEARCH_DIR / "games"
GAMES_DIR = VAULT_DIR / "Games"


# ============================================================================
# String Utilities
# ============================================================================

def slugify(title: str) -> str:
    """
    Convert game title to folder slug.
    
    Examples:
        "King's Quest VII" -> "kings-quest-vii"
        "Space Quest III: The Pirates of Pestulon" -> "space-quest-iii-the-pirates-of-pestulon"
    """
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


# ============================================================================
# URL Utilities
# ============================================================================

def normalize_url(url: str) -> str:
    """
    Normalize URL for duplicate detection.
    
    Handles:
    - http/https variations
    - www/non-www variations
    - Trailing slashes
    - URL fragments
    - Common tracking parameters
    """
    url = url.strip().lower()
    
    # Remove protocol
    url = re.sub(r'^https?://', '', url)
    
    # Remove www prefix
    url = re.sub(r'^www\.', '', url)
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    # Remove URL fragments
    url = url.split('#')[0]
    
    # Remove tracking parameters
    if '?' in url:
        base, params = url.split('?', 1)
        tracking_prefixes = ('utm_', 'ref', 'source', 'campaign', 'fbclid', 'gclid')
        filtered_params = []
        for p in params.split('&'):
            param_name = p.split('=')[0].lower()
            if not any(param_name.startswith(prefix) for prefix in tracking_prefixes):
                filtered_params.append(p)
        if filtered_params:
            url = base + '?' + '&'.join(filtered_params)
        else:
            url = base
    
    return url


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return ""


# ============================================================================
# Environment Utilities
# ============================================================================

def load_env(env_path: Path = None):
    """
    Load environment variables from .env file.
    
    Args:
        env_path: Path to .env file. Defaults to scripts/.env
    """
    if env_path is None:
        env_path = SCRIPTS_DIR / ".env"
    
    if not env_path.exists():
        return
    
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.replace('export ', '').strip()
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value


def get_api_key(key_name: str, load_from_env: bool = True) -> str:
    """
    Get API key from environment.
    
    Args:
        key_name: Name of the environment variable (e.g., 'ANTHROPIC_API_KEY')
        load_from_env: Whether to load from .env file first
    
    Returns:
        API key string or empty string if not found
    """
    if load_from_env:
        load_env()
    return os.environ.get(key_name, '')


# ============================================================================
# File Utilities
# ============================================================================

def extract_yaml_frontmatter(filepath: Path) -> dict:
    """
    Extract YAML frontmatter from markdown file.
    
    Returns empty dict if no frontmatter found.
    """
    try:
        import yaml
        content = filepath.read_text(encoding='utf-8')
        
        if content.startswith('---'):
            end = content.find('---', 3)
            if end != -1:
                yaml_str = content[3:end].strip()
                return yaml.safe_load(yaml_str) or {}
    except Exception:
        pass
    
    return {}


def get_game_title_from_path(filepath: Path) -> str:
    """
    Extract game title from file path.
    
    Handles patterns like:
    - "1990 - King's Quest V.md" -> "King's Quest V"
    - "King's Quest V.md" -> "King's Quest V"
    """
    name = filepath.stem
    # Remove year prefix like "1990 - "
    name = re.sub(r'^\d{4}\s*[-–—]\s*', '', name)
    return name


# ============================================================================
# Company Name Normalization
# ============================================================================

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


def normalize_company_name(name: str) -> str:
    """Normalize company name to canonical form for comparison."""
    name_lower = name.lower().strip()
    for canonical, aliases in COMPANY_ALIASES.items():
        for alias in aliases:
            if alias.lower() == name_lower:
                return canonical
    return name_lower


# ============================================================================
# Game Type Detection
# ============================================================================

NON_NARRATIVE_GENRES = [
    'casino', 'card', 'poker', 'blackjack', 'solitaire', 'board game', 'mahjong',
    'chess', 'crossword', 'word game', 'puzzle game', 'trivia',
    'sports', 'racing', 'golf', 'football', 'baseball', 'basketball', 'soccer',
    'fishing', 'hunting', 'flight simulation', 'flight sim', 'driving',
    'pinball', 'pool', 'billiards',
    'city building', 'city-building', 'city builder', 'construction simulation',
    'tycoon', 'management simulation', 'business simulation', 'god game',
    'real-time strategy', 'rts', 'turn-based strategy', '4x',
    'screensaver', 'utility', 'educational', 'typing', 'math',
    'shooter', 'fixed shooter', 'arcade', 'action arcade',
]

NON_NARRATIVE_SERIES = [
    'hoyle', '3d ultra', '3-d ultra', 'front page sports', 'sierra pro pilot',
    "driver's education", 'pga championship', 'nascar', 'trophy bass',
    "you don't know jack", 'after dark', 'incredible machine',
    "crazy nick", 'jumpstart', 'dr. brain', 'power chess',
    'caesar', 'pharaoh', 'zeus', 'emperor', 'cleopatra', 'poseidon',
    'lords of the realm', 'lords of magic', 'robert e. lee',
    'outpost', 'earthsiege', 'starsiege', 'cyberstorm',
]


def detect_game_type(content: str, filepath: str = "") -> dict:
    """
    Detect game type for scoring adjustments.
    
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


if __name__ == "__main__":
    # Quick tests
    print("Testing utils.py...")
    
    assert slugify("King's Quest VII") == "kings-quest-vii"
    assert slugify("Space Quest III: The Pirates") == "space-quest-iii-the-pirates"
    print("  slugify: OK")
    
    assert normalize_url("https://www.example.com/page/") == "example.com/page"
    assert normalize_url("http://example.com/page?utm_source=test") == "example.com/page"
    print("  normalize_url: OK")
    
    assert get_domain("https://www.gog.com/game/kings_quest") == "www.gog.com"
    print("  get_domain: OK")
    
    print("\nAll tests passed!")
