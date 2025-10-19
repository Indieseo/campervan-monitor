@echo off
REM Quick Start - Focused Intelligence System

echo ========================================
echo    Indie Campers Intelligence System
echo    Focused Approach - Quality Data
echo ========================================
echo.

cd /d C:\Projects\campervan-monitor

REM Check if virtual environment exists
if not exist "venv" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/5] Virtual environment exists ✓
)

REM Activate virtual environment
echo [2/5] Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo [3/5] Installing dependencies...
pip install -q -r requirements.txt

REM Install Playwright browsers
echo [4/5] Installing Playwright browsers...
python -m playwright install chromium

REM Initialize database
echo [5/5] Initializing database...
python -c "from database.models import init_database; init_database()"

echo.
echo ========================================
echo    Setup Complete! ✅
echo ========================================
echo.
echo Next Steps:
echo.
echo 1. Gather intelligence:
echo    python run_intelligence.py
echo.
echo 2. Launch dashboard:
echo    streamlit run dashboard\app.py
echo.
echo 3. View logs:
echo    type logs\intel_YYYY-MM-DD.log
echo.
pause
