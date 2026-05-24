#!/usr/bin/env python3
"""
Nexus Tech Network Link Verification Suite
Scans all compiled HTML files in the nexus-tech folder, parses anchors, and checks for broken internal paths.
"""

import os
import sys
from bs4 import BeautifulSoup

def main():
    print("================================================================================")
    print("            NEXUS TECH NETWORK COMPREHENSIVE LINK AUDITOR")
    print("================================================================================")
    
    base_dir = "nexus-tech"
    if not os.path.exists(base_dir):
        print(f"[ERROR] Target directory '{base_dir}' does not exist.")
        sys.exit(1)
        
    # Get all HTML files in directory
    html_files = [f for f in os.listdir(base_dir) if f.endswith(".html")]
    print(f"[+] Discovered {len(html_files)} HTML pages inside '{base_dir}/':")
    for f in sorted(html_files):
        print(f"    * {f} ({os.path.getsize(os.path.join(base_dir, f)):,} bytes)")
        
    # Standard compliance files
    compliance_files = ["privacy.html", "terms.html", "disclosure.html"]
    for comp in compliance_files:
        if comp not in html_files:
            print(f"[WARNING] Compliance file '{comp}' is missing from the directory!")
            
    audit_passed = True
    total_links_checked = 0
    broken_links_count = 0
    
    # Audit each HTML file
    for html_file in sorted(html_files):
        path = os.path.join(base_dir, html_file)
        print(f"\n[-] Auditing links inside '{path}'...")
        try:
            with open(path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
        except Exception as e:
            print(f"    [ERROR] Failed to read/parse file: {e}")
            audit_passed = False
            continue
            
        links = soup.find_all("a")
        checked_links_count = 0
        
        for link in links:
            href = link.get("href")
            if not href:
                continue
                
            # Filter for local page links (ignore external links, mailto, tel, or pure hashes)
            if href.startswith("http://") or href.startswith("https://") or href.startswith("mailto:") or href.startswith("tel:") or href.startswith("#"):
                continue
                
            # Strip hash anchor fragments
            target_file = href.split("#")[0]
            if not target_file:
                continue
                
            checked_links_count += 1
            total_links_checked += 1
            
            # Target path check
            target_path = os.path.join(base_dir, target_file)
            if os.path.exists(target_path):
                # Valid
                pass
            else:
                print(f"    [BROKEN] Link to '{href}' target is missing ({target_file})!")
                broken_links_count += 1
                audit_passed = False
                
        print(f"    [+] Checked {checked_links_count} local anchor link(s).")
        
    print("\n================================================================================")
    print(f"             AUDIT SUMMARY: Checked {total_links_checked} link(s). Broken: {broken_links_count}")
    print("================================================================================")
    if audit_passed:
        print("             ALL CROSS-PAGE LINKS VERIFIED & SECURE (PASSED)")
        print("================================================================================")
        sys.exit(0)
    else:
        print("             LINK VERIFICATION AUDIT DETECTED BROKEN PATHS (FAILED)")
        print("================================================================================")
        sys.exit(1)

if __name__ == "__main__":
    main()
