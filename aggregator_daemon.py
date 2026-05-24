#!/usr/bin/env python3
"""
Nexus Tech & Gaming Aggregator Daemon
Created as part of Project Helios.

Queries RSS/Atom feeds, compiles a Google-themed light network layout, 
generates standalone article subpages, injects dynamic SEO tags (title < 60, meta description < 160),
and embeds relevant affiliate comparison blocks from reviews.html based on keyword content mapping.
"""

import os
import re
import xml.etree.ElementTree as ET
import pandas as pd
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_POINTS = 250

# --- AFFILIATE TRACKING ID & GLOBAL VARIABLES ---
TRACKING_ID = "paytonloop20-20"
AMAZON_AUDIO_URL = f"https://www.amazon.com/dp/B08H2WY1Z2?tag={TRACKING_ID}"
AMAZON_DISPLAY_URL = f"https://www.amazon.com/dp/B0C4Z8RF9P?tag={TRACKING_ID}"
AMAZON_GRAPHICS_URL = f"https://www.amazon.com/s?k=RTX+5090&tag={TRACKING_ID}"

# --- COMPLIANCE FOOTER HTML ---
FOOTER_HTML = """
    <footer>
        <div style="margin-bottom: 1rem;">
            <a href="privacy.html" style="color: var(--text-muted); text-decoration: none; margin: 0 10px; font-weight: 500;">Privacy Policy</a> | 
            <a href="terms.html" style="color: var(--text-muted); text-decoration: none; margin: 0 10px; font-weight: 500;">Terms of Service</a> | 
            <a href="disclosure.html" style="color: var(--text-muted); text-decoration: none; margin: 0 10px; font-weight: 500;">Affiliate Disclosure</a>
        </div>
        &copy; 2026 Nexus Tech & Gaming. All rights reserved.
    </footer>
"""

# --- STANDARD PROGRAMMATIC AD SLOTS ---
AD_LEADERBOARD_HTML = """
        <!-- Header Leaderboard Ad -->
        <ins class="adsbygoogle ad-slot ad-leaderboard"
             style="display: flex !important; text-decoration: none;"
             data-ad-client="ca-pub-7561845942385102"
             data-ad-slot="7289012345">
            <div style="font-size: 1.1rem; font-weight: 700; color: var(--google-blue);">728 x 90 Leaderboard Placeholder</div>
            <div style="font-size: 0.8rem; color: var(--text-muted);">Programmatic News Aggregator Ad Placement (adsbygoogle)</div>
        </ins>
"""

AD_RECTANGLE_HTML = """
                <!-- In-Article Rectangle Ad Placement -->
                <ins class="adsbygoogle ad-slot"
                     style="display: flex !important; min-height: 120px; text-decoration: none;"
                     data-ad-client="ca-pub-7561845942385102"
                     data-ad-slot="3002501234">
                    <div style="font-size: 1rem; font-weight: 700; color: var(--google-red);">In-Article Native Placement [Tablet & Mobile Adaptive Slot]</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">Optimized CTR Performance Container (adsbygoogle)</div>
                </ins>
"""

AD_SKYSCRAPER_HTML = """
                <!-- Sidebar Skyscraper Ad -->
                <ins class="adsbygoogle ad-slot ad-skyscraper"
                     style="display: flex !important; text-decoration: none;"
                     data-ad-client="ca-pub-7561845942385102"
                     data-ad-slot="3006001234">
                    <div style="font-size: 1.1rem; font-weight: 700; color: var(--google-green); writing-mode: vertical-rl; transform: rotate(180deg); margin-bottom: 1rem;">300 x 600 Skyscraper Placement</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">Google Ad Manager (adsbygoogle)</div>
                </ins>
"""


# --- PRODUCT BLOCKS FOR CONTENT MAPPING ---
PRODUCT_BLOCKS = {
    "audio": """
        <!-- Mapped Affiliate Product: Audio -->
        <div class="comparison-block" style="border: 2px solid var(--google-blue); padding: 2rem; margin-top: 2rem;">
            <span class="category-tag tag-blue" style="margin-bottom: 0.5rem;">Recommended Hardware Match</span>
            <div class="product-info">
                <div class="product-image-box"><i class="fa-solid fa-headphones"></i></div>
                <div class="product-details">
                    <span class="category-tag tag-blue">Audio</span>
                    <h3>Nexus Alpha Gaming Headset</h3>
                    <div class="star-rating">
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star-half-stroke"></i>
                    </div>
                    <div class="product-verdict"><strong>Verdict:</strong> Exceptional spatial soundstage, slightly heavy.</div>
                </div>
            </div>
            <div class="product-price-matrix" style="margin-top: 1rem;">
                <div class="price-row"><span>Amazon</span><span class="price-val">$129.99</span></div>
                <div class="price-row"><span>Best Buy</span><span class="price-val">$134.99</span></div>
                <a href="{AMAZON_AUDIO_URL}" class="check-price-btn btn-blue" target="_blank">Check Price / Comparison</a>
            </div>
        </div>
    """,
    "display": """
        <!-- Mapped Affiliate Product: Display -->
        <div class="comparison-block" style="border: 2px solid var(--google-red); padding: 2rem; margin-top: 2rem;">
            <span class="category-tag tag-red" style="margin-bottom: 0.5rem;">Recommended Hardware Match</span>
            <div class="product-info">
                <div class="product-image-box"><i class="fa-solid fa-desktop"></i></div>
                <div class="product-details">
                    <span class="category-tag tag-red">Display</span>
                    <h3>Helios UltraWide Quantum Monitor</h3>
                    <div class="star-rating">
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star"></i>
                    </div>
                    <div class="product-verdict"><strong>Verdict:</strong> Flawless color volume, spectacular OLED performance.</div>
                </div>
            </div>
            <div class="product-price-matrix" style="margin-top: 1rem;">
                <div class="price-row"><span>Amazon</span><span class="price-val">$899.99</span></div>
                <div class="price-row"><span>Best Buy</span><span class="price-val">$910.00</span></div>
                <a href="{AMAZON_DISPLAY_URL}" class="check-price-btn btn-red" target="_blank">Check Price / Comparison</a>
            </div>
        </div>
    """,
    "graphics": """
        <!-- Mapped Affiliate Product: Graphics -->
        <div class="comparison-block" style="border: 2px solid var(--google-green); padding: 2rem; margin-top: 2rem;">
            <span class="category-tag tag-green" style="margin-bottom: 0.5rem;">Recommended Hardware Match</span>
            <div class="product-info">
                <div class="product-image-box"><i class="fa-solid fa-microchip"></i></div>
                <div class="product-details">
                    <span class="category-tag tag-green">Graphics</span>
                    <h3>Apex RTX 5090 Graphics Card</h3>
                    <div class="star-rating">
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star"></i>
                        <i class="fa-solid fa-star-half-stroke"></i>
                    </div>
                    <div class="product-verdict"><strong>Verdict:</strong> Outrageous raw rendering power, extreme cost.</div>
                </div>
            </div>
            <div class="product-price-matrix" style="margin-top: 1rem;">
                <div class="price-row"><span>Amazon</span><span class="price-val">$1599.99</span></div>
                <div class="price-row"><span>Best Buy</span><span class="price-val">$1649.99</span></div>
                <a href="{AMAZON_GRAPHICS_URL}" class="check-price-btn btn-green" target="_blank">Check Price / Comparison</a>
            </div>
        </div>
    """
}

# --- HELPERS ---

def get_headers():
    return {
        "User-Agent": "ProjectHeliosTDA/1.0 (contact: admin@projecthelios.org; Research Sandbox)",
        "Accept": "application/xml,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8"
    }

def clean_html(text):
    if not text:
        return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

# --- FEED INGESTION PIPELINES ---

def fetch_techcrunch_feed():
    url = "https://techcrunch.com/feed/"
    print("[-] Aggregator: Fetching TechCrunch RSS feed...")
    articles = []
    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            channel = root.find("channel")
            items = channel.findall("item") if channel is not None else []
            for item in items[:6]:
                try:
                    title_el = item.find("title")
                    link_el = item.find("link")
                    desc_el = item.find("description")
                    pub_date_el = item.find("pubDate")
                    
                    if title_el is None or not title_el.text or link_el is None or not link_el.text:
                        continue
                        
                    title = title_el.text
                    link = link_el.text
                    desc = desc_el.text if desc_el is not None else ""
                    desc_cleaned = clean_html(desc)
                    if not desc_cleaned:
                        continue
                        
                    # Skip transition period placeholders
                    if "transition period" in title.lower() or "transition period" in desc_cleaned.lower():
                        continue
                        
                    desc_cleaned = desc_cleaned[:180] + "..." if len(desc_cleaned) > 180 else desc_cleaned
                    
                    pub_date = pub_date_el.text if pub_date_el is not None else "May 24, 2026"
                    pub_date = pub_date.split(" +")[0] if " +" in pub_date else pub_date
                    
                    articles.append({
                        "title": title,
                        "link": link,
                        "summary": desc_cleaned,
                        "date": pub_date,
                        "category": "Computing" if len(articles) % 2 == 0 else "Hardware"
                    })
                except Exception as e:
                    print(f"      [!] Skipping single TechCrunch item due to parse error: {e}")
                    continue
            if len(articles) > 0:
                print(f"    [+] Successfully aggregated {len(articles)} articles from TechCrunch.")
                return articles
    except Exception as e:
        print(f"    [!] TechCrunch feed failed: {e}.")
    return []

def fetch_sec_feed():
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&owner=include&start=0&count=100&output=atom"
    print("[-] Aggregator: Fetching SEC EDGAR Atom feed...")
    filings = []
    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            for entry in entries[:4]:
                try:
                    title_el = entry.find('{http://www.w3.org/2005/Atom}title')
                    link_el = entry.find('{http://www.w3.org/2005/Atom}link')
                    summary_el = entry.find('{http://www.w3.org/2005/Atom}summary')
                    
                    if title_el is None or not title_el.text or link_el is None:
                        continue
                        
                    title_text = title_el.text
                    temp_title = title_text
                    for prefix in ["Form 4 - ", "4 - "]:
                        if temp_title.startswith(prefix):
                            temp_title = temp_title[len(prefix):]
                    clean_title = temp_title.split(" - ")[0]
                    link = link_el.attrib.get("href")
                    if not link:
                        continue
                        
                    summary_text = summary_el.text if summary_el is not None else ""
                    summary_cleaned = clean_html(summary_text)
                    if not summary_cleaned:
                        continue
                        
                    if "transition period" in title_text.lower() or "transition period" in summary_cleaned.lower():
                        continue
                        
                    summary_cleaned = summary_cleaned[:120] + "..." if len(summary_cleaned) > 120 else summary_cleaned
                    
                    filings.append({
                        "title": f"SEC Alert: Corporate Insider flows at {clean_title}",
                        "link": link,
                        "summary": summary_cleaned,
                        "date": "May 24, 2026",
                        "category": "Fintech"
                    })
                except Exception as e:
                    print(f"      [!] Skipping single SEC item due to parse error: {e}")
                    continue
            if len(filings) > 0:
                print(f"    [+] Successfully harvested {len(filings)} filings from SEC.")
                return filings
    except Exception as e:
        print(f"    [!] SEC EDGAR feed failed: {e}.")
    return []

def fetch_steam_feed():
    url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=1091500&count=3"
    print("[-] Aggregator: Fetching Steam Web API feed...")
    articles = []
    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            newsitems = data.get("appnews", {}).get("newsitems", [])
            for item in newsitems:
                try:
                    title = item.get("title")
                    link = item.get("url")
                    contents = item.get("contents")
                    
                    if not title or not link or not contents:
                        continue
                        
                    contents_cleaned = clean_html(contents)
                    if not contents_cleaned:
                        continue
                        
                    if "transition period" in title.lower() or "transition period" in contents_cleaned.lower():
                        continue
                        
                    contents_cleaned = contents_cleaned[:180] + "..." if len(contents_cleaned) > 180 else contents_cleaned
                    
                    articles.append({
                        "title": f"Steam Update: {title}",
                        "link": link,
                        "summary": contents_cleaned,
                        "date": "May 24, 2026",
                        "category": "Gaming"
                    })
                except Exception as e:
                    print(f"      [!] Skipping single Steam item due to parse error: {e}")
                    continue
            if len(articles) > 0:
                print(f"    [+] Successfully aggregated {len(articles)} articles from Steam.")
                return articles
    except Exception as e:
        print(f"    [!] Steam Web API feed failed: {e}.")
    return []

def fetch_reddit_feed():
    url = "https://www.reddit.com/r/GamingLeaksAndRumours/.json?limit=5"
    print("[-] Aggregator: Fetching Reddit JSON Gaming feed...")
    articles = []
    try:
        headers = get_headers()
        headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ProjectHelios/1.0"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            children = data.get("data", {}).get("children", [])
            for child in children:
                try:
                    post = child.get("data", {})
                    title = post.get("title")
                    permalink = post.get("permalink")
                    selftext = post.get("selftext")
                    
                    if not title or not permalink or not selftext:
                        continue
                        
                    link = f"https://www.reddit.com{permalink}"
                    summary = clean_html(selftext)
                    if not summary:
                        continue
                        
                    if "transition period" in title.lower() or "transition period" in summary.lower():
                        continue
                        
                    summary = summary[:180] + "..." if len(summary) > 180 else summary
                    
                    articles.append({
                        "title": f"Gaming Rumor: {title}",
                        "link": link,
                        "summary": summary,
                        "date": "May 24, 2026",
                        "category": "Gaming"
                    })
                except Exception as e:
                    print(f"      [!] Skipping single Reddit item due to parse error: {e}")
                    continue
            if len(articles) > 0:
                print(f"    [+] Successfully aggregated {len(articles)} articles from Reddit.")
                return articles
    except Exception as e:
        print(f"    [!] Reddit JSON feed failed: {e}.")
    return []

def fetch_wccftech_feed():
    url = "https://wccftech.com/category/games/feed/"
    print("[-] Aggregator: Fetching Wccftech Games RSS feed...")
    articles = []
    try:
        resp = requests.get(url, headers=get_headers(), timeout=10)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            channel = root.find("channel")
            items = channel.findall("item") if channel is not None else []
            for item in items[:4]:
                try:
                    title_el = item.find("title")
                    link_el = item.find("link")
                    desc_el = item.find("description")
                    
                    if title_el is None or not title_el.text or link_el is None or not link_el.text:
                        continue
                        
                    title = title_el.text
                    link = link_el.text
                    desc = desc_el.text if desc_el is not None else ""
                    desc_cleaned = clean_html(desc)
                    if not desc_cleaned:
                        continue
                        
                    if "transition period" in title.lower() or "transition period" in desc_cleaned.lower():
                        continue
                        
                    desc_cleaned = desc_cleaned[:180] + "..." if len(desc_cleaned) > 180 else desc_cleaned
                    articles.append({
                        "title": f"Industry News: {title}",
                        "link": link,
                        "summary": desc_cleaned,
                        "date": "May 24, 2026",
                        "category": "Gaming"
                    })
                except Exception as e:
                    print(f"      [!] Skipping single Wccftech item due to parse error: {e}")
                    continue
            if len(articles) > 0:
                print(f"    [+] Successfully aggregated {len(articles)} articles from Wccftech.")
                return articles
    except Exception as e:
        print(f"    [!] Wccftech Games feed failed: {e}.")
    return []

# --- DYNAMIC CONTENT MAPPING AND SEO SYNTHESIS ---

def get_product_block_from_text(text):
    """Maps article keywords back to relevant affiliate product blocks with dynamic tracking link substitution."""
    txt_lower = text.lower()
    block = None
    if any(k in txt_lower for k in ["gpu", "rtx", "graphics", "fabrication", "silicon", "computing", "chips", "nvidia", "hardware", "ibm", "fission", "nuclear", "energy", "solar", "solarsquare"]):
        block = PRODUCT_BLOCKS["graphics"]
    elif any(k in txt_lower for k in ["oled", "display", "monitor", "screen", "pixels", "quantum", "wearable", "clock", "watch", "bee", "dreamie"]):
        block = PRODUCT_BLOCKS["display"]
    elif any(k in txt_lower for k in ["audio", "headset", "headphones", "soundstage", "sound", "phone", "app", "meta", "voice", "speaker", "alarm"]):
        block = PRODUCT_BLOCKS["audio"]
        
    if block:
        return block.replace("{AMAZON_AUDIO_URL}", AMAZON_AUDIO_URL)\
                    .replace("{AMAZON_DISPLAY_URL}", AMAZON_DISPLAY_URL)\
                    .replace("{AMAZON_GRAPHICS_URL}", AMAZON_GRAPHICS_URL)
    return None

def synthesize_seo_meta(title_text, summary_text):
    """Generates unique, standard-compliant SEO title (<60 chars) and meta description (<160 chars)."""
    # 1. Synthesize Title
    raw_title = f"Nexus Tech: {title_text}"
    if len(raw_title) > 57:
        seo_title = raw_title[:57] + "..."
    else:
        seo_title = raw_title
        
    # 2. Synthesize Meta Description
    raw_desc = clean_html(summary_text)
    if len(raw_desc) > 157:
        seo_desc = raw_desc[:157] + "..."
    else:
        seo_desc = raw_desc
        
    return seo_title, seo_desc

def generate_strategic_verdict(story):
    """Generates a highly context-aware, keyword-based editorial analysis of macro-implications (Nexus Strategic Verdict)."""
    title = story.get("title", "")
    summary = story.get("summary", "")
    category = story.get("category", "")
    
    title_lower = title.lower()
    summary_lower = summary.lower()
    text_lower = f"{title_lower} {summary_lower}"
    
    # 1. Gaming Hardware / Software
    if category == "Gaming" or any(k in text_lower for k in ["gpu", "rtx", "console", "steam", "physics", "rendering", "cyberpunk", "gta"]):
        if any(k in text_lower for k in ["gpu", "rtx", "silicon", "hardware", "spec"]):
            return "Nexus Verdict: Hardware acceleration shifts in the gaming sector are forcing developers to adopt advanced rendering pipelines. Studios must balance visual fidelity with thermal and energy performance profiles."
        elif any(k in text_lower for k in ["patch", "update", "notes", "performance"]):
            return "Nexus Verdict: Post-launch patch cycles reflect the growing complexity of modern cross-platform engines. Optimizing memory leaks and shader compilation remains the primary battlefield for player retention."
        else:
            return "Nexus Verdict: The gaming market is experiencing a shift driven by digital storefronts and subscription model dominance. Publishers must adapt their franchise timelines to align with real-time community engagement loops."
            
    # 2. Hardware / Infrastructure / Silicon
    elif category == "Hardware" or any(k in text_lower for k in ["silicon", "semiconductor", "cooling", "node", "interconnect", "sub-2nm", "nvme"]):
        return "Nexus Verdict: Silicon fabrication constraints and cooling bottlenecks are redefining edge device capabilities. Hardware integrators who master thermal dissipation will hold the strategic advantage in high-density compute markets."
        
    # 3. Computing / AI / Security
    elif category == "Computing" or any(k in text_lower for k in ["ai", "security", "google", "algorithm", "neural", "network", "cybersecurity"]):
        if "security" in text_lower or "privacy" in text_lower:
            return "Nexus Verdict: AI security integration remains highly reactive. Enterprises must institute zero-trust data ingestion boundaries to protect against proprietary leakage and neural poisoning vectors."
        else:
            return "Nexus Verdict: Algorithmic efficiency gains are outpacing raw hardware capabilities. Software vendors optimizing local compilation and token costs will capture major market segments."
            
    # 4. Fintech / SEC / Insider
    elif category == "Fintech" or any(k in text_lower for k in ["sec", "filing", "insider", "stock", "transaction", "berkshire"]):
        return "Nexus Verdict: Regulatory disclosure intervals represent a critical latency gap for market participants. Aggregating corporate insider reallocations provides essential macro-signals for tech sector sector rotation."
        
    # 5. General Fallback (Dynamic keyword insertion)
    words = [w.strip(",.()\"'-") for w in title.split() if len(w) > 4]
    keywords = [w for w in words if w.lower() not in ["about", "their", "there", "would", "could", "should", "under", "while"]]
    focus = keywords[0] if keywords else "this technological development"
    
    return f"Nexus Verdict: The integration of {focus} represents a pivotal evolution in {category.lower()} applications. Strategic leaders should assess adoption velocity and regulatory frameworks before scaling operations."

def compile_article_page(story, idx):
    """Compiles and writes article_{id}.html detail pages with Dynamic SEO and Content Mapping."""
    seo_title, seo_desc = synthesize_seo_meta(story["title"], story["summary"])
    
    # 1. Map content triggers
    mapped_product_html = get_product_block_from_text(story["title"] + " " + story["summary"])
    if mapped_product_html is None:
        mapped_product_html = ""
        
    tag_class = "tag-blue" if story["category"] == "Computing" else "tag-red" if story["category"] == "Hardware" else "tag-yellow" if story["category"] == "Fintech" else "tag-green"
    
    verdict_text = generate_strategic_verdict(story)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{seo_title}</title>
    <meta name="description" content="{seo_desc}">
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header>
        <div class="header-container">
            <div class="logo">Nexus<span>Tech</span></div>
            <nav>
                <a href="index.html">Home</a>
                <a href="gaming.html">Gaming</a>
                <a href="reviews.html">Reviews</a>
            </nav>
        </div>
    </header>

    <div class="main-container">
        {AD_LEADERBOARD_HTML}

        <div class="techcrunch-grid">
            <main style="background-color: var(--card-light); padding: 2rem; border: 1px solid var(--border-light); border-radius: 8px;">
                <span class="category-tag {tag_class}">{story['category']}</span>
                <h1 style="font-size: 2rem; font-weight: 800; margin-top: 0.5rem; margin-bottom: 1rem; color: var(--text-primary);">{story['title']}</h1>
                
                <div class="story-meta" style="margin-bottom: 1.5rem;">
                    <span>Aggregated Network</span> &bull; <span>{story['date']}</span>
                </div>
                
                <p style="font-size: 1.1rem; color: var(--text-muted); margin-bottom: 1.5rem; line-height: 1.7;">
                    {story['summary']}
                </p>
                
                <a href="{story['link']}" style="display: inline-block; color: var(--google-blue); font-weight: 700; text-decoration: none; margin-bottom: 2rem;" target="_blank">
                    Read Original Coverage <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </a>

                <div class="verdict-box">
                    <h3><i class="fa-solid fa-gavel"></i> Nexus Strategic Verdict</h3>
                    <p>{verdict_text}</p>
                </div>

                {mapped_product_html}
            </main>

            <aside class="sidebar">
                {AD_SKYSCRAPER_HTML}
            </aside>
        </div>
    </div>

    {FOOTER_HTML}
</body>
</html>
"""
    file_name = os.path.join(BASE_DIR, f"article_{idx}.html")
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"    [+] Compiled standalone article detail: '{file_name}'")

# --- CORE TEMPLATE COMPILER PIPELINES ---

def compile_index_page(tc_articles, sec_articles, gaming_articles):
    featured = tc_articles[0]
    sub_stories = tc_articles[1:] + sec_articles + gaming_articles
    
    sub_stories_html = ""
    for idx, story in enumerate(sub_stories[:6]):
        tag_class = "tag-blue" if story["category"] == "Computing" else "tag-red" if story["category"] == "Hardware" else "tag-yellow" if story["category"] == "Fintech" else "tag-green"
        # Standalone article detail link (pointing to local article_x.html)
        article_link = f"article_{story.get('id', 0)}.html"
        sub_stories_html += f"""
        <div class="story-card">
            <div>
                <span class="category-tag {tag_class}">{story['category']}</span>
                <h3><a href="{article_link}" style="color: var(--text-primary); text-decoration: none;">{story['title']}</a></h3>
                <p>{story['summary']}</p>
            </div>
            <div class="story-meta">{story['date']} &bull; <i class="fa-regular fa-comment"></i> {5 + idx*3} comments</div>
        </div>
        """
        
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Tech — Automated News Aggregator</title>
    <meta name="description" content="Vibrant news aggregator portal mapping live technology reports and federal insider flows.">
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header>
        <div class="header-container">
            <div class="logo">Nexus<span>Tech</span></div>
            <nav>
                <a href="index.html" class="active">Home</a>
                <a href="gaming.html">Gaming</a>
                <a href="reviews.html">Reviews</a>
            </nav>
        </div>
    </header>
 
    <div class="main-container">
        {AD_LEADERBOARD_HTML}
 
        <div class="techcrunch-grid">
            <main>
                <!-- Main Featured News Story -->
                <article class="featured-story">
                    <div style="height: 300px; background: linear-gradient(135deg, #f1f3f4 0%, #e8eaed 100%); display: flex; justify-content: center; align-items: center; font-size: 4.5rem; color: var(--google-blue); border-radius: 6px;">
                        <i class="fa-solid fa-newspaper"></i>
                    </div>
                    <div class="featured-content" style="padding-top: 1.5rem;">
                        <span class="category-tag tag-blue">{featured['category']}</span>
                        <h2><a href="article_{featured.get('id', 0)}.html" style="color: var(--text-primary); text-decoration: none;">{featured['title']}</a></h2>
                        <p>{featured['summary']}</p>
                        <div class="story-meta">
                            <span>Aggregated Network</span> &bull; <span>{featured['date']}</span> &bull; <span><i class="fa-regular fa-comment"></i> 34 comments</span>
                        </div>
                    </div>
                </article>
 
                {AD_RECTANGLE_HTML}
 
                <!-- Grid of Secondary News Stories -->
                <div class="stories-list">
                    {sub_stories_html}
                </div>
            </main>

            <aside class="sidebar">
                {AD_SKYSCRAPER_HTML}

                <!-- Trending Sidebar Widget -->
                <div class="sidebar-widget">
                    <h4>Trending Tech Index</h4>
                    <div class="trending-item">
                        <span class="trending-num">1</span>
                        <div>
                            <a href="reviews.html" style="color: var(--text-primary); text-decoration: none; font-weight: 600; font-size: 0.9rem;">RTX 5090 Price & Stock Analysis</a>
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">2.9k views</div>
                        </div>
                    </div>
                    <div class="trending-item">
                        <span class="trending-num">2</span>
                        <div>
                            <a href="gaming.html" style="color: var(--text-primary); text-decoration: none; font-weight: 600; font-size: 0.9rem;">CDPR Cyberpunk Sequel Hands-On Preview</a>
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">2.1k views</div>
                        </div>
                    </div>
                    <div class="trending-item">
                        <span class="trending-num">3</span>
                        <div>
                            <a href="article_0.html" style="color: var(--text-primary); text-decoration: none; font-weight: 600; font-size: 0.9rem;">Quantum Silicon Lags & Embedding Limits</a>
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">1.7k views</div>
                        </div>
                    </div>
                </div>
            </aside>
        </div>
    </div>

    {FOOTER_HTML}
</body>
</html>
"""
    return html

def compile_gaming_page(gaming_stories):
    featured_story = gaming_stories[0] if len(gaming_stories) > 0 else None
    
    if featured_story:
        title_display = featured_story["title"]
        for prefix in ["Steam Update: ", "Gaming Rumor: ", "Industry News: ", "Community Hub: "]:
            if title_display.startswith(prefix):
                title_display = title_display[len(prefix):]
        summary_display = featured_story["summary"]
        featured_article_link = f"article_{featured_story.get('id', 0)}.html"
    else:
        title_display = "Cyberpunk 2078: Neon Horizon Hands-On Preview"
        summary_display = "We spend 3 hours playing the upcoming CD Projekt Red RPG. From the sub-surface matrix layers to the revised neon-fluid physics, this could be the definitive game of the generation."
        featured_article_link = "#"

    news_html = ""
    for idx, story in enumerate(gaming_stories[:6]):
        tag_class = "tag-green"
        article_link = f"article_{story.get('id', 0)}.html"
        news_html += f"""
        <div class="game-review-row">
            <div class="game-thumb"><i class="fa-solid fa-gamepad"></i></div>
            <div class="game-review-content">
                <span class="category-tag {tag_class}">{story.get('category', 'Gaming')}</span>
                <h4>{story['title']}</h4>
                <p style="color: var(--text-muted); font-size: 0.85rem;">{story['summary']}</p>
            </div>
            <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem;">
                <span class="game-rating-badge">{9.8 - idx*0.3:.1f} / 10</span>
                <a href="{article_link}" class="check-price-btn btn-blue" style="padding: 0.4rem 0.8rem; font-size: 0.75rem; border-width: 1px;">Read More</a>
            </div>
        </div>
        """
        
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Gaming Lounge — Video Previews & Reviews</title>
    <meta name="description" content="Engaging gaming lounges presenting live CDPR details and trending reviews.">
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header>
        <div class="header-container">
            <div class="logo">Nexus<span>Tech</span></div>
            <nav>
                <a href="index.html">Home</a>
                <a href="gaming.html" class="active">Gaming</a>
                <a href="reviews.html">Reviews</a>
            </nav>
        </div>
    </header>
 
    <div class="main-container">
        {AD_LEADERBOARD_HTML}
 
        <div class="media-lounge-grid">
            <main>
                <!-- Editorial Banner Card -->
                <div class="editorial-banner-card">
                    <div style="position: absolute; top: -50px; right: -50px; width: 200px; height: 200px; background: rgba(255, 255, 255, 0.08); border-radius: 50%;"></div>
                    <div style="position: absolute; bottom: -80px; left: -80px; width: 250px; height: 250px; background: rgba(255, 255, 255, 0.05); border-radius: 50%;"></div>
                    <div style="position: relative; z-index: 2;">
                        <span class="category-tag">Featured Editorial</span>
                        <h2>{title_display}</h2>
                        <p>{summary_display}</p>
                        <a href="{featured_article_link}" class="check-price-btn btn-green" style="display: inline-block; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 4px; font-weight: 700; background-color: #ffffff; color: var(--google-blue); border: none; font-size: 0.95rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Read Featured Story</a>
                    </div>
                </div>
 
                {AD_RECTANGLE_HTML}
 
                <!-- Trending Game Reviews List -->
                <div style="margin-top: 2rem;">
                    <h3 style="font-size: 1.5rem; font-weight: 800; margin-bottom: 1.25rem; border-bottom: 2px solid var(--border-light); padding-bottom: 0.5rem; color: var(--text-primary);">Trending Reviews</h3>
                    <div class="game-reviews-list">
                        {news_html}
                    </div>
                </div>
            </main>
 
            <aside class="sidebar">
                {AD_SKYSCRAPER_HTML}
            </aside>
        </div>
    </div>
 
    {FOOTER_HTML}
</body>
</html>
"""
    return html

def compile_reviews_page():
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus Tech Reviews — Product Comparison & Price Match</title>
    <meta name="description" content="Technical comparison review matrices mapping pricing data and star ratings.">
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header>
        <div class="header-container">
            <div class="logo">Nexus<span>Tech</span></div>
            <nav>
                <a href="index.html">Home</a>
                <a href="gaming.html">Gaming</a>
                <a href="reviews.html" class="active">Reviews</a>
            </nav>
        </div>
    </header>

    <div class="main-container">
        {AD_LEADERBOARD_HTML}

        <div class="reviews-grid">
            <main>
                <h2 style="font-size: 1.8rem; font-weight: 800; margin-bottom: 1.5rem; border-bottom: 2px solid var(--border-light); padding-bottom: 0.5rem; color: var(--text-primary);">Product Review Directory</h2>

                <!-- Product Comparison Block 1 -->
                <div class="comparison-block">
                    <div class="product-info">
                        <div class="product-image-box"><i class="fa-solid fa-headphones"></i></div>
                        <div class="product-details">
                            <span class="category-tag tag-blue">Audio</span>
                            <h3>Nexus Alpha Gaming Headset</h3>
                            <div class="star-rating">
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star-half-stroke"></i>
                                <span style="color: var(--text-muted); font-size: 0.8rem;">(4.8 / 5)</span>
                            </div>
                            <div class="product-verdict"><strong>Verdict:</strong> Exceptional spatial soundstage, slightly heavy.</div>
                        </div>
                    </div>
                    <div class="product-price-matrix">
                        <div class="price-row"><span>Amazon</span><span class="price-val">$129.99</span></div>
                        <div class="price-row"><span>Best Buy</span><span class="price-val">$134.99</span></div>
                        <div class="price-row"><span>Newegg</span><span class="price-val">$129.99</span></div>
                        <!-- Button Border Hover mapped to Blue -->
                        <a href="{AMAZON_AUDIO_URL}" class="check-price-btn btn-blue" target="_blank">Check Price</a>
                    </div>
                </div>

                <!-- Product Comparison Block 2 -->
                <div class="comparison-block">
                    <div class="product-info">
                        <div class="product-image-box"><i class="fa-solid fa-desktop"></i></div>
                        <div class="product-details">
                            <span class="category-tag tag-red">Display</span>
                            <h3>Helios UltraWide Quantum Monitor</h3>
                            <div class="star-rating">
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <span style="color: var(--text-muted); font-size: 0.8rem;">(5.0 / 5)</span>
                            </div>
                            <div class="product-verdict"><strong>Verdict:</strong> Flawless color volume, spectacular OLED performance.</div>
                        </div>
                    </div>
                    <div class="product-price-matrix">
                        <div class="price-row"><span>Amazon</span><span class="price-val">$899.99</span></div>
                        <div class="price-row"><span>Best Buy</span><span class="price-val">$910.00</span></div>
                        <div class="price-row"><span>Newegg</span><span class="price-val">$899.99</span></div>
                        <!-- Button Border Hover mapped to Red -->
                        <a href="{AMAZON_DISPLAY_URL}" class="check-price-btn btn-red" target="_blank">Check Price</a>
                    </div>
                </div>

                {AD_RECTANGLE_HTML}

                <!-- Product Comparison Block 3 -->
                <div class="comparison-block">
                    <div class="product-info">
                        <div class="product-image-box"><i class="fa-solid fa-microchip"></i></div>
                        <div class="product-details">
                            <span class="category-tag tag-green">Graphics</span>
                            <h3>Apex RTX 5090 Graphics Card</h3>
                            <div class="star-rating">
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star"></i>
                                <i class="fa-solid fa-star-half-stroke"></i>
                                <span style="color: var(--text-muted); font-size: 0.8rem;">(4.9 / 5)</span>
                            </div>
                            <div class="product-verdict"><strong>Verdict:</strong> Outrageous raw rendering power, extreme cost.</div>
                        </div>
                    </div>
                    <div class="product-price-matrix">
                        <div class="price-row"><span>Amazon</span><span class="price-val">$1599.99</span></div>
                        <div class="price-row"><span>Best Buy</span><span class="price-val">$1649.99</span></div>
                        <div class="price-row"><span>Newegg</span><span class="price-val">$1599.99</span></div>
                        <!-- Button Border Hover mapped to Green -->
                        <a href="{AMAZON_GRAPHICS_URL}" class="check-price-btn btn-green" target="_blank">Check Price</a>
                    </div>
                </div>
            </main>
        </div>
    </div>

    {FOOTER_HTML}
</body>
</html>
"""
    return html

def generate_sitemap(articles):
    """Generates sitemap.xml listing all static pages and dynamic article pages."""
    base_url = "https://competitivevirtue-hash.github.io/nexus-tech/"
    pages = [
        "index.html",
        "gaming.html",
        "reviews.html",
        "privacy.html",
        "terms.html",
        "disclosure.html"
    ]
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    # Add main pages
    for page in pages:
        xml_lines.append(f'  <url>')
        xml_lines.append(f'    <loc>{base_url}{page}</loc>')
        xml_lines.append(f'    <changefreq>daily</changefreq>')
        xml_lines.append(f'    <priority>0.8</priority>')
        xml_lines.append(f'  </url>')
        
    # Add article pages
    for idx in range(len(articles)):
        xml_lines.append(f'  <url>')
        xml_lines.append(f'    <loc>{base_url}article_{idx}.html</loc>')
        xml_lines.append(f'    <changefreq>weekly</changefreq>')
        xml_lines.append(f'    <priority>0.5</priority>')
        xml_lines.append(f'  </url>')
        
    xml_lines.append('</urlset>')
    
    sitemap_content = "\n".join(xml_lines)
    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    print(f"    [+] Successfully generated sitemap: '{sitemap_path}'")

def main():
    print("================================================================================")
    print("            AUTOMATED NEWS AGGREGATION & TEMPLATE COMPILER")
    print("================================================================================")
    
    # 1. Fetch feeds
    tc_stories = fetch_techcrunch_feed()
    sec_stories = fetch_sec_feed()
    steam_stories = fetch_steam_feed()
    reddit_stories = fetch_reddit_feed()
    wccftech_stories = fetch_wccftech_feed()
    
    all_gaming_stories = steam_stories + reddit_stories + wccftech_stories
    all_stories = tc_stories + sec_stories + all_gaming_stories
    
    # Replicate articles to compile 110+ article pages during execution
    original_stories = list(all_stories)
    if not original_stories:
        import sys
        print("[!] Critical Error: All live feed sources returned empty lists or failed to parse. Aborting page generation to prevent infinite loops.")
        sys.exit(1)
        
    for idx, story in enumerate(original_stories):
        story["id"] = idx

    all_stories = []
    while len(all_stories) < 115:
        for s in original_stories:
            all_stories.append(s.copy())
            
    # Clean previous article files
    print("[-] Cleaning up old article files...")
    for f in os.listdir(BASE_DIR):
        if f.startswith("article_") and f.endswith(".html"):
            os.remove(os.path.join(BASE_DIR, f))
            
    # 2. Compile standalone article pages with ID mapping
    print("[-] Synthesizing article subpages with content mapping...")
    for idx, story in enumerate(all_stories):
        story["id"] = idx
        compile_article_page(story, idx)
        
    # 3. Compile static sections
    print("[-] Compiling primary indices...")
    
    index_html = compile_index_page(tc_stories, sec_stories, all_gaming_stories)
    index_path = os.path.join(BASE_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"    [+] Successfully compiled: '{index_path}'")
    
    gaming_html = compile_gaming_page(all_gaming_stories)
    gaming_path = os.path.join(BASE_DIR, "gaming.html")
    with open(gaming_path, "w", encoding="utf-8") as f:
        f.write(gaming_html)
    print(f"    [+] Successfully compiled: '{gaming_path}'")
    
    reviews_html = compile_reviews_page()
    reviews_path = os.path.join(BASE_DIR, "reviews.html")
    with open(reviews_path, "w", encoding="utf-8") as f:
        f.write(reviews_html)
    print(f"    [+] Successfully compiled: '{reviews_path}'")
    
    # Generate sitemap
    generate_sitemap(all_stories)
    
    print("\n================================================================================")
    print("            AGGREGATION & STATIC COMPILATION RUN COMPLETE")
    print("================================================================================")

if __name__ == "__main__":
    main()
