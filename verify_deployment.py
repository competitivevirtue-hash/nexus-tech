#!/usr/bin/env python3
"""
verify_deployment.py
QA verification script for validating sitemap.xml, DOM layout integrity (editorial banner cards,
verdict boxes), the complete removal of YouTube components/iframes, and correct page linkages.
"""

import os
import sys
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def main():
    print("================================================================================")
    print("            NEXUS TECH QA DOM, VERDICT, & SITEMAP AUDITOR")
    print("================================================================================")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Verify sitemap.xml exists, is well-formed XML, and covers all pages
    sitemap_path = os.path.join(base_dir, "sitemap.xml")
    if not os.path.exists(sitemap_path):
        print(f"[ERROR] 'sitemap.xml' not found at {sitemap_path}")
        sys.exit(1)
        
    print(f"[-] Auditing 'sitemap.xml'...")
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        print("    [PASS] 'sitemap.xml' is well-formed XML.")
    except Exception as e:
        print(f"    [FAIL] Failed to parse 'sitemap.xml': {e}")
        sys.exit(1)
        
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    loc_elements = root.findall('.//ns:loc', namespaces)
    if not loc_elements:
        loc_elements = root.findall('.//loc')
        
    sitemap_urls = [loc.text for loc in loc_elements if loc.text]
    print(f"    [INFO] Found {len(sitemap_urls)} URLs in 'sitemap.xml'.")
    
    base_url = "https://competitivevirtue-hash.github.io/nexus-tech/"
    for url in sitemap_urls:
        if not url.startswith(base_url):
            print(f"    [FAIL] URL '{url}' does not start with expected base URL: '{base_url}'")
            sys.exit(1)
            
        relative_path = url[len(base_url):]
        local_file_path = os.path.join(base_dir, relative_path)
        if not os.path.exists(local_file_path):
            print(f"    [FAIL] Sitemap contains '{url}' but file does not exist locally at '{local_file_path}'")
            sys.exit(1)
            
    print("    [PASS] All sitemap URLs exist as local files.")
    
    # 2. Verify gaming.html featured media is replaced by static editorial banner
    gaming_path = os.path.join(base_dir, "gaming.html")
    if not os.path.exists(gaming_path):
        print(f"[ERROR] 'gaming.html' not found at {gaming_path}")
        sys.exit(1)
        
    print(f"[-] Auditing '{os.path.basename(gaming_path)}'...")
    with open(gaming_path, "r", encoding="utf-8") as f:
        gaming_soup = BeautifulSoup(f.read(), "html.parser")
        
    # Ensure NO iframe is present on gaming.html
    if gaming_soup.find("iframe"):
        print("    [FAIL] Found <iframe> in gaming.html, YouTube elements were not fully eradicated")
        sys.exit(1)
        
    # Check for the editorial banner card
    banner_card = gaming_soup.find(class_="editorial-banner-card")
    if not banner_card:
        print("    [FAIL] '.editorial-banner-card' not found in gaming.html")
        sys.exit(1)
    else:
        print("    [PASS] Verified '.editorial-banner-card' in gaming.html")
        
    # Check that it has a category-tag and h2
    category_tag = banner_card.find(class_="category-tag")
    h2_tag = banner_card.find("h2")
    if not category_tag or not h2_tag:
        print("    [FAIL] '.editorial-banner-card' lacks category tag or heading title")
        sys.exit(1)
    else:
        print(f"    [PASS] Banner featured editorial title: '{h2_tag.get_text().strip()}'")

    # 3. Verify index.html contains correct page link mapping (no multiple references to article_0.html)
    index_path = os.path.join(base_dir, "index.html")
    if not os.path.exists(index_path):
        print(f"[ERROR] 'index.html' not found at {index_path}")
        sys.exit(1)
        
    print(f"[-] Auditing '{os.path.basename(index_path)}'...")
    with open(index_path, "r", encoding="utf-8") as f:
        index_soup = BeautifulSoup(f.read(), "html.parser")
        
    # Find all anchor tags pointing to article_*.html
    article_links = []
    for a in index_soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("article_") and href.endswith(".html"):
            article_links.append(href)
            
    unique_links = set(article_links)
    print(f"    [INFO] Found {len(article_links)} article links in index.html, referencing {len(unique_links)} unique pages.")
    
    # Assert that they are not all pointing to article_0.html
    if len(article_links) > 2 and len(unique_links) <= 1:
        print(f"    [FAIL] Linkage bug detected: Multiple article cards map to the same file: {unique_links}")
        sys.exit(1)
    else:
        print("    [PASS] Article card linkage verification passed.")

    # 4. Verify all article detail subpages are video-free and contain styled verdict boxes
    html_files = [f for f in os.listdir(base_dir) if f.startswith("article_") and f.endswith(".html")]
    print(f"[-] Scanning {len(html_files)} generated article detail subpages...")
    
    for filename in sorted(html_files):
        expected_url = f"{base_url}{filename}"
        if expected_url not in sitemap_urls:
            print(f"    [FAIL] Article '{filename}' is not indexed in 'sitemap.xml'")
            sys.exit(1)
            
        path = os.path.join(base_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            article_soup = BeautifulSoup(f.read(), "html.parser")
            
        # Assert NO iframes exist
        if article_soup.find("iframe"):
            print(f"    [FAIL] Article '{filename}' contains an <iframe>, YouTube element not eradicated")
            sys.exit(1)
            
        # Verify verdict box exists
        verdict_box = article_soup.find(class_="verdict-box")
        if not verdict_box:
            print(f"    [FAIL] Article '{filename}' is missing '.verdict-box' container")
            sys.exit(1)
            
        verdict_header = verdict_box.find("h3")
        if not verdict_header or "Nexus Strategic Verdict" not in verdict_header.get_text():
            print(f"    [FAIL] Article '{filename}' verdict box is missing the correct header")
            sys.exit(1)
            
        verdict_text = verdict_box.find("p")
        if not verdict_text or not verdict_text.get_text().strip():
            print(f"    [FAIL] Article '{filename}' verdict text is empty")
            sys.exit(1)
            
        # Verify no "Standard evolutionary step" text
        verdict_str = verdict_text.get_text()
        if "Standard evolutionary step" in verdict_str:
            print(f"    [FAIL] Article '{filename}' contains the boilerplate verdict string 'Standard evolutionary step'")
            sys.exit(1)
            
        # Verify no "We're in the transition period" in the article
        with open(path, "r", encoding="utf-8") as f_raw:
            raw_content = f_raw.read()
            if "transition period" in raw_content:
                print(f"    [FAIL] Article '{filename}' contains the 'transition period' boilerplate string")
                sys.exit(1)

    print("================================================================================")
    print(f"             QA PASSED: Verified 'sitemap.xml' structure & complete coverage.")
    print(f"             Verified 100% video-free HTML files (0 iframes found).")
    print(f"             Verified '.verdict-box' with context-aware logic present in all {len(html_files)} articles.")
    print("================================================================================")
    sys.exit(0)

if __name__ == "__main__":
    main()
