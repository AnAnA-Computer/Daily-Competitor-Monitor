import os
import time
from playwright.sync_api import sync_playwright

BOT_PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_profile")

def init_bot_profile():
    print(f"🚀 Initializing Bot Profile in: {BOT_PROFILE_DIR}")
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=BOT_PROFILE_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={'width': 1280, 'height': 800}
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.facebook.com/login")
        
        print("\n" + "="*60)
        print("👉 1. Log into your burner Facebook account in the browser.")
        print("👉 2. Complete any 2FA/checkpoints and wait for the feed to load.")
        print("👉 3. Return here and press ENTER to finalize session storage.")
        print("="*60 + "\n")
        
        input("Press [ENTER] after logging in successfully: ")
        context.close()
        print("✅ Bot profile configured successfully! You can now run scraper.py.")

if __name__ == "__main__":
    init_bot_profile()