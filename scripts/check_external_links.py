#!/usr/bin/env python3
"""
Check GOG/Steam links for broken URLs using Brave Search API.
Usage:
    python3 check_external_links.py [--days 7]
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from collections import defaultdict

try:
    import httpx
except ImportError:
    print("Installing httpx...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "httpx"])
    import httpx


def get_recent_files(days=7):
    """Get markdown files modified in the last N days."""
    cmd = f"find vault/Games -name '*.md' -mtime -{days}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/Users/woodd/Projects/sierravault')
    return result.stdout.strip().split('\n') if result.stdout.strip() else []


def extract_external_links(content):
    """Extract GOG and Steam links from markdown content."""
    gog_pattern = r'https?://www\.gog\.com/game/[^"\')\s]+'
    steam_pattern = r'https?://store\.steampowered\.com/app/\d+/[^"\')\s]*'
    
    gog_links = re.findall(gog_pattern, content)
    steam_links = re.findall(steam_pattern, content)
    
    return gog_links, steam_links


def check_link_brave_search(url):
    """Check if a URL is accessible using Brave Search API."""
    import urllib.parse
    
    # Get API key from environment
    brave_key = os.environ.get('BRAVE_API_KEY')
    if not brave_key:
        print(f"⚠️  BRAVE_API_KEY not set, skipping URL check for: {url}")
        return None, "API_KEY_MISSING"
    
    # Search for the exact URL
    query = f'"{url}"'
    endpoint = "https://api.search.brave.com/res/v1/web/search"
    
    headers = {
        "X-Subscription-Token": brave_key,
        "Accept": "application/json"
    }
    
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(endpoint, params={"q": query}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                results = data.get('web', {}).get('results', [])
                
                # Check if exact URL appears in results
                for result in results:
                    result_url = result.get('url', '')
                    if result_url == url or result_url.startswith(url + '/'):
                        return True, "FOUND"
                
                return False, "NOT_FOUND"
            else:
                return None, f"API_ERROR_{response.status_code}"
    except Exception as e:
        return None, f"ERROR_{str(e)}"


def find_better_gog_link(broken_url):
    """Try to find a working GOG link for the same game."""
    import urllib.parse
    
    brave_key = os.environ.get('BRAVE_API_KEY')
    if not brave_key:
        return None
    
    # Extract game name from broken URL
    # Example: https://www.gog.com/game/the_witcher -> "the_witcher"
    path = urllib.parse.urlparse(broken_url).path
    game_slug = path.split('/')[-1] if path else None
    
    if not game_slug:
        return None
    
    # Search for the game on GOG
    query = f"site:gog.com/game/ {game_slug.replace('_', ' ')}"
    endpoint = "https://api.search.brave.com/res/v1/web/search"
    
    headers = {
        "X-Subscription-Token": brave_key,
        "Accept": "application/json"
    }
    
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(endpoint, params={"q": query}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                results = data.get('web', {}).get('results', [])
                
                # Find the best matching GOG link
                for result in results[:5]:  # Check top 5 results
                    result_url = result.get('url', '')
                    if result_url.startswith('https://www.gog.com/game/'):
                        # Make sure it's not the broken URL
                        if result_url != broken_url:
                            return result_url
    except Exception as e:
        pass
    
    return None


def find_better_steam_link(broken_url):
    """Try to find a working Steam link for the same game."""
    import urllib.parse
    
    brave_key = os.environ.get('BRAVE_API_KEY')
    if not brave_key:
        return None
    
    # Extract game name from broken URL
    path = urllib.parse.urlparse(broken_url).path
    app_id = None
    game_name = None
    
    # Try to extract app ID
    match = re.search(r'app/(\d+)', broken_url)
    if match:
        app_id = match.group(1)
    
    if not app_id:
        # Extract game name from path
        game_name = path.split('/')[-1]
    
    # Search for the game on Steam
    if game_name:
        query = f"site:store.steampowered.com/app {game_name.replace('_', ' ')}"
    elif app_id:
        query = f"site:store.steampowered.com/app {app_id}"
    else:
        return None
    
    endpoint = "https://api.search.brave.com/res/v1/web/search"
    
    headers = {
        "X-Subscription-Token": brave_key,
        "Accept": "application/json"
    }
    
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(endpoint, params={"q": query}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                results = data.get('web', {}).get('results', [])
                
                # Find the best matching Steam link
                for result in results[:5]:  # Check top 5 results
                    result_url = result.get('url', '')
                    if result_url.startswith('https://store.steampowered.com/app/'):
                        # Make sure it's not the broken URL
                        if result_url != broken_url:
                            return result_url
    except Exception as e:
        pass
    
    return None


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    
    print("=" * 80)
    print("EXTERNAL LINK HEALTH CHECK")
    print(f"Checking files modified in last {days} days")
    print("=" * 80)
    print()
    
    # Check for API key
    if not os.environ.get('BRAVE_API_KEY'):
        print("❌ ERROR: BRAVE_API_KEY environment variable not set!")
        print("   Set it in your shell: export BRAVE_API_KEY='your-key-here'")
        print("   Or add it to ~/.zshenv")
        return
    
    recent_files = get_recent_files(days)
    
    if not recent_files or len([f for f in recent_files if f]) == 0:
        print("No files modified in the last 7 days.")
        return
    
    print(f"Found {len([f for f in recent_files if f])} recent files\n")
    
    broken_gog = defaultdict(list)
    broken_steam = defaultdict(list)
    fixed_gog = defaultdict(list)
    fixed_steam = defaultdict(list)
    total_gog = 0
    total_steam = 0
    
    for filepath in recent_files:
        if not filepath:
            continue
            
        rel_path = filepath.replace('/Users/woodd/Projects/sierravault/', '')
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {rel_path}: {e}")
            continue
        
        gog_links, steam_links = extract_external_links(content)
        total_gog += len(gog_links)
        total_steam += len(steam_links)
        
        # Check GOG links
        for link in gog_links:
            status, result = check_link_brave_search(link)
            if status == False:
                broken_gog[rel_path].append(link)
                print(f"❌ GOG BROKEN: {rel_path}")
                print(f"   {link}")
                
                # Try to find a working link
                new_link = find_better_gog_link(link)
                if new_link:
                    fixed_gog[rel_path].append((link, new_link))
                    print(f"   ✅ Found replacement: {new_link}")
            elif status == None:
                print(f"⚠️  GOG SKIPPED: {rel_path}")
                print(f"   {link}")
        
        # Check Steam links
        for link in steam_links:
            status, result = check_link_brave_search(link)
            if status == False:
                broken_steam[rel_path].append(link)
                print(f"❌ Steam BROKEN: {rel_path}")
                print(f"   {link}")
                
                # Try to find a working link
                new_link = find_better_steam_link(link)
                if new_link:
                    fixed_steam[rel_path].append((link, new_link))
                    print(f"   ✅ Found replacement: {new_link}")
            elif status == None:
                print(f"⚠️  Steam SKIPPED: {rel_path}")
                print(f"   {link}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal GOG links checked: {total_gog}")
    print(f"Total Steam links checked: {total_steam}")
    
    if broken_gog:
        print(f"\n❌ Broken GOG links: {sum(len(v) for v in broken_gog.values())}")
        for filepath, links in sorted(broken_gog.items()):
            print(f"\n{filepath}:")
            for link in links:
                print(f"  ❌ {link}")
        
        if fixed_gog:
            print(f"\n✅ Auto-fixed GOG links: {sum(len(v) for v in fixed_gog.values())}")
            for filepath, fixes in sorted(fixed_gog.items()):
                print(f"\n{filepath}:")
                for old, new in fixes:
                    print(f"  {old} → {new}")
    
    if broken_steam:
        print(f"\n❌ Broken Steam links: {sum(len(v) for v in broken_steam.values())}")
        for filepath, links in sorted(broken_steam.items()):
            print(f"\n{filepath}:")
            for link in links:
                print(f"  ❌ {link}")
        
        if fixed_steam:
            print(f"\n✅ Auto-fixed Steam links: {sum(len(v) for v in fixed_steam.values())}")
            for filepath, fixes in sorted(fixed_steam.items()):
                print(f"\n{filepath}:")
                for old, new in fixes:
                    print(f"  {old} → {new}")
    
    total_broken = sum(len(v) for v in broken_gog.values()) + sum(len(v) for v in broken_steam.values())
    total_fixed = sum(len(v) for v in fixed_gog.values()) + sum(len(v) for v in fixed_steam.values())
    
    if total_broken == 0:
        print("\n✅ All external links are working!")
    else:
        print(f"\n⚠️  {total_broken} broken links found, {total_fixed} auto-fixed")
        if total_fixed > 0 and total_fixed < total_broken:
            print("📝 Manual fixes needed: Some links couldn't be auto-fixed")
    
    print("\n" + "=" * 80)
    
    # Save report for PR generation
    report = {
        'broken_gog': dict(broken_gog),
        'broken_steam': dict(broken_steam),
        'fixed_gog': dict(fixed_gog),
        'fixed_steam': dict(fixed_steam),
        'total_checked': total_gog + total_steam,
        'total_broken': total_broken,
        'total_fixed': total_fixed
    }
    
    import json
    with open('/Users/woodd/Projects/sierravault/link_health_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n📄 Report saved to: link_health_report.json")

if __name__ == '__main__':
    main()