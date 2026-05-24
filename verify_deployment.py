#!/usr/bin/env python3
"""
verify_deployment.py
QA verification script for validating DOM media states, YouTube iframe embed sources,
the "Nexus Strategic Verdict" boxes, and sitemap.xml validity and completeness.
"""

import os
import sys
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def verify_media_element(iframe, file_path):
    if not iframe:
        return "Missing <iframe> element"
    
    src = iframe.get("src", "")
    if not src:
        return "<iframe> has no src attribute"
        
    # Regex to match valid youtube embed format: https://www.youtube.com/embed/{11-char-id}
    pattern = r'^https://www\.youtube\.com/embed/([a-zA-Z0-9_-]{11})$'
    match = re.match(pattern, src)
    if not match:
        return f"<iframe> src '{src}' does not match expected YouTube embed pattern"
        
    video_id = match.group(1)
    print(f"    [PASS] Verified video ID '{video_id}' in '{file_path}'")
    return None

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
        
    # Extract all <loc> values from the sitemap
    # Sitemaps usually have a namespace: {http://www.sitemaps.org/schemas/sitemap/0.9}
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    loc_elements = root.findall('.//ns:loc', namespaces)
    if not loc_elements:
        # Try finding without namespace if namespace not found
        loc_elements = root.findall('.//loc')
        
    sitemap_urls = [loc.text for loc in loc_elements if loc.text]
    print(f"    [INFO] Found {len(sitemap_urls)} URLs in 'sitemap.xml'.")
    
    # Map URLs to local files and verify they exist
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
    
    # 2. Verify gaming.html featured video
    gaming_path = os.path.join(base_dir, "gaming.html")
    if not os.path.exists(gaming_path):
        print(f"[ERROR] 'gaming.html' not found at {gaming_path}")
        sys.exit(1)
        
    print(f"[-] Auditing '{os.path.basename(gaming_path)}'...")
    with open(gaming_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    # Check for featured video frame aspect ratio container
    aspect_container = soup.find(class_="video-aspect-ratio")
    if not aspect_container:
        print("    [FAIL] Aspect ratio container '.video-aspect-ratio' not found in gaming.html")
        sys.exit(1)
        
    iframe = aspect_container.find("iframe")
    issue = verify_media_element(iframe, "gaming.html")
    if issue:
        print(f"    [FAIL] {issue}")
        sys.exit(1)
        
    # 3. Verify all article detail subpages
    html_files = [f for f in os.listdir(base_dir) if f.startswith("article_") and f.endswith(".html")]
    print(f"[-] Scanning {len(html_files)} generated article detail subpages...")
    
    gaming_articles_count = 0
    verified_gaming_videos_count = 0
    
    # Ensure all files are checked for sitemap inclusion
    for filename in sorted(html_files):
        expected_url = f"{base_url}{filename}"
        if expected_url not in sitemap_urls:
            print(f"    [FAIL] Article '{filename}' is not indexed in 'sitemap.xml'")
            sys.exit(1)
            
        path = os.path.join(base_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            article_soup = BeautifulSoup(f.read(), "html.parser")
            
        # Verify verdict box exists in EVERY article page
        verdict_box = article_soup.find(class_="verdict-box")
        if not verdict_box:
            print(f"    [FAIL] Article '{filename}' is missing '.verdict-box' container")
            sys.exit(1)
            
        verdict_header = verdict_box.find("h3")
        if not verdict_header or "Nexus Strategic Verdict" not in verdict_header.get_text():
            print(f"    [FAIL] Article '{filename}' has a '.verdict-box' but is missing the 'Nexus Strategic Verdict' header")
            sys.exit(1)
            
        verdict_text = verdict_box.find("p")
        if not verdict_text or not verdict_text.get_text().strip():
            print(f"    [FAIL] Article '{filename}' has an empty '.verdict-box' text block")
            sys.exit(1)
            
        # Check category specific details
        category_tag = article_soup.find(class_=lambda x: x and "category-tag" in x)
        if category_tag and category_tag.get_text().strip() == "Gaming":
            gaming_articles_count += 1
            article_aspect = article_soup.find(class_="video-aspect-ratio")
            if not article_aspect:
                print(f"    [FAIL] Gaming article '{filename}' is missing '.video-aspect-ratio' container")
                sys.exit(1)
                
            article_iframe = article_aspect.find("iframe")
            issue = verify_media_element(article_iframe, filename)
            if issue:
                print(f"    [FAIL] Gaming article '{filename}': {issue}")
                sys.exit(1)
            verified_gaming_videos_count += 1
            
    # Check that core static layouts are also indexed in the sitemap
    for core_page in ["index.html", "gaming.html", "reviews.html", "privacy.html", "terms.html", "disclosure.html"]:
        expected_url = f"{base_url}{core_page}"
        if expected_url not in sitemap_urls:
            print(f"    [FAIL] Core static page '{core_page}' is not indexed in 'sitemap.xml'")
            sys.exit(1)

    print("================================================================================")
    print(f"             QA PASSED: Verified 'sitemap.xml' structure & complete coverage.")
    print(f"             Verified '.verdict-box' present in all {len(html_files)} articles.")
    print(f"             Verified {verified_gaming_videos_count} gaming videos across {gaming_articles_count} gaming articles.")
    print("================================================================================")
    sys.exit(0)

if __name__ == "__main__":
    main()
