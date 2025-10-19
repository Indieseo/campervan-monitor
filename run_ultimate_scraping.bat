@echo off
echo ========================================
echo ULTIMATE COMPETITOR SCRAPING
echo ========================================
echo.
echo This will test ALL strategies to get the remaining 3 competitors working:
echo - McRent (Error pages)
echo - Yescapa (Cookie popups)
echo - Cruise America (Error pages)
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak > nul

echo.
echo [1/4] Testing McRent with advanced strategies...
python scrapers/test_mcrent_advanced.py

echo.
echo [2/4] Testing Yescapa with cookie bypass...
python scrapers/test_yescapa_advanced.py

echo.
echo [3/4] Testing Cruise America with multiple URLs...
python scrapers/test_cruise_america_advanced.py

echo.
echo [4/4] Running ultimate comprehensive scraper...
python scrapers/ultimate_competitor_scraper.py

echo.
echo ========================================
echo ULTIMATE SCRAPING COMPLETE
echo ========================================
echo.
echo Check the output/ directory for results
echo Check data/screenshots/ for visual evidence
echo.
echo Launching updated dashboard...
python -m streamlit run dashboard/comprehensive_calendar_display.py --server.port 8505

pause



