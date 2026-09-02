import re
from datetime import datetime, timedelta
import pandas as pd
from playwright.sync_api import sync_playwright

# Tracked IT Competitor Pages in Phnom Penh
COMPETITORS = [
    {"brand": "AnAnA Computer", "page_id": "296930736995334", "is_self": True},
    {"brand": "PTC Computer", "page_id": "137830336353637", "is_self": False},
    {"brand": "ICE Electronics", "page_id": "144749988927232", "is_self": False},
    {"brand": "ECI Distribution", "page_id": "282049375491253", "is_self": False},
    {"brand": "BCS Computer", "page_id": "1398887223669216", "is_self": False},
    {"brand": "Kim Heng Center", "page_id": "571154319650596", "is_self": False},
    {"brand": "ICT Distribution", "page_id": "646103285256164", "is_self": False},
    {"brand": "Root IT", "page_id": "300873193306593", "is_self": False},
    {"brand": "PSC Computer", "page_id": "100386573392063", "is_self": False},
    {"brand": "IQ Distributor", "page_id": "1470204603230594", "is_self": False}
]

def extract_pricing_tiers(text):
    """
    Categorizes extracted price points into Installments, Rebates, and MSRPs.
    """
    pricing = {
        "installment": None,
        "discount_rebate": None,
        "msrp": None
    }
    # 1. Installment Matching ($XX/month, $XX/mo, $X/day)
    installment_match = re.search(r'(\$\s*\d+(?:\.\d{1,2})?\s*(?:/|\s*per\s*)?(?:month|mo|day|ខែ))', text, re.I)
    if installment_match:
        pricing["installment"] = installment_match.group(1).strip()

    # 2. Discount / Rebate Matching (Save $XX, Discount $XX, ចំណេញ XX $)
    rebate_match = re.search(r'(?:discount|save|ចំណេញ|ចុះតម្លៃ)\s*[:\$]?\s*(\d+)\s*\$?', text, re.I)
    if rebate_match:
        pricing["discount_rebate"] = f"${rebate_match.group(1)}"

    # 3. Direct MSRP ($XXX, $X,XXX)
    msrp_matches = re.findall(r'\$\s*([0-9]{2,4}(?:,[0-9]{3})?)', text)
    if msrp_matches:
        # Take the largest dollar amount found as the likely product MSRP
        cleaned_prices = [int(p.replace(',', '')) for p in msrp_matches]
        pricing["msrp"] = f"${max(cleaned_prices):,}"

    return pricing

def classify_hardware_segment(text):
    """
    Classifies the hardware target: B2B Enterprise, Gaming, or Office/Commercial.
    """
    text_lower = text.lower()
    
    b2b_keywords = ['mikrotik', 'ruijie', 'reyee', 'ubiquiti', 'cisco', 'server', 'poweredge', 'switch', 'router', 'synology', 'nas', 'latitude', 'vostro', 'expertbook']
    gaming_keywords = ['rtx', 'rog', 'tuf', 'legion', 'zephyrus', 'gaming', 'strix', 'predator', 'victus', 'loq', 'radeon', 'geforce', 'fps']
    
    if any(k in text_lower for k in b2b_keywords):
        return "B2B / Network Infrastructure"
    elif any(k in text_lower for k in gaming_keywords):
        return "Gaming Rig & Hardware"
    else:
        return "Commercial / Student Laptop"

def extract_leadgen_funnel(text):
    """
    Extracts Telegram Sales Channels and Messenger hooks from copy.
    """
    tg_match = re.findall(r'(https?://t\.me/[a-zA-Z0-9_+]+)', text)
    return ", ".join(list(set(tg_match))) if tg_match else "Messenger Direct"

def parse_start_date(card_text):
    today = datetime.now()
    match = re.search(r"Started running on\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4})", card_text, re.IGNORECASE)
    if match:
        date_str = match.group(1).replace(",", "")
        for fmt in ("%b %d %Y", "%d %b %Y", "%B %d %Y", "%d %B %Y"):
            try:
                start_dt = datetime.strptime(date_str, fmt)
                days_diff = (today - start_dt).days
                return start_dt.strftime('%Y-%m-%d'), max(1, days_diff)
            except ValueError:
                continue
    return today.strftime('%Y-%m-%d'), 1

def run_scraper():
    scraped_data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1366, 'height': 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for comp in COMPETITORS:
            brand = comp["brand"]
            page_id = comp["page_id"]
            url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=KH&view_all_page_id={page_id}&search_type=page&media_type=all"
            
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)

            # Scroll dynamically
            for _ in range(3):
                page.mouse.wheel(0, 2500)
                page.wait_for_timeout(1500)

            cards = page.locator("div").filter(has_text="Library ID:").all()
            seen_ids = set()

            for card in cards:
                try:
                    card_text = card.inner_text()
                    if len(card_text) < 40:
                        continue

                    match_id = re.search(r"Library ID:\s*(\d+)", card_text)
                    if not match_id:
                        continue

                    ad_id = match_id.group(1)
                    if ad_id in seen_ids:
                        continue
                    seen_ids.add(ad_id)

                    launch_date_str, days_active = parse_start_date(card_text)
                    pricing = extract_pricing_tiers(card_text)
                    segment = classify_hardware_segment(card_text)
                    leadgen_channel = extract_leadgen_funnel(card_text)

                    # Determine creative media
                    media_url = "https://via.placeholder.com/500x500?text=No+Creative+Image"
                    video = card.locator("video").first
                    if video.is_visible():
                        poster = video.get_attribute("poster")
                        if poster:
                            media_url = poster
                    else:
                        images = card.locator("img").all()
                        for img in images:
                            box = img.bounding_box()
                            src = img.get_attribute("src")
                            if box and box["width"] > 140 and box["height"] > 100 and src:
                                media_url = src
                                break

                    lines = [l.strip() for l in card_text.split('\n') if l.strip()]
                    headline = lines[0][:60] + "..." if lines else "Active Promotion"
                    body = " ".join(lines[1:8])[:250] + "..." if len(lines) > 1 else card_text[:150]

                    cta = "Send Message"
                    for c_cta in ["Send Message", "Shop Now", "Learn More", "Contact Us", "Call Now"]:
                        if c_cta.lower() in card_text.lower():
                            cta = c_cta
                            break

                    scraped_data.append({
                        "id": ad_id,
                        "brand": brand,
                        "is_self": comp["is_self"],
                        "launch_date": launch_date_str,
                        "days_active": days_active,
                        "product_cat": segment,
                        "theme": "Enterprise Push" if "B2B" in segment else "Consumer Retail",
                        "headline": headline,
                        "body": body,
                        "cta": cta,
                        "msrp": pricing["msrp"] or "N/A",
                        "rebate": pricing["discount_rebate"] or "N/A",
                        "installment": pricing["installment"] or "N/A",
                        "funnel_channel": leadgen_channel,
                        "offer_tag": f"Active {days_active}d",
                        "media_type": "Video Reel" if video.is_visible() else "Static Image",
                        "media_url": media_url,
                        "link": f"https://www.facebook.com/ads/library/?id={ad_id}"
                    })
                except Exception:
                    continue

        browser.close()

    df = pd.DataFrame(scraped_data)
    df.to_csv('ads_data.csv', index=False)
    print(f"Extraction complete: {len(df)} ads structured and written to ads_data.csv.")

if __name__ == "__main__":
    run_scraper()