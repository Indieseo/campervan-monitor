@echo off
echo ===============================================
echo   Indie Campers Competitive Intelligence
echo   Dashboard Launcher
echo ===============================================
echo.
echo Starting dashboard on http://localhost:8501
echo.

cd /d "%~dp0"
streamlit run dashboard/app.py

pause
