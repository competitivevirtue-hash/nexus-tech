#!/usr/bin/env python3
"""
nexus-tech/audit_affiliate_links.py
Audits all compiled HTML pages in nexus-tech/ to ensure compliance with affiliate disclosures,
affiliate tracking parameters, and footer constraints.
"""

import os
import sys
import urllib.parse
from bs4 import BeautifulSoup

TARGET_TAG = "paytonloop20-20"


def audit_html_file(file_path):
    issues = []
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # 1. Audit Outbound Amazon Links and "Check Price" Buttons
    anchors = soup.find_all("a")
    for a in anchors:
        href = a.get("href", "")
        text = a.get_text().strip()
        classes = a.get("class", [])

        # Check if it is an Amazon link or a "Check Price" button
        is_amazon = "amazon.com" in href.lower()
        is_check_price = "check price" in text.lower()

        if is_amazon or is_check_price:
            if not href:
                issues.append(f"Button/Link '{text}' has no href attribute.")
                continue

            parsed_url = urllib.parse.urlparse(href)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            tag_val = query_params.get("tag", [None])[0]

            if tag_val != TARGET_TAG:
                issues.append(
                    f"Link/Button '{text}' (href: '{href}') does not have the required affiliate tag '{TARGET_TAG}'."
                )

    # 2. Audit Footer for Trademark Footnotes
    footers = soup.find_all("footer")
    for footer in footers:
        footer_text = footer.get_text()
        
        # Check for trademark symbols or footnote keywords
        for symbol in ["™", "®"]:
            if symbol in footer_text:
                issues.append(f"Footer contains restricted trademark symbol '{symbol}'.")
                
        for word in ["trademark", "property of", "licensed by", "footnote"]:
            if word in footer_text.lower():
                issues.append(f"Footer contains restricted trademark footnote word: '{word}'.")

    return issues


def main():
    print("================================================================================")
    print("            NEXUS TECH AFFILIATE LINK & FOOTER COMPLIANCE AUDITOR")
    print("================================================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_files = [
        os.path.join(base_dir, f) for f in os.listdir(base_dir) if f.endswith(".html")
    ]

    if not html_files:
        print("[WARNING] No HTML files found to audit!")
        sys.exit(0)

    print(f"[-] Scanning {len(html_files)} HTML pages...")
    all_passed = True
    total_issues = 0

    for file_path in sorted(html_files):
        rel_path = os.path.relpath(file_path, base_dir)
        print(f"    * Auditing '{rel_path}'...")
        file_issues = audit_html_file(file_path)
        if file_issues:
            all_passed = False
            total_issues += len(file_issues)
            for issue in file_issues:
                print(f"      [FAIL] {issue}")
        else:
            print(f"      [PASS] Link & footer compliance verified.")

    print("================================================================================")
    if all_passed:
        print(f"             AUDIT PASSED: 0 compliance issues detected across {len(html_files)} pages.")
        print("================================================================================")
        sys.exit(0)
    else:
        print(f"             AUDIT FAILED: {total_issues} compliance issue(s) detected.")
        print("================================================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
