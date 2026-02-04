#!/usr/bin/env python3
"""
Designer Page Hallucination Audit
Audits all designer pages for potential hallucinations and verification gaps.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

VAULT_ROOT = Path(__file__).parent.parent / "vault"
DESIGNERS_DIR = VAULT_ROOT / "Designers"
INTERNAL_ROOT = Path(os.environ.get("SIERRAVAULT_INTERNAL", Path(__file__).parent.parent.parent / "sierravault-internal"))
RESEARCH_DIR = INTERNAL_ROOT / "research" / "designers"
GAMES_DIR = VAULT_ROOT / "Games"

def slugify(name):
    """Convert name to research folder slug."""
    return name.lower().replace(" ", "-").replace("'", "").replace(".", "")

def get_all_game_files():
    """Get all game file paths and names."""
    games = {}
    for game_file in GAMES_DIR.rglob("*.md"):
        # Extract game name from filename
        name = game_file.stem
        # Also extract from file for wikilinks
        games[str(game_file.relative_to(VAULT_ROOT))] = name
        games[name] = str(game_file.relative_to(VAULT_ROOT))
    return games

def extract_frontmatter(content):
    """Extract frontmatter from markdown file."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        return frontmatter
    return {}

def count_citations(content):
    """Count number of citations in content."""
    # Count [^ref-X] style references
    refs = re.findall(r'\[\^ref-\d+\]', content)
    return len(set(refs))

def extract_game_credits(content):
    """Extract game credits from the Games table."""
    games = []
    # Find the Games section and table
    table_pattern = r'\| Year \| Game \| Role \|.*?(?=\n## |\n\Z)'
    match = re.search(table_pattern, content, re.DOTALL)
    if match:
        table = match.group(0)
        # Extract wikilinks from table
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', table)
        for link in links:
            games.append(link)
    return games

def verify_game_exists(game_path, all_games):
    """Check if a game page exists."""
    # Clean up the path
    clean_path = game_path.replace("\\", "/")
    if clean_path in all_games:
        return True
    # Try matching without .md
    if not clean_path.endswith(".md"):
        if clean_path + ".md" in all_games:
            return True
    # Try partial match
    for existing in all_games:
        if clean_path in existing or existing in clean_path:
            return True
    return False

def extract_biographical_claims(content):
    """Extract key biographical claims for verification."""
    claims = []
    
    # Birth year
    birth_match = re.search(r'born (?:in )?(\d{4})', content, re.IGNORECASE)
    if birth_match:
        claims.append(f"Birth year: {birth_match.group(1)}")
    
    # Death year
    death_match = re.search(r'died (?:in )?(\d{4})', content, re.IGNORECASE)
    if death_match:
        claims.append(f"Death year: {death_match.group(1)}")
    
    # Companies
    company_pattern = r'(?:worked (?:at|for)|joined|employed by|hired by) ([A-Z][A-Za-z\- ]+(?:On-Line|Entertainment|Productions|Interactive|Games|Studios|Software|Inc\.))'
    companies = re.findall(company_pattern, content)
    if companies:
        claims.append(f"Companies: {', '.join(set(companies))}")
    
    return claims

def check_uncited_claims(content):
    """Find paragraphs that may have uncited claims."""
    uncited = []
    # Split into paragraphs
    paragraphs = re.split(r'\n\n+', content)
    for para in paragraphs:
        # Skip headings, tables, frontmatter
        if para.startswith('#') or para.startswith('|') or para.startswith('---'):
            continue
        # Skip very short paragraphs
        if len(para) < 100:
            continue
        # Check if paragraph has any citations
        if not re.search(r'\[\^ref-\d+\]', para):
            # Extract first 50 chars for context
            preview = para[:100].replace('\n', ' ').strip()
            if preview and not preview.startswith('[^ref'):
                uncited.append(preview + "...")
    return uncited[:3]  # Return max 3 examples

def count_sierra_games(game_credits, all_games):
    """Count games that are verified Sierra games."""
    sierra_count = 0
    for game_path in game_credits:
        # Check if the game exists and is in a Sierra-related folder
        if verify_game_exists(game_path, all_games):
            # Check if it's a core Sierra game (not spiritual successor, etc)
            if 'Spiritual Successors' not in game_path:
                sierra_count += 1
    return sierra_count

def get_research_file_count(slug):
    """Count research files for a designer."""
    research_path = RESEARCH_DIR / slug
    if research_path.exists():
        files = list(research_path.glob("*.json")) + list(research_path.glob("*.html")) + list(research_path.glob("*.md"))
        return len(files)
    return 0

def audit_designer(designer_file):
    """Audit a single designer page."""
    name = designer_file.stem
    slug = slugify(name)
    
    content = designer_file.read_text(encoding='utf-8')
    frontmatter = extract_frontmatter(content)
    
    result = {
        "name": name,
        "slug": slug,
        "research_folder": False,
        "research_files": 0,
        "citation_count": 0,
        "game_credits": [],
        "verified_games": 0,
        "missing_games": [],
        "sierra_games": 0,
        "biographical_claims": [],
        "uncited_claims": [],
        "issues": [],
        "risk_level": "LOW"
    }
    
    # Check research folder
    research_path = RESEARCH_DIR / slug
    if research_path.exists() and research_path.is_dir():
        result["research_folder"] = True
        result["research_files"] = get_research_file_count(slug)
    
    # Count citations
    result["citation_count"] = count_citations(content)
    
    # Extract and verify game credits
    all_games = get_all_game_files()
    game_credits = extract_game_credits(content)
    result["game_credits"] = game_credits
    
    verified = 0
    missing = []
    for game in game_credits:
        if verify_game_exists(game, all_games):
            verified += 1
        else:
            missing.append(game)
    
    result["verified_games"] = verified
    result["missing_games"] = missing
    result["sierra_games"] = count_sierra_games(game_credits, all_games)
    
    # Extract biographical claims
    result["biographical_claims"] = extract_biographical_claims(content)
    
    # Check for uncited claims
    result["uncited_claims"] = check_uncited_claims(content)
    
    # Determine issues and risk level
    issues = []
    risk_points = 0
    
    if not result["research_folder"]:
        issues.append("No research folder")
        risk_points += 2
    elif result["research_files"] < 5:
        issues.append(f"Limited research ({result['research_files']} files)")
        risk_points += 1
    
    if result["citation_count"] < 5:
        issues.append(f"Very few citations ({result['citation_count']})")
        risk_points += 2
    elif result["citation_count"] < 10:
        issues.append(f"Low citations ({result['citation_count']})")
        risk_points += 1
    
    if result["missing_games"]:
        issues.append(f"Missing game pages: {', '.join(result['missing_games'][:3])}")
        risk_points += 1
    
    if result["sierra_games"] < 2:
        issues.append(f"Fewer than 2 verified Sierra games ({result['sierra_games']})")
        risk_points += 2
    
    if result["uncited_claims"]:
        issues.append(f"Uncited claims found")
        risk_points += 1
    
    result["issues"] = issues
    
    # Determine risk level
    if risk_points >= 4:
        result["risk_level"] = "HIGH"
    elif risk_points >= 2:
        result["risk_level"] = "MEDIUM"
    else:
        result["risk_level"] = "LOW"
    
    return result

def main():
    """Run full audit."""
    results = []
    
    for designer_file in sorted(DESIGNERS_DIR.glob("*.md")):
        result = audit_designer(designer_file)
        results.append(result)
        print(f"Audited: {result['name']} - {result['risk_level']}")
    
    # Generate report
    report = generate_report(results)
    
    # Save report
    output_dir = INTERNAL_ROOT / "audit"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = output_dir / "designer-audit.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"\nReport saved to: {report_path}")
    
    # Also save raw JSON for reference
    json_path = output_dir / "designer-audit.json"
    json_path.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f"JSON data saved to: {json_path}")

def generate_report(results):
    """Generate markdown report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Count statistics
    total = len(results)
    high_risk = sum(1 for r in results if r['risk_level'] == 'HIGH')
    medium_risk = sum(1 for r in results if r['risk_level'] == 'MEDIUM')
    low_risk = sum(1 for r in results if r['risk_level'] == 'LOW')
    with_research = sum(1 for r in results if r['research_folder'])
    low_sierra = sum(1 for r in results if r['sierra_games'] < 2)
    
    report = f"""# Designer Pages Hallucination Audit

**Generated:** {now}
**Total Pages Audited:** {total}

## Summary

| Metric | Count |
|--------|-------|
| HIGH Risk | {high_risk} |
| MEDIUM Risk | {medium_risk} |
| LOW Risk | {low_risk} |
| With Research Folder | {with_research}/{total} |
| Missing Research Folder | {total - with_research} |
| Fewer than 2 Sierra Games | {low_sierra} |

## Risk Definitions

- **HIGH**: Multiple verification concerns (missing research, very few citations, unverified claims)
- **MEDIUM**: Some verification gaps (limited research or citations)
- **LOW**: Well-documented with research and citations

---

## HIGH Risk Pages

These pages require immediate attention and verification:

"""
    
    for r in sorted(results, key=lambda x: (-['LOW', 'MEDIUM', 'HIGH'].index(x['risk_level']), x['name'])):
        if r['risk_level'] == 'HIGH':
            report += f"""### {r['name']}

| Attribute | Value |
|-----------|-------|
| Research Folder | {'✅ YES' if r['research_folder'] else '❌ NO'} |
| Research Files | {r['research_files']} |
| Citations | {r['citation_count']} |
| Game Credits | {len(r['game_credits'])} |
| Verified Games | {r['verified_games']} |
| Sierra Games | {r['sierra_games']} |

**Issues:**
"""
            for issue in r['issues']:
                report += f"- {issue}\n"
            
            if r['uncited_claims']:
                report += "\n**Sample Uncited Claims:**\n"
                for claim in r['uncited_claims'][:2]:
                    report += f"> {claim}\n"
            
            report += "\n---\n\n"
    
    report += """## MEDIUM Risk Pages

These pages have some verification gaps:

"""
    
    for r in results:
        if r['risk_level'] == 'MEDIUM':
            issues_str = "; ".join(r['issues']) if r['issues'] else "None"
            report += f"""### {r['name']}

- Research Folder: {'✅' if r['research_folder'] else '❌'} ({r['research_files']} files)
- Citations: {r['citation_count']}
- Sierra Games: {r['sierra_games']}
- Issues: {issues_str}

"""
    
    report += """---

## LOW Risk Pages

These pages are well-documented:

| Page | Research | Citations | Sierra Games |
|------|----------|-----------|--------------|
"""
    
    for r in results:
        if r['risk_level'] == 'LOW':
            research = '✅' if r['research_folder'] else '❌'
            report += f"| {r['name']} | {research} ({r['research_files']}) | {r['citation_count']} | {r['sierra_games']} |\n"
    
    report += """

---

## Pages with Fewer than 2 Verified Sierra Games

These designers may not warrant full pages or need additional verification:

| Page | Sierra Games | Total Credits | Risk |
|------|-------------|---------------|------|
"""
    
    for r in results:
        if r['sierra_games'] < 2:
            report += f"| {r['name']} | {r['sierra_games']} | {len(r['game_credits'])} | {r['risk_level']} |\n"
    
    report += """

---

## Full Audit Details

"""
    
    for r in sorted(results, key=lambda x: x['name']):
        issues_str = "; ".join(r['issues']) if r['issues'] else "None"
        report += f"| {r['name']} | {'YES' if r['research_folder'] else 'NO'} | {r['citation_count']} | {r['sierra_games']} | {r['risk_level']} | {issues_str} |\n"
    
    return report

if __name__ == "__main__":
    main()
