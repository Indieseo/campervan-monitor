@echo off
echo ========================================
echo ULTIMATE SCRAPING SYSTEM
echo ========================================
echo.
echo This system will run until 100%% completion is achieved:
echo - ALL 8 companies working
echo - ALL vehicle models identified
echo - 365 days of pricing data for each company
echo - Self-validation and verification
echo - NO STOPPING until 100%% complete
echo.
echo Starting in 5 seconds...
timeout /t 5 /nobreak > nul

echo.
echo [1/6] Initializing system...
python -c "import sys; print('Python version:', sys.version)"

echo.
echo [2/6] Running validation system...
python scrapers/validation_system.py

echo.
echo [3/6] Starting progress monitoring (background)...
start /B python scrapers/progress_monitor.py

echo.
echo [4/6] Starting master scraping controller...
echo This will run until 100%% completion is achieved
echo.
python scrapers/master_scraping_controller.py

echo.
echo [5/6] Final validation...
python scrapers/validation_system.py

echo.
echo [6/6] Generating final report...
python scrapers/progress_monitor.py

echo.
echo ========================================
echo ULTIMATE SCRAPING COMPLETE
echo ========================================
echo.
echo Check the following files for results:
echo - output/ultimate_results.json
echo - output/validation_results.json
echo - output/completion_report.json
echo - output/progress_report.json
echo.
echo Launching final dashboard...
python -m streamlit run dashboard/comprehensive_calendar_display.py --server.port 8505

pause



