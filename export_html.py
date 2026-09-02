import pandas as pd
import json
import os
from datetime import datetime

def generate_interactive_html():
    if not os.path.exists('ads_data.csv'):
        print("❌ Error: ads_data.csv not found! Run scraper.py first.")
        return

    df = pd.read_csv('ads_data.csv')
    df = df.fillna("")
    
    # Ensure days_active is numeric to track Evergreen 30+ day profitable campaigns
    df['days_active'] = pd.to_numeric(df['days_active'], errors='coerce').fillna(1).astype(int)
    
    ads_json = df.to_dict(orient='records')
    ads_json_str = json.dumps(ads_json)
    
    today_str = datetime.now().strftime("%A %d %B %Y")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AnAnA Computer — Competitor Ad Monitor</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #0E1117;
            --card-bg: #181D28;
            --border-color: #283042;
            --text-primary: #FFFFFF;
            --text-secondary: #8F9CAE;
            --accent-orange: #FF6A00;
            --accent-red: #E32636;
            --accent-green: #00E676;
            --accent-blue: #00B4D8;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            margin: 0;
            padding: 24px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 4px solid var(--accent-red);
            padding-left: 16px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 4px 0 0 0;
            color: var(--text-secondary);
            font-size: 13px;
        }}
        .filter-bar {{
            background: #151A24;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }}
        .filter-group label {{
            display: block;
            font-size: 11px;
            font-weight: bold;
            color: var(--text-secondary);
            text-transform: uppercase;
            margin-bottom: 6px;
        }}
        .filter-group select, .filter-group input {{
            width: 100%;
            background: #1E2433;
            border: 1px solid var(--border-color);
            color: #fff;
            padding: 8px 10px;
            border-radius: 6px;
            font-size: 13px;
            box-sizing: border-box;
        }}
        .kpi-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: #1E222D;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px;
        }}
        .kpi-title {{
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-weight: bold;
        }}
        .kpi-val {{
            font-size: 26px;
            font-weight: bold;
            margin: 6px 0;
        }}
        .kpi-sub {{
            font-size: 11px;
            color: #717D8A;
        }}
        .tabs {{
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 20px;
        }}
        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 10px 16px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            border-bottom: 2px solid transparent;
        }}
        .tab-btn.active {{
            color: var(--text-primary);
            border-bottom: 2px solid var(--accent-orange);
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
        .creative-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
        }}
        .ad-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .badge {{
            font-size: 11px;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 4px;
        }}
        .badge-anana {{ background: var(--accent-red); color: #fff; }}
        .badge-comp {{ background: var(--accent-orange); color: #fff; }}
        .badge-days {{ background: #232D3F; color: var(--accent-green); }}
        .ad-img {{
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 6px;
            margin: 10px 0;
            background: #111;
        }}
        .ad-headline {{
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 6px;
            color: #fff;
        }}
        .ad-body {{
            font-size: 12px;
            color: #A0AEC0;
            height: 50px;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 12px;
        }}
        .ad-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #232936;
            padding-top: 10px;
            font-size: 11px;
        }}
        .ad-footer a {{
            color: var(--accent-orange);
            text-decoration: none;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #12161F;
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            padding: 12px 14px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
            font-size: 13px;
        }}
        th {{ background: #1A1F2C; color: var(--text-secondary); text-transform: uppercase; font-size: 11px; }}
        .callout {{
            background: #151A24;
            border-left: 4px solid var(--accent-blue);
            border-radius: 4px;
            padding: 16px;
            margin-bottom: 16px;
        }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>Competitor Ad Monitor — Meta Ads Library</h1>
            <p>Phnom Penh IT Retail Market · collected {today_str}</p>
        </div>
        <div>
            <span style="font-size: 12px; background: #232D3F; color: var(--accent-green); padding: 6px 12px; border-radius: 20px; font-weight: bold;">● Live Snapshot</span>
        </div>
    </div>

    <!-- FILTER BAR -->
    <div class="filter-bar">
        <div class="filter-group">
            <label>Competitor Brand</label>
            <select id="brandFilter" onchange="renderDashboard()">
                <option value="ALL">All Competitors</option>
            </select>
        </div>
        <div class="filter-group">
            <label>Search Text</label>
            <input type="text" id="searchInput" placeholder="Search keywords (e.g. RTX, Laptop)..." oninput="renderDashboard()" />
        </div>
    </div>

    <!-- STATS ROW -->
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-title">Active Brands Tracked</div>
            <div class="kpi-val" id="kpi-brands">0</div>
            <div class="kpi-sub">Across Phnom Penh</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Total Active Creatives</div>
            <div class="kpi-val" id="kpi-total">0</div>
            <div class="kpi-sub">Live scanned ads</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">New in Last 7 Days</div>
            <div class="kpi-val" style="color: var(--accent-green);" id="kpi-new7">0</div>
            <div class="kpi-sub">Recent launches</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Longest Running Ad</div>
            <div class="kpi-val" id="kpi-longest">0d</div>
            <div class="kpi-sub" id="kpi-longest-brand">-</div>
        </div>
    </div>

    <!-- TABS -->
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('wall', this)">🖼️ Creative Wall</button>
        <button class="tab-btn" onclick="switchTab('new7', this)">⚡ New (Last 7 Days)</button>
        <button class="tab-btn" onclick="switchTab('longest', this)">⏳ Longest Running</button>
        <button class="tab-btn" onclick="switchTab('strategy', this)">💡 Strategic Recommendations</button>
        <button class="tab-btn" onclick="switchTab('methodology', this)">ℹ️ Methodology & Limits</button>
    </div>

    <!-- TAB 1: CREATIVE WALL -->
    <div id="tab-wall" class="tab-content active">
        <div class="creative-grid" id="creativeGrid"></div>
    </div>

    <!-- TAB 2: NEW ADS -->
    <div id="tab-new7" class="tab-content">
        <div class="creative-grid" id="newAdsGrid"></div>
    </div>

    <!-- TAB 3: LONGEST ADS -->
    <div id="tab-longest" class="tab-content">
        <table>
            <thead>
                <tr>
                    <th>Brand</th>
                    <th>Days Active</th>
                    <th>Headline</th>
                    <th>Call to Action</th>
                    <th>Link</th>
                </tr>
            </thead>
            <tbody id="longestTableBody"></tbody>
        </table>
    </div>

    <!-- TAB 4: RECOMMENDATIONS -->
    <div id="tab-strategy" class="tab-content">
        <div class="callout">
            <h3 style="margin-top:0; color: var(--accent-blue);">1. Implement Installment Anchoring (AEON / 0% Plans)</h3>
            <p style="font-size:13px; line-height:1.6; color:#E2E8F0;">
                PTC Computer drives high engagement on $1,000+ gaming PCs by advertising <b>"$45/month with 0% installment"</b> rather than showing full retail prices. Feature monthly payment breakdowns on your high-end ASUS and Legion creative overlays.
            </p>
        </div>
        <div class="callout">
            <h3 style="margin-top:0; color: var(--accent-green);">2. Build an Evergreen B2B Funnel for MikroTik & Ruijie</h3>
            <p style="font-size:13px; line-height:1.6; color:#E2E8F0;">
                High-margin enterprise networking hardware should be separated from consumer laptop promotions and routed directly to dedicated IT Lead Gen campaigns.
            </p>
        </div>
        <div class="callout">
            <h3 style="margin-top:0; color: var(--accent-orange);">3. Switch from Static Banners to 15s Benchmark Reels</h3>
            <p style="font-size:13px; line-height:1.6; color:#E2E8F0;">
                Short video benchmark reels comparing gaming performance (FPS) drive significantly higher click-through rates across local tech audiences than static image posts.
            </p>
        </div>
    </div>

    <!-- TAB 5: METHODOLOGY -->
    <div id="tab-methodology" class="tab-content">
        <div class="callout">
            <h3 style="margin-top:0; color: var(--accent-blue);">🔍 How Data Was Collected</h3>
            <p style="font-size:13px; line-height:1.6; color:#E2E8F0;">
                Data is scraped directly from Meta's public Ad Library using exact brand Page IDs in Cambodia (KH). Days active are dynamically calculated from the recorded launch date.
            </p>
            <h3 style="margin-top:20px; color: var(--accent-red);">⚠️ Limitations</h3>
            <p style="font-size:13px; line-height:1.6; color:#E2E8F0;">
                Meta does not disclose private commercial ad spend or conversion rates. It reveals <i>what</i> competitors are boosting, but not their exact revenue or ROAS.
            </p>
        </div>
    </div>

    <script>
        const ALL_ADS = {ads_json_str};

        // Populate Brand Dropdown
        const brands = [...new Set(ALL_ADS.map(a => a.brand))];
        const brandSelect = document.getElementById('brandFilter');
        brands.forEach(b => {{
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

            const filtered = ALL_ADS.filter(ad => {{
                const matchBrand = (selectedBrand === 'ALL' || ad.brand === selectedBrand);
                const matchText = (ad.headline.toLowerCase().includes(searchText) || ad.body.toLowerCase().includes(searchText));
                return matchBrand && matchText;
            }});

            // Update KPIs
            document.getElementById('kpi-brands').innerText = new Set(filtered.map(a => a.brand)).size;
            document.getElementById('kpi-total').innerText = filtered.length;
            
            const new7 = filtered.filter(a => a.days_active <= 7);
            document.getElementById('kpi-new7').innerText = new7.length;

            const sortedLongest = [...filtered].sort((a, b) => b.days_active - a.days_active);
            if (sortedLongest.length > 0) {{
                document.getElementById('kpi-longest').innerText = sortedLongest[0].days_active + 'd';
                document.getElementById('kpi-longest-brand').innerText = sortedLongest[0].brand;
            }} else {{
                document.getElementById('kpi-longest').innerText = '0d';
                document.getElementById('kpi-longest-brand').innerText = '-';
            }}

            // Render Creative Wall
            const grid = document.getElementById('creativeGrid');
            grid.innerHTML = '';
            filtered.forEach(ad => {{
                const badgeClass = ad.is_self ? 'badge-anana' : 'badge-comp';
                grid.innerHTML += `
                    <div class="ad-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="badge ${{badgeClass}}">${{ad.brand}}</span>
                            <span class="badge badge-days">Active ${{ad.days_active}}d</span>
                        </div>
                        <img src="${{ad.media_url}}" class="ad-img" onerror="this.src='https://via.placeholder.com/400x200?text=Ad+Creative'" />
                        <div class="ad-headline">${{ad.headline}}</div>
                        <div class="ad-body">${{ad.body}}</div>
                        <div class="ad-footer">
                            <span style="color: var(--accent-blue);">🎯 ${{ad.cta}}</span>
                            <a href="${{ad.link}}" target="_blank">Ad Library ↗</a>
                        </div>
                    </div>
                `;
            }});

            // Render New in 7 Days Tab
            const newGrid = document.getElementById('newAdsGrid');
            newGrid.innerHTML = '';
            new7.forEach(ad => {{
                newGrid.innerHTML += `
                    <div class="ad-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="badge badge-comp">${{ad.brand}}</span>
                            <span class="badge badge-days">Launched ${{ad.days_active}}d ago</span>
                        </div>
                        <img src="${{ad.media_url}}" class="ad-img" onerror="this.src='https://via.placeholder.com/400x200?text=New+Creative'" />
                        <div class="ad-headline">${{ad.headline}}</div>
                        <div class="ad-body">${{ad.body}}</div>
                        <div class="ad-footer">
                            <span style="color: var(--accent-blue);">🎯 ${{ad.cta}}</span>
                            <a href="${{ad.link}}" target="_blank">Ad Library ↗</a>
                        </div>
                    </div>
                `;
            }});

            // Render Longest Running Table
            const tbody = document.getElementById('longestTableBody');
            tbody.innerHTML = '';
            sortedLongest.forEach(ad => {{
                tbody.innerHTML += `
                    <tr>
                        <td><b>${{ad.brand}}</b></td>
                        <td><span class="badge badge-days">${{ad.days_active}} days</span></td>
                        <td>${{ad.headline}}</td>
                        <td>${{ad.cta}}</td>
                        <td><a href="${{ad.link}}" target="_blank" style="color: var(--accent-orange);">open ↗</a></td>
                    </tr>
                `;
            }});
        }}

        // Initial Load
        renderDashboard();
    </script>
</body>
</html>
"""
    
    filename = f"AnAnA_Competitor_Ad_Monitor_{datetime.now().strftime('%d_%B_%Y')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Standardized output required for GitHub Pages
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"🎉 Success! Generated standalone HTML files: {filename} and index.html")

if __name__ == "__main__":
    generate_interactive_html()