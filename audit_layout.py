#!/usr/bin/env python3
"""
nexus-tech/audit_layout.py
Parses and audits layout structure, CSS category tag badges, Google ad slots, and padding guidelines.
Can auto-patch visual layout issues.
"""

import os
import sys
import re
from bs4 import BeautifulSoup

VALID_BADGES = {"tag-blue", "tag-red", "tag-yellow", "tag-green"}
CATEGORY_COLOR_MAP = {
    "computing": "tag-blue",
    "hardware": "tag-red",
    "fintech": "tag-yellow",
    "gaming": "tag-green",
    "audio": "tag-blue",
    "display": "tag-red",
    "graphics": "tag-green"
}

CORRECT_LEADERBOARD_AD = """<!-- Header Leaderboard Ad -->
        <ins class="adsbygoogle ad-slot ad-leaderboard"
             style="display: flex !important; text-decoration: none;"
             data-ad-client="ca-pub-7561845942385102"
             data-ad-slot="7289012345">
            <div style="font-size: 1.1rem; font-weight: 700; color: var(--google-blue);">728 x 90 Leaderboard Placeholder</div>
            <div style="font-size: 0.8rem; color: var(--text-muted);">Programmatic News Aggregator Ad Placement (adsbygoogle)</div>
        </ins>"""


def audit_and_patch_file(file_path, auto_patch=True):
    issues = []
    patched = False

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")

    # 1. Verify Category Tag Badges
    badges = soup.find_all(class_=lambda x: x and "category-tag" in x)
    for badge in badges:
        classes = badge.get("class", [])
        badge_color_class = [c for c in classes if c.startswith("tag-")]
        
        if not badge_color_class:
            issues.append(f"Badge with text '{badge.get_text()}' is missing a color class.")
            continue
            
        color_class = badge_color_class[0]
        if color_class not in VALID_BADGES:
            issues.append(f"Badge has invalid color class: '{color_class}'.")
            
        # Semantic check (e.g. Gaming should be green, Computing blue, etc.)
        badge_text_lower = badge.get_text().strip().lower()
        expected_class = CATEGORY_COLOR_MAP.get(badge_text_lower)
        if expected_class and color_class != expected_class:
            issues.append(
                f"Badge '{badge.get_text()}' uses class '{color_class}' but expected '{expected_class}'."
            )

    # 2. Verify Ad Slots
    # Any element with class ad-slot must be an ins tag and have class adsbygoogle and data-ad-client
    ad_slots = soup.find_all(class_=lambda x: x and "ad-slot" in x)
    for ad in ad_slots:
        classes = ad.get("class", [])
        if ad.name != "ins":
            issues.append(f"Ad slot uses tag <{ad.name}> instead of <ins>.")
        if "adsbygoogle" not in classes:
            issues.append("Ad slot is missing the 'adsbygoogle' class.")
        if ad.get("data-ad-client") != "ca-pub-7561845942385102":
            issues.append(
                f"Ad slot has invalid or missing data-ad-client: '{ad.get('data-ad-client')}'."
            )

    # 3. Verify Padding Guidelines
    # Check comparison blocks: if they have inline padding, it should be 2rem
    comparison_blocks = soup.find_all(class_=lambda x: x and "comparison-block" in x)
    for block in comparison_blocks:
        style = block.get("style", "")
        if "padding" in style:
            # extract padding value
            match = re.search(r"padding:\s*([^;]+)", style)
            if match:
                padding_val = match.group(1).strip()
                if padding_val not in ["2rem", "2rem;"]:
                    issues.append(
                        f"Comparison block has inline padding '{padding_val}' which conflicts with the 2rem layout guideline."
                    )

    # 4. Auto-Patching
    if issues and auto_patch:
        print(f"      [PATCHING] Auto-repairing layout bugs in '{os.path.basename(file_path)}'...")
        
        # Patch invalid ad slots (replacing <div class="ad-slot ad-leaderboard"> with the correct <ins> version)
        old_div_ad_pattern = re.compile(
            r'<!-- Header Leaderboard Ad -->\s*<div class="ad-slot ad-leaderboard">.*?</div>\s*</div>',
            re.DOTALL
        )
        if old_div_ad_pattern.search(content):
            content = old_div_ad_pattern.sub(CORRECT_LEADERBOARD_AD, content)
            patched = True

        # Second variant replacement for divs
        old_div_ad_pattern_simple = re.compile(
            r'<div class="ad-slot ad-leaderboard">\s*<div style="font-size: 1.1rem; font-weight: 700; color: var\(--google-blue\);">728 x 90 Leaderboard Placeholder</div>\s*<div style="font-size: 0.8rem; color: var\(--text-muted\);">Programmatic News Aggregator Ad Placement</div>\s*</div>',
            re.DOTALL
        )
        if old_div_ad_pattern_simple.search(content):
            content = old_div_ad_pattern_simple.sub(CORRECT_LEADERBOARD_AD, content)
            patched = True

        # Patch incorrect inline padding in comparison-blocks
        if "padding: 1.5rem;" in content:
            content = content.replace("padding: 1.5rem;", "padding: 2rem;")
            patched = True

        if patched:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"      [+] File '{os.path.basename(file_path)}' was successfully patched.")
            # Clear issues if they have been repaired
            issues = []

    return issues


def main():
    print("================================================================================")
    print("            NEXUS TECH VISUAL LAYOUT & PADDING AUDITOR")
    print("================================================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_files = [
        os.path.join(base_dir, f) for f in os.listdir(base_dir) if f.endswith(".html")
    ]

    all_passed = True
    total_issues = 0

    for file_path in sorted(html_files):
        rel_path = os.path.relpath(file_path, base_dir)
        print(f"    * Auditing layout inside '{rel_path}'...")
        file_issues = audit_and_patch_file(file_path, auto_patch=True)
        if file_issues:
            all_passed = False
            total_issues += len(file_issues)
            for issue in file_issues:
                print(f"      [FAIL] {issue}")
        else:
            print(f"      [PASS] Layout & padding verified.")

    print("================================================================================")
    if all_passed:
        print(f"             LAYOUT AUDIT PASSED: 0 layout issues remaining.")
        print("================================================================================")
        sys.exit(0)
    else:
        print(f"             LAYOUT AUDIT FAILED: {total_issues} unresolved layout issues.")
        print("================================================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
