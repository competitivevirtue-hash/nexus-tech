#!/usr/bin/env python3
"""
verify_deployment.py
QA verification script for validating DOM media states and YouTube iframe embed sources.
"""

import os
import sys
import re
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
    print("            NEXUS TECH QA MEDIA PLAYBACK & DOM AUDITOR")
    print("================================================================================")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Verify gaming.html featured video
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
        print("    [FAIL] Aspect ratio container '.video-aspect-ratio' not found")
        sys.exit(1)
        
    iframe = aspect_container.find("iframe")
    issue = verify_media_element(iframe, "gaming.html")
    if issue:
        print(f"    [FAIL] {issue}")
        sys.exit(1)
        
    # 2. Verify all gaming article detail subpages
    html_files = [f for f in os.listdir(base_dir) if f.startswith("article_") and f.endswith(".html")]
    print(f"[-] Scanning {len(html_files)} generated article detail subpages...")
    
    gaming_articles_count = 0
    verified_articles_count = 0
    
    for filename in sorted(html_files):
        path = os.path.join(base_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            article_soup = BeautifulSoup(f.read(), "html.parser")
            
        # Check if the article is in the Gaming category
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
            verified_articles_count += 1
            
    print("================================================================================")
    print(f"             QA MEDIA PASSED: Verified {verified_articles_count} gaming videos across {gaming_articles_count} gaming articles.")
    print("================================================================================")
    sys.exit(0)

if __name__ == "__main__":
    main()
