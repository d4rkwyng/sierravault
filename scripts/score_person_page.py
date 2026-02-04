#!/usr/bin/env python3
"""
Score Designer/Developer pages for quality.

Adapted from score_page.py but with criteria appropriate for person pages.

Usage:
  python score_person_page.py /path/to/designer.md
  python score_person_page.py --all-designers
  python score_person_page.py --all-developers
"""

import re
import sys
import argparse
from pathlib import Path

VAULT_ROOT = Path(__file__).parent.parent


def extract_references(content: str) -> list:
    """Extract reference URLs from markdown."""
    refs = re.findall(r'\[\^ref-\d+\]:\s*(?:\[([^\]]+)\]\()?([^\s\)]+)', content)
    return refs


def count_inline_citations(content: str) -> int:
    """Count inline citation uses like [^ref-1]."""
    return len(re.findall(r'\[\^ref-\d+\](?!:)', content))


def check_yaml_fields(content: str, page_type: str) -> dict:
    """Check YAML frontmatter for required fields."""
    yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not yaml_match:
        return {"present": False, "missing": ["entire YAML block"]}

    yaml_content = yaml_match.group(1)

    if page_type == "designer":
        required = ["title", "type", "birth_year", "notable_games", "companies", "last_updated"]
    else:  # developer
        required = ["title", "type", "founded", "headquarters", "last_updated"]

    missing = []
    for field in required:
        if field + ":" not in yaml_content:
            missing.append(field)

    return {"present": True, "missing": missing}


def check_sections(content: str, page_type: str) -> dict:
    """Check for required sections."""
    if page_type == "designer":
        required_sections = [
            "## Overview",
            "## Career",
            "## Notable Works",
            "## Legacy",
            "## Games",
            "## References"
        ]
        optional_sections = [
            "## Design Philosophy",
            "### Early Career",
            "### Sierra Years",
            "### Later Career"
        ]
    else:  # developer
        required_sections = [
            "## Overview",
            "## History",
            "## Notable Games",
            "## Legacy",
            "## Games",
            "## References"
        ]
        optional_sections = [
            "## Technology",
            "### Founding",
            "### Sierra Era"
        ]

    missing = []
    present = []
    for section in required_sections:
        if section.lower() in content.lower():
            present.append(section)
        else:
            missing.append(section)

    optional_present = sum(1 for s in optional_sections if s.lower() in content.lower())

    return {
        "required_present": len(present),
        "required_total": len(required_sections),
        "missing": missing,
        "optional_bonus": optional_present
    }


def check_content_depth(content: str) -> dict:
    """Check content depth and quality."""
    # Word count (excluding YAML and references)
    main_content = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL)
    main_content = re.sub(r'\n## References\n.*$', '', main_content, flags=re.DOTALL)
    words = len(main_content.split())

    # Check for specific elements
    has_quotes = '>' in content or '"' in content
    has_dates = bool(re.search(r'\b(19|20)\d{2}\b', content))
    has_game_links = '[[Games/' in content or '[[' in content

    # Count notable works subsections
    notable_works_sections = len(re.findall(r'### .+ \(\d{4}\)', content))

    return {
        "word_count": words,
        "has_quotes": has_quotes,
        "has_dates": has_dates,
        "has_game_links": has_game_links,
        "notable_works_sections": notable_works_sections
    }


def score_page(filepath: Path, page_type: str = None) -> dict:
    """Score a person page and return detailed results."""
    content = filepath.read_text()

    # Auto-detect page type if not specified
    if page_type is None:
        if "type: designer" in content:
            page_type = "designer"
        elif "type: developer" in content:
            page_type = "developer"
        else:
            page_type = "designer"  # default

    results = {
        "file": filepath.name,
        "type": page_type,
        "scores": {},
        "issues": [],
        "suggestions": []
    }

    # 1. References (30 points)
    refs = extract_references(content)
    ref_count = len(refs)
    inline_citations = count_inline_citations(content)
    unique_domains = len(set(re.search(r'https?://([^/]+)', r[1]).group(1) if re.search(r'https?://([^/]+)', r[1]) else '' for r in refs if r[1]))

    ref_score = 0
    if ref_count >= 15:
        ref_score = 30
    elif ref_count >= 10:
        ref_score = 25
    elif ref_count >= 8:
        ref_score = 20
    elif ref_count >= 5:
        ref_score = 15
    else:
        ref_score = ref_count * 2

    # Bonus for citation diversity
    if unique_domains >= 8:
        ref_score = min(30, ref_score + 2)

    # Penalty for very low citations
    if ref_count < 8:
        results["issues"].append(f"LOW REFERENCES: Only {ref_count} (target: 15+)")

    if inline_citations < ref_count * 2:
        results["suggestions"].append("Add more inline citations throughout prose")

    results["scores"]["references"] = {
        "score": ref_score,
        "max": 30,
        "details": f"{ref_count} refs, {unique_domains} domains, {inline_citations} inline citations"
    }

    # 2. Sections (25 points)
    sections = check_sections(content, page_type)
    section_score = int((sections["required_present"] / sections["required_total"]) * 20)
    section_score += min(5, sections["optional_bonus"])

    if sections["missing"]:
        results["issues"].append(f"Missing sections: {', '.join(sections['missing'])}")

    results["scores"]["sections"] = {
        "score": section_score,
        "max": 25,
        "details": f"{sections['required_present']}/{sections['required_total']} required, {sections['optional_bonus']} optional"
    }

    # 3. Content Depth (25 points)
    depth = check_content_depth(content)
    depth_score = 0

    if depth["word_count"] >= 2000:
        depth_score += 15
    elif depth["word_count"] >= 1500:
        depth_score += 12
    elif depth["word_count"] >= 1000:
        depth_score += 8
    else:
        depth_score += max(0, depth["word_count"] // 200)

    if depth["has_quotes"]:
        depth_score += 2
    if depth["has_dates"]:
        depth_score += 2
    if depth["notable_works_sections"] >= 3:
        depth_score += 4
    elif depth["notable_works_sections"] >= 2:
        depth_score += 2
    if depth["has_game_links"]:
        depth_score += 2

    depth_score = min(25, depth_score)

    if depth["word_count"] < 1500:
        results["issues"].append(f"Short content: {depth['word_count']} words (target: 1500+)")
    if depth["notable_works_sections"] < 3:
        results["suggestions"].append("Add more detailed Notable Works subsections with years")

    results["scores"]["content_depth"] = {
        "score": depth_score,
        "max": 25,
        "details": f"{depth['word_count']} words, {depth['notable_works_sections']} notable works"
    }

    # 4. Formatting (20 points)
    yaml = check_yaml_fields(content, page_type)
    format_score = 0

    if yaml["present"]:
        format_score += 10
        format_score -= len(yaml["missing"]) * 2

    if "last_updated:" in content:
        format_score += 3
    else:
        results["issues"].append("Missing last_updated in YAML")

    if "## Games" in content and "[[" in content:
        format_score += 4

    if re.search(r'\| .+ \| .+ \|', content):  # Has tables
        format_score += 3

    format_score = max(0, min(20, format_score))

    if yaml["missing"]:
        results["issues"].append(f"YAML missing: {', '.join(yaml['missing'])}")

    results["scores"]["formatting"] = {
        "score": format_score,
        "max": 20,
        "details": f"YAML: {len(yaml['missing'])} missing fields"
    }

    # Calculate total
    total = sum(s["score"] for s in results["scores"].values())
    max_total = sum(s["max"] for s in results["scores"].values())

    results["total"] = total
    results["max_total"] = max_total
    results["percentage"] = round(total / max_total * 100, 1)
    results["passed"] = results["percentage"] >= 80

    return results


def print_results(results: dict):
    """Print scoring results."""
    status = "PASS" if results["passed"] else "FAIL" if results["percentage"] < 70 else "REVIEW"
    print(f"\n{status} {results['file']}: {results['total']}/{results['max_total']} ({results['percentage']}%)")

    for category, data in results["scores"].items():
        print(f"  {category}: {data['score']}/{data['max']} - {data['details']}")

    if results["issues"]:
        print("  ISSUES:")
        for issue in results["issues"]:
            print(f"    - {issue}")

    if results["suggestions"]:
        print("  SUGGESTIONS:")
        for suggestion in results["suggestions"]:
            print(f"    - {suggestion}")


def main():
    parser = argparse.ArgumentParser(description="Score designer/developer pages")
    parser.add_argument("file", nargs="?", help="Path to markdown file")
    parser.add_argument("--all-designers", action="store_true", help="Score all designer pages")
    parser.add_argument("--all-developers", action="store_true", help="Score all developer pages")
    parser.add_argument("--summary", action="store_true", help="Show summary only")

    args = parser.parse_args()

    files_to_score = []

    if args.all_designers:
        designers_dir = VAULT_ROOT / "Designers"
        files_to_score = [(f, "designer") for f in designers_dir.glob("*.md")]
    elif args.all_developers:
        developers_dir = VAULT_ROOT / "Developers"
        files_to_score = [(f, "developer") for f in developers_dir.glob("*.md")]
    elif args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"File not found: {filepath}")
            sys.exit(1)
        files_to_score = [(filepath, None)]
    else:
        parser.print_help()
        sys.exit(0)

    all_results = []
    for filepath, page_type in files_to_score:
        results = score_page(filepath, page_type)
        all_results.append(results)
        if not args.summary:
            print_results(results)

    if len(all_results) > 1:
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        passed = sum(1 for r in all_results if r["passed"])
        avg_score = sum(r["percentage"] for r in all_results) / len(all_results)
        print(f"Total: {len(all_results)} pages")
        print(f"Passed (80%+): {passed}/{len(all_results)} ({100*passed//len(all_results)}%)")
        print(f"Average score: {avg_score:.1f}%")

        # List failures
        failures = [r for r in all_results if not r["passed"]]
        if failures:
            print(f"\nFailing pages ({len(failures)}):")
            for r in sorted(failures, key=lambda x: x["percentage"]):
                print(f"  {r['file']}: {r['percentage']}%")


if __name__ == "__main__":
    main()
