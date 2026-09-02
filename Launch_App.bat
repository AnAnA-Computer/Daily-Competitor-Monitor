@echo off
cd /d "%~dp0"
title AnAnA Computer - Omnichannel Intelligence Engine
color 0A

echo =======================================================
echo [1/3] Scraping Meta Ad Library (Paid Data)...
echo =======================================================
python scraper.py

echo.
echo =======================================================
echo [2/3] Scraping Telegram & Facebook (organic data)...
echo =======================================================
python organic_scraper.py

echo.
echo =======================================================
echo [3/3] Generating Dashboard...
echo =======================================================
python export_html.py

echo.
echo =======================================================
echo Launching Dashboard...
echo =======================================================
:: Make sure this matches the filename generated in export_html.py
for /f "delims=" %%i in ('dir AnAnA_Omnichannel_*.html /b /o-d') do (
    start "" "%%i"
    exit /b
)