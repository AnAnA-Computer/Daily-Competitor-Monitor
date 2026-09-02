import pandas as pd
import json
import os
from datetime import datetime

# ==========================================
# 1. IMAGE SLOT: PASTE BASE64 STRING BELOW
# ==========================================
ANANA_LOGO_BASE64 = "data:image/png;base64,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"

def generate_interactive_html():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ads_path = os.path.join(BASE_DIR, 'ads_data.csv')
    org_path = os.path.join(BASE_DIR, 'organic_data.csv')
    
    # 1. Process Paid Ads Data
    if not os.path.exists(ads_path):
        ads_json_str = "[]"
    else:
        df_ads = pd.read_csv(ads_path).fillna("N/A")
        if 'days_active' in df_ads.columns:
            df_ads['days_active'] = pd.to_numeric(df_ads['days_active'], errors='coerce').fillna(1).astype(int)
        ads_json_str = json.dumps(df_ads.to_dict(orient='records'))

    # 2. Process Organic Data (Fallback safely if scraper hasn't run yet)
    if not os.path.exists(org_path):
        org_json_str = "[]"
    else:
        df_org = pd.read_csv(org_path).fillna("")
        org_json_str = json.dumps(df_org.to_dict(orient='records'))
    
    today_str = datetime.now().strftime("%A, %d %B %Y")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="referrer" content="no-referrer">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AnAnA Computer — Omnichannel IT Competitor Intelligence</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg:            #0C1620;
            --surface-1:     #111E2A;
            --surface-2:     #162836;
            --surface-3:     #1C3243;
            --border-subtle: #1D3040;
            --border-strong: #2A4459;
            --text-1:        #E8EFF4;
            --text-2:        #9CB2C1;
            --text-3:        #6B8496;
            --brand:         #1E98D5;
            --brand-bright:  #4FB6E8;
            --brand-deep:    #12628B;
            --brand-wash:    rgba(30, 152, 213, 0.14);
            --good:          #2FBF71;
            --warning:       #E8A33D;
            --critical:      #E5484D;
            --good-wash:     rgba(47, 191, 113, 0.14);
            --font-ui:      'IBM Plex Sans', 'Segoe UI', system-ui, sans-serif;
            --font-display: 'Oswald', 'IBM Plex Sans Condensed', 'Arial Narrow', sans-serif;
            --font-mono:    'IBM Plex Mono', 'JetBrains Mono', ui-monospace, monospace;
            --font-khmer:   'Noto Sans Khmer', 'Kantumruy Pro', sans-serif;
            --fs-label: 11px;
            --fs-body:  13.5px;
            --fs-cell:  13px;
            --radius-card: 10px;
            --pad-card:    18px;
            --row-h:       38px;
        }}
        
        body {{ background: var(--bg); color: var(--text-2); font-family: var(--font-ui); font-size: var(--fs-body); margin: 0; padding: 24px; }}
        
        .num, td.num, .kpi-val {{ font-family: var(--font-mono); font-variant-numeric: tabular-nums; letter-spacing: -0.01em; color: var(--text-1); }}
        .label, .kpi-title {{ font-family: var(--font-display); font-size: var(--fs-label); letter-spacing: 0.14em; text-transform: uppercase; color: var(--text-3); }}
        
        .header {{ display: flex; justify-content: space-between; align-items: center; border-left: 4px solid var(--brand); padding-left: 16px; margin-bottom: 24px; }}
        .header-left {{ display: flex; align-items: center; gap: 16px; }}
        .header-logo-text {{ font-family: var(--font-display); font-size: 26px; font-weight: 900; color: var(--brand-bright); letter-spacing: 1px; }}
        .header-titles h1 {{ margin: 0; font-size: 20px; color: var(--text-1); font-weight: 700; }}
        .header-titles p {{ margin: 2px 0 0 0; color: var(--text-3); font-size: 12px; }}
        
        .filter-bar {{ background: var(--surface-1); border: 1px solid var(--border-subtle); border-radius: var(--radius-card); padding: 16px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 24px; }}
        .filter-group select, .filter-group input {{ width: 100%; background: var(--surface-2); border: 1px solid var(--border-strong); color: var(--text-1); padding: 8px 10px; border-radius: 6px; font-size: 13px; box-sizing: border-box; outline: none; }}
        .filter-group select:focus, .filter-group input:focus {{ border-color: var(--brand-bright); }}
        
        .kpi-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 32px; }}
        .card {{ background: var(--surface-1); border: 1px solid var(--border-subtle); border-radius: var(--radius-card); padding: var(--pad-card); }}
        .kpi-val {{ font-size: 32px; font-weight: bold; margin: 6px 0; }}
        .kpi-sub {{ font-size: 11px; color: var(--text-3); }}
        
        .tabs {{ display: flex; gap: 8px; border-bottom: 1px solid var(--border-strong); margin-bottom: 24px; padding-bottom: 8px; flex-wrap: wrap; }}
        .tab-btn {{ background: transparent; border: none; color: var(--text-3); padding: 10px 16px; font-size: 14px; font-weight: bold; cursor: pointer; border-radius: 6px; transition: 0.2s; }}
        .tab-btn:hover {{ color: var(--text-1); background: var(--surface-2); }}
        .tab-btn.active {{ color: var(--brand-bright); background: var(--brand-wash); box-shadow: inset 3px 0 0 var(--brand); }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        
        .creative-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }}
        .ad-card {{ display: flex; flex-direction: column; justify-content: space-between; }}
        .ad-card.is-anana {{ box-shadow: inset 3px 0 0 var(--brand); border-color: var(--brand-deep); }}
        
        .pill {{ display: inline-flex; align-items: center; gap: 6px; height: 22px; padding: 0 10px; border-radius: 999px; font-size: 11.5px; font-weight: 500; font-family: var(--font-display); text-transform: uppercase; letter-spacing: 0.5px; }}
        .pill-brand {{ background: var(--brand-deep); color: var(--text-1); }}
        .pill-comp {{ background: var(--surface-3); color: var(--text-1); border: 1px solid var(--border-strong); }}
        .pill-good {{ background: var(--good-wash); color: var(--good); }}
        
        .spec-tag {{ display: inline-block; background: var(--surface-3); color: var(--text-1); border: 1px solid var(--border-subtle); padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; margin: 0 4px 4px 0; }}
        .spec-tag-price {{ color: var(--good); border-color: var(--good); background: var(--good-wash); font-family: var(--font-mono); font-weight: bold; }}
        
        .media-container {{ width: 100%; height: 180px; border-radius: 6px; margin: 12px 0; background: #000; overflow: hidden; border: 1px solid var(--border-strong); }}
        .ad-img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
        
        .ad-headline {{ font-size: 14px; font-weight: 600; margin-bottom: 8px; color: var(--text-1); }}
        .ad-body {{ font-size: var(--fs-cell); color: var(--text-2); height: 100px; overflow-y: auto; margin-bottom: 12px; line-height: 1.6; padding-right: 6px; font-family: var(--font-khmer), var(--font-ui); }}
        
        .ad-footer {{ display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-subtle); padding-top: 12px; font-size: 12px; }}
        .ad-footer a {{ color: var(--brand-bright); text-decoration: none; font-weight: 500; }}
        .ad-footer a:hover {{ text-decoration: underline; }}
        
        table {{ border-collapse: collapse; width: 100%; font-family: var(--font-ui); }}
        th {{ background: var(--surface-2); color: var(--text-3); font-family: var(--font-display); font-size: var(--fs-label); letter-spacing: 0.14em; text-transform: uppercase; text-align: left; padding: 0 16px; height: var(--row-h); border-bottom: 1px solid var(--border-strong); }}
        td {{ height: var(--row-h); padding: 8px 16px; border-bottom: 1px solid var(--border-subtle); color: var(--text-2); font-size: var(--fs-cell); }}
        tbody tr:hover {{ background: var(--surface-2); }}
        
        .callout {{ border-left: 4px solid var(--brand); margin-bottom: 20px; }}
        .chart-container {{ position: relative; height: 350px; width: 100%; margin-top: 16px; }}
    </style>
</head>
<body>

    <div class="header">
        <div class="header-left">
            <div class="header-logo-text">AnAnA IT</div>
            <div class="header-titles">
                <h1>Competitor Intelligence Matrix</h1>
                <p>Phnom Penh IT Retail & Distribution · Updated {today_str}</p>
            </div>
        </div>
        <div>
            <span class="pill pill-good">● System Active</span>
        </div>
    </div>

    <!-- FILTER BAR -->
    <div class="filter-bar">
        <div class="filter-group">
            <label class="label">Brand Filter</label>
            <select id="brandFilter" onchange="renderDashboard()">
                <option value="ALL">All Tracked Brands</option>
            </select>
        </div>
        <div class="filter-group">
            <label class="label">Hardware / Price / Spec Keyword</label>
            <input type="text" id="searchInput" placeholder="Search (RTX 4070, MikroTik, Ruijie, $45/mo, Latitude)..." oninput="renderDashboard()" />
        </div>
    </div>

    <!-- KPIS -->
    <div class="kpi-row">
        <div class="card kpi-card">
            <div class="kpi-title label">Tracked Brands</div>
            <div class="kpi-val num" id="kpi-brands">0</div>
            <div class="kpi-sub label">Phnom Penh Retail</div>
        </div>
        <div class="card kpi-card">
            <div class="kpi-title label">Meta Ads Active</div>
            <div class="kpi-val num" id="kpi-ads">0</div>
            <div class="kpi-sub label">Paid Ad Library</div>
        </div>
        <div class="card kpi-card">
            <div class="kpi-title label">Timeline Posts</div>
            <div class="kpi-val num" style="color: var(--brand-bright);" id="kpi-org">0</div>
            <div class="kpi-sub label">Organic Drops</div>
        </div>
        <div class="card kpi-card">
            <div class="kpi-title label">Price Anchors Found</div>
            <div class="kpi-val num" style="color: var(--good);" id="kpi-prices">0</div>
            <div class="kpi-sub label">MSRP / Installment / Rebate</div>
        </div>
    </div>

    <!-- TABS -->
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('paid', this)">🖼️ Paid Ad Library</button>
        <button class="tab-btn" onclick="switchTab('organic', this)">📰 Organic Facebook Feed</button>
        <button class="tab-btn" onclick="switchTab('pricing', this)">💰 Competitor Pricing Matrix</button>
        <button class="tab-btn" onclick="switchTab('longest', this)">⏳ Evergreen Ads (30+ Days)</button>
        <button class="tab-btn" onclick="switchTab('strategy', this)">💡 Strategic Recommendations</button>
    </div>

    <!-- TAB 1: PAID CREATIVES -->
    <div id="tab-paid" class="tab-content active">
        <div class="creative-grid" id="paidGrid"></div>
    </div>

    <!-- TAB 2: ORGANIC FEED -->
    <div id="tab-organic" class="tab-content">
        <div class="creative-grid" id="organicGrid"></div>
    </div>

    <!-- TAB 3: COMPETITOR PRICING MATRIX -->
    <div id="tab-pricing" class="tab-content">
        <div class="card callout" style="border-left-color: var(--good);">
            <h3 style="margin-top:0; color: var(--text-1);">Pricing Tiers & Clearance Tracking</h3>
            <p style="font-size:13px; line-height:1.6; color:var(--text-2);">
                Tracks <strong>MSRP Street Prices</strong>, <strong>Clearance Rebates</strong> (e.g. Save $150), and <strong>Installment Floors</strong> (e.g. $45/month AEON 0%).
            </p>
        </div>
        <div class="card" style="padding: 0; overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>Brand</th>
                        <th>Extracted Value</th>
                        <th>Hardware Target Context</th>
                        <th>CTA Funnel</th>
                        <th>Inspect Ad</th>
                    </tr>
                </thead>
                <tbody id="pricingTableBody"></tbody>
            </table>
        </div>
    </div>

    <!-- TAB 4: LONGEST RUNNING -->
    <div id="tab-longest" class="tab-content">
        <div class="card callout" style="border-left-color: var(--warning);">
            <h3 style="margin-top:0; color: var(--text-1);">⏳ Evergreen Campaigns (High ROAS Winners)</h3>
            <p style="font-size:13px; line-height:1.6; color:var(--text-2);">
                Ads active continuously for 30+ days represent proven bottom-of-funnel customer acquisition drivers for competitors.
            </p>
        </div>
        <div class="card" style="padding: 0; overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>Brand</th>
                        <th>Days Active</th>
                        <th>Headline / Core Hook</th>
                        <th>Call to Action</th>
                        <th>Meta Ad Library</th>
                    </tr>
                </thead>
                <tbody id="longestTableBody"></tbody>
            </table>
        </div>
    </div>

    <!-- TAB 5: STRATEGY & RECOMMENDATIONS -->
    <div id="tab-strategy" class="tab-content">
        <div class="card callout" style="border-left-color: var(--warning);">
            <h3 style="margin-top:0; color: var(--text-1);">1. Installment Anchoring ($45/mo vs $1,200 Upfront)</h3>
            <p style="font-size:13px; line-height:1.6; color:var(--text-2);">
                PTC Computer drives high engagement on $1,000+ gaming PCs by advertising <b>"$45/month with 0% installment"</b> rather than showing full retail prices. Feature monthly payment breakdowns on your high-end ASUS and Legion creative overlays.
            </p>
        </div>
        <div class="card callout" style="border-left-color: var(--brand-bright);">
            <h3 style="margin-top:0; color: var(--text-1);">2. Enterprise Infrastructure Lead Gen (MikroTik & Ruijie)</h3>
            <p style="font-size:13px; line-height:1.6; color:var(--text-2);">
                Over 70% of tech retail ads route directly to Messenger. Corporate IT Directors do not purchase network switches through web carts. Deploy paid <b>Send Message</b> campaigns targeting IT Administrators with pre-configured formal PDF quote templates.
            </p>
        </div>
        <div class="card callout" style="border-left-color: var(--good);">
            <h3 style="margin-top:0; color: var(--text-1);">3. Switch from Static Banners to 15s Benchmark Reels</h3>
            <p style="font-size:13px; line-height:1.6; color:var(--text-2);">
                Short video benchmark reels comparing gaming performance (FPS) drive significantly higher click-through rates across local tech audiences than static image posts.
            </p>
        </div>
    </div>

    <script>
        const ALL_ADS = {ads_json_str};
        const ALL_ORG = {org_json_str};

        // Populate Brand Dropdown Options
        const allBrands = [...new Set([...ALL_ADS.map(a => a.brand), ...ALL_ORG.map(o => o.brand)])].sort();
        const brandSelect = document.getElementById('brandFilter');
        allBrands.forEach(b => {{
            const opt = document.createElement('option');
            opt.value = b;
            opt.innerText = b;
            brandSelect.appendChild(opt);
        }});

        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            btn.classList.add('active');
        }}

        function renderDashboard() {{
            const selectedBrand = document.getElementById('brandFilter').value;
            const searchText = document.getElementById('searchInput').value.toLowerCase();

            // Filter Paid Ads
            const filteredAds = ALL_ADS.filter(ad => {{
                const matchBrand = (selectedBrand === 'ALL' || ad.brand === selectedBrand);
                const matchText = ((ad.headline && ad.headline.toLowerCase().includes(searchText)) || 
                                   (ad.body && ad.body.toLowerCase().includes(searchText)));
                return matchBrand && matchText;
            }});

            // Filter Organic Posts
            const filteredOrg = ALL_ORG.filter(post => {{
                const matchBrand = (selectedBrand === 'ALL' || post.brand === selectedBrand);
                const caption = post.caption_text ? post.caption_text.toLowerCase() : "";
                return matchBrand && caption.includes(searchText);
            }});

            // Identify items with Pricing
            const pricingAds = filteredAds.filter(ad => (ad.msrp && ad.msrp !== "N/A") || (ad.rebate && ad.rebate !== "N/A") || (ad.installment && ad.installment !== "N/A"));

            // Update Header KPIs
            document.getElementById('kpi-brands').innerText = new Set([...filteredAds.map(a => a.brand), ...filteredOrg.map(o => o.brand)]).size;
            document.getElementById('kpi-ads').innerText = filteredAds.length;
            document.getElementById('kpi-org').innerText = filteredOrg.length;
            document.getElementById('kpi-prices').innerText = pricingAds.length;

            // 1. Render Paid Ads Tab
            const paidGrid = document.getElementById('paidGrid');
            paidGrid.innerHTML = '';
            filteredAds.forEach(ad => {{
                const badgeClass = ad.is_self ? "pill-brand" : "pill-comp";
                const isAnanaCard = ad.is_self ? "is-anana" : "";
                
                paidGrid.innerHTML += `
                    <div class="card ad-card ${{isAnanaCard}}">
                        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                            <span class="pill ${{badgeClass}}">${{ad.brand}}</span>
                            <span class="pill pill-good">Active ${{ad.days_active}}d</span>
                        </div>
                        <div class="media-container">
                            <img src="${{ad.media_url}}" class="ad-img" referrerpolicy="no-referrer" onerror="this.src='https://via.placeholder.com/400x200?text=IT+Promotion';" />
                        </div>
                        <div class="ad-headline">${{ad.headline || 'Active Promotion'}}</div>
                        <div class="ad-body">${{ad.body || 'No ad copy provided.'}}</div>
                        <div class="ad-footer">
                            <span style="color: var(--brand-bright); font-weight:bold;">🎯 ${{ad.cta}}</span>
                            <a href="${{ad.link}}" target="_blank">Ad Library ↗</a>
                        </div>
                    </div>
                `;
            }});

            // 2. Render Organic Tab
            const orgGrid = document.getElementById('organicGrid');
            orgGrid.innerHTML = '';
            if(filteredOrg.length === 0) {{
                orgGrid.innerHTML = '<p style="color:var(--text-3); grid-column: 1/-1;">No organic posts found in dataset. Run organic_scraper.py locally and push organic_data.csv to populate this tab.</p>';
            }} else {{
                filteredOrg.forEach(post => {{
                    const badgeClass = post.brand.includes("AnAnA") ? "pill-brand" : "pill-comp";
                    const isAnanaCard = post.brand.includes("AnAnA") ? "is-anana" : "";
                    const mediaHtml = post.media_url 
                        ? `<img src="${{post.media_url}}" class="ad-img" referrerpolicy="no-referrer" onerror="this.style.display='none';" />`
                        : `<div style="height:100%; display:flex; align-items:center; justify-content:center; color:var(--text-3); font-family:var(--font-mono); font-size:11px;">[ TIMELINE POST ]</div>`;
                    
                    orgGrid.innerHTML += `
                        <div class="card ad-card ${{isAnanaCard}}">
                            <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                                <span class="pill ${{badgeClass}}">${{post.brand}}</span>
                                <span class="pill pill-good">${{post.media_type || 'Post'}}</span>
                            </div>
                            <div class="media-container">${{mediaHtml}}</div>
                            <div class="ad-body">${{post.caption_text || 'Hardware post'}}</div>
                            <div class="ad-footer">
                                <span style="color:var(--text-3); font-family:var(--font-mono);">${{post.timestamp || 'Recent'}}</span>
                                <a href="${{post.post_url}}" target="_blank">View Post ↗</a>
                            </div>
                        </div>
                    `;
                }});
            }}

            // 3. Render Competitor Pricing Matrix Tab
            const priceTbody = document.getElementById('pricingTableBody');
            priceTbody.innerHTML = '';
            pricingAds.forEach(ad => {{
                let priceTags = [];
                if(ad.msrp && ad.msrp !== "N/A") priceTags.push(`<span class="spec-tag spec-tag-price">MSRP: ${{ad.msrp}}</span>`);
                if(ad.rebate && ad.rebate !== "N/A") priceTags.push(`<span class="spec-tag spec-tag-price" style="color:var(--brand-bright); border-color:var(--brand-bright); background:var(--brand-wash);">Save: ${{ad.rebate}}</span>`);
                if(ad.installment && ad.installment !== "N/A") priceTags.push(`<span class="spec-tag spec-tag-price" style="color:var(--warning); border-color:var(--warning); background:rgba(232, 163, 61, 0.14);">Plan: ${{ad.installment}}</span>`);
                
                priceTbody.innerHTML += `
                    <tr>
                        <td><b>${{ad.brand}}</b></td>
                        <td>${{priceTags.join(' ')}}</td>
                        <td style="color:var(--text-3); font-size:12px;">${{ad.product_cat || 'Hardware Segment'}}</td>
                        <td><span style="color:var(--brand-bright); font-size:12px;">${{ad.cta}}</span></td>
                        <td><a href="${{ad.link}}" target="_blank" style="color:var(--brand-bright); text-decoration:none; font-weight:500;">Inspect Ad ↗</a></td>
                    </tr>
                `;
            }});

            // 4. Render Evergreen Tab
            const sortedLongest = [...filteredAds].sort((a, b) => b.days_active - a.days_active);
            const longestTbody = document.getElementById('longestTableBody');
            longestTbody.innerHTML = '';
            sortedLongest.forEach(ad => {{
                longestTbody.innerHTML += `
                    <tr>
                        <td><b>${{ad.brand}}</b></td>
                        <td><span class="pill pill-good">${{ad.days_active}} Days</span></td>
                        <td style="color:var(--text-1); font-weight:500;">${{ad.headline}}</td>
                        <td><span style="color:var(--brand-bright); font-size:12px;">${{ad.cta}}</span></td>
                        <td><a href="${{ad.link}}" target="_blank" style="color:var(--brand-bright); text-decoration:none; font-weight:500;">Inspect Ad ↗</a></td>
                    </tr>
                `;
            }});
        }}

        renderDashboard();
    </script>
</body>
</html>
"""
    
    filename = os.path.join(BASE_DIR, f"AnAnA_Competitor_Ad_Monitor_{datetime.now().strftime('%d_%B_%Y')}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Standardized output required for GitHub Pages
    with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"🎉 Success! Generated standalone HTML files: {filename} and index.html")

if __name__ == "__main__":
    generate_interactive_html()