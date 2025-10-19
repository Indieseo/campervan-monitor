@echo off
REM Complete System Launcher
echo ========================================
echo CAMPERVAN PRICE MONITOR
echo ========================================
echo.

cd /d C:\Projects\campervan-monitor
call venv\Scripts\activate

echo [1/4] Checking database...
python check_database.py

echo.
echo [2/4] Running scrapers...
python fixed_scrapers.py

echo.
echo [3/4] Database updated!
python check_database.py

echo.
echo [4/4] Launching dashboard...
echo Dashboard URL: http://localhost:8501
echo.
streamlit run dashboard\app.py

pause
