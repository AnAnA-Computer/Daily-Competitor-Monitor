import requests
import sqlite3
import datetime

# --- YOUR MASTER KEY ---
ACCESS_TOKEN = 'EAGQ8Th1UYU4BSUIdg6rvE3dv5QCiiAL4Wb2rCcN1FORDAP2uRZAfzaQdhXz4xQmCqaa2rJoUymasdWMmW0VXIgBSCOEB1wmzNuvZAZAgU5uixYeZCYlF8b7PHBnAnDJr8I73uFE4LLOvZAhZAN5hP64UcxODCzmyWsx1lXQaB5sBMyoymhmkap8sPOVLN6o9ds'

# Connect to database (or create it)
conn = sqlite3.connect('ad_tracker.db')
c = conn.cursor()

# Create tables for Competitors and Ads
c.execute('''CREATE TABLE IF NOT EXISTS competitors (page_id TEXT PRIMARY KEY, page_name TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS ads 
             (ad_id TEXT PRIMARY KEY, page_name TEXT, date_found TEXT, copy TEXT, link TEXT)''')
conn.commit()

def fetch_ads(page_id):
    # Using the latest v25.0 API
    url = "https://graph.facebook.com/v25.0/ads_archive"
    params = {
        "access_token": ACCESS_TOKEN,
        "search_page_ids": page_id,
        "ad_type": "ALL",  # <--- NEW: Required by Meta for commercial ads
        "ad_reached_countries": "['KH', 'US']", 
        "ad_active_status": "ACTIVE",
        "fields": "id,page_name,ad_creation_time,ad_creative_bodies,ad_snapshot_url",
        "limit": 50
    }
    
    response = requests.get(url, params=params)
    
    # NEW: Print the exact error if Meta rejects the request
    if response.status_code != 200:
        print(f"❌ API Error for {page_id}: {response.text}")
        return []
        
    return response.json().get('data', [])

def run_monitor():
    # Get competitors from the database
    c.execute("SELECT page_id FROM competitors")
    competitors = [row[0] for row in c.fetchall()]
    
    if not competitors:
        print("No competitors in database. Add some via the dashboard first!")
        return

    new_ads_count = 0
    for page_id in competitors:
        print(f"Scanning {page_id}...")
        ads = fetch_ads(page_id)
        
        for ad in ads:
            ad_id = ad['id']
            c.execute("SELECT ad_id FROM ads WHERE ad_id=?", (ad_id,))
            
            if not c.fetchone(): # If ad is new
                copy_text = ad.get('ad_creative_bodies', [''])[0] if ad.get('ad_creative_bodies') else "No text"
                link = ad.get('ad_snapshot_url', '')
                page_name = ad.get('page_name', 'Unknown Page')
                
                c.execute("INSERT INTO ads (ad_id, page_name, date_found, copy, link) VALUES (?, ?, ?, ?, ?)", 
                          (ad_id, page_name, str(datetime.date.today()), copy_text, link))
                new_ads_count += 1
                
    conn.commit()
    print(f"Scan complete. {new_ads_count} new ads added to the dashboard.")

if __name__ == "__main__":
    run_monitor()