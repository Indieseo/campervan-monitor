@echo off
REM Run Campervan Price Monitor (Main Engine)

echo.
echo ========================================
echo   Campervan Price Monitor - Engine
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Check activation
if errorlevel 1 (
    echo ERROR: Virtual environment not found!
    echo Run: .\scripts\setup_windows.ps1
    pause
    exit /b 1
)

REM Run main monitor
echo Running price monitor...
echo.
python campervan_price_monitor.py

pause
