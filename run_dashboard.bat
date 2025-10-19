@echo off
REM Windows Run Script for Campervan Price Monitor
REM Double-click this file to run the dashboard

echo.
echo ========================================
echo   Campervan Price Monitor Dashboard
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Check if activation worked
if errorlevel 1 (
    echo ERROR: Virtual environment not found!
    echo Run setup_windows.ps1 first
    pause
    exit /b 1
)

REM Run Streamlit dashboard
echo Starting dashboard on http://localhost:8501
echo.
streamlit run dashboard\app.py --server.port 8501

pause
