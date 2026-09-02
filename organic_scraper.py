import sqlite3
import pandas as pd
import time
import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_PROFILE_DIR = os.path.join(BASE_DIR, "bot_profile")
DB_NAME = os.path.join(BASE_DIR, "ad_tracker.db")
OUTPUT_CSV = os.path.join(BASE_DIR, "organic_data.csv")

FB_TARGETS = [
    {"brand": "AnAnA Computer", "url": "https://www.facebook.com/ananacomputer"},
    {"brand": "PTC Computer", "url": "https://www.facebook.com/PTCcomputerkh"},
    {"brand": "ICE Electronics", "url": "https://www.facebook.com/ICEElectronics"},
    {"brand": "ECI Distribution", "url": "https://www.facebook.com/ecidisti"},
    {"brand": "BCS Computer", "url": "https://www.facebook.com/Bcscomputer168"},
    {"brand": "Kim Heng Center", "url": "https://www.facebook.com/kimhengctTrading"},
    {"brand": "ICT Distribution", "url": "https://www.facebook.com/ICTDistributionKH"},
    {"brand": "Root IT", "url": "https://www.facebook.com/rootitsupport"},
    {"brand": "PSC Computer", "url": "https://www.facebook.com/visit.psc"},
    {"brand": "IQ Distributor", "url": "https://www.facebook.com/IQDistribution"}
]

def init_organic_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS organic_posts_history (
            post_id TEXT PRIMARY KEY,
            brand TEXT,
            platform TEXT,
            timestamp TEXT,
            caption_text TEXT,
            media_type TEXT,
            media_url TEXT,
            reactions INTEGER,
            comments INTEGER,
            shares INTEGER,
            post_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def clean_organic_caption(text):
    text = text.replace('\u200b', '').replace('\ufeff', '')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    ignore_tokens = ["like", "comment", "share", "write a comment", "most relevant", "view more comments", "all comments", "see translation"]
    filtered = [l for l in lines if not any(t == l.lower() for t in ignore_tokens) and len(l) > 3]
    return " ".join(filtered)[:600] if filtered else "Hardware Specification Post"

def scrape_facebook_organic():
    records = []
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    if not os.path.exists(BOT_PROFILE_DIR):
        print(f"❌ Error: {BOT_PROFILE_DIR} not found. Run bot setup first.")
        return []

    print("\n🌐 Initiating Facebook Organic Scraper (Hardware Spec Focus)...")
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=BOT_PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={'width': 1366, 'height': 900}
        )
        page = context.pages[0] if context.pages else context.new_page()

        for fb in FB_TARGETS:
            brand = fb["brand"]
            print(f"   ↳ Scanning Timeline: {brand}...")
            
            try:
                page.goto(fb["url"], wait_until="commit", timeout=30000)
            except Exception:
                print(f"     ⚠️ Navigation timeout for {brand}, parsing loaded nodes...")
            
            time.sleep(4)
            
            try:
                close_btn = page.locator("div[aria-label='Close']").or_(page.locator("text=Allow all cookies"))
                if close_btn.first.is_visible(timeout=2000):
                    close_btn.first.click()
            except Exception:
                pass
            
            for _ in range(3):
                page.mouse.wheel(0, 1500)
                time.sleep(1.5)
            
            # In-Browser JavaScript DOM Extractor
            posts_extracted = page.evaluate("""() => {
                const results = [];
                const seenCaptions = new Set();
                
                // 1. Identify valid post wrappers
                let cards = Array.from(document.querySelectorAll('div.x1yztbdb, div[role="article"]'));
                if (cards.length === 0) {
                    cards = Array.from(document.querySelectorAll('div[data-pagelet^="ProfileTimeline"] > div > div'));
                }
                
                for (const card of cards) {
                    if (results.length >= 5) break;
                    
                    // --- CAPTION EXTRACTION ---
                    const textDivs = Array.from(card.querySelectorAll('div[dir="auto"][style*="text-align: start"]'));
                    let caption = '';
                    for (let div of textDivs) {
                        let txt = div.innerText.trim();
                        if (txt.length > 10 && !txt.includes('View more comments') && !txt.includes('Write a comment')) {
                            caption = txt;
                            break; 
                        }
                    }
                    if (!caption || caption.length < 15 || seenCaptions.has(caption)) continue;
                    seenCaptions.add(caption);
                    
                    // --- IMAGE EXTRACTION ---
                    let mediaUrl = '';
                    let mediaType = 'Photo Post';
                    
                    // Direct hit using Facebook's specific feed image attribute
                    const feedImage = card.querySelector('img[data-imgperflogname="feedImage"]');
                    if (feedImage && feedImage.src) {
                        mediaUrl = feedImage.src;
                    }
                    
                    // Fallback for Video Reels
                    if (!mediaUrl) {
                        const video = card.querySelector('video');
                        if (video) {
                            mediaUrl = video.poster || video.getAttribute('src');
                            mediaType = 'Video Reel';
                        }
                    }
                    
                    // Ultimate Fallback (Look for large scontent images)
                    if (!mediaUrl) {
                        const imgs = Array.from(card.querySelectorAll('img'));
                        for (const img of imgs) {
                            const src = img.src || img.getAttribute('src') || '';
                            if (src.includes('scontent') && !src.includes('emoji') && !src.includes('/p50x50/')) {
                                const h = img.getAttribute('height') || 0;
                                if (h > 100 || !h) {
                                    mediaUrl = src;
                                    break;
                                }
                            }
                        }
                    }
                    
                    results.push({
                        caption: caption.substring(0, 400),
                        media_url: mediaUrl || '',
                        media_type: mediaType
                    });
                }
                return results;
            }""")

            found_count = 0
            for item in posts_extracted:
                post_id = f"fb_{brand.replace(' ', '_')}_{int(time.time())}_{found_count}"
                records.append({
                    "post_id": post_id,
                    "brand": brand,
                    "platform": "Facebook",
                    "timestamp": timestamp_str,
                    "caption_text": item["caption"],
                    "media_type": item["media_type"],
                    "media_url": item["media_url"],  # Fixed: Dynamically maps the extracted URL
                    "reactions": 0,
                    "comments": 0,
                    "shares": 0,
                    "post_url": fb["url"]
                })
                found_count += 1

            print(f"     ↳ Captured {found_count} posts for {brand}.")

        context.close()
    return records

if __name__ == "__main__":
    init_organic_db()
    scraped_posts = scrape_facebook_organic()
    
    if scraped_posts:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        for r in scraped_posts:
            c.execute('''
                INSERT OR REPLACE INTO organic_posts_history VALUES (
                    :post_id, :brand, :platform, :timestamp, :caption_text,
                    :media_type, :media_url, :reactions, :comments, :shares, :post_url
                )
            ''', r)
        conn.commit()
        
        df = pd.read_sql_query("SELECT * FROM organic_posts_history ORDER BY timestamp DESC", conn)
        df.to_csv(OUTPUT_CSV, index=False)
        conn.close()
        print(f"\n✅ Pipeline Complete! Successfully wrote {len(df)} records to {OUTPUT_CSV}.")
    else:
        print("\n⚠️ No organic posts captured.")