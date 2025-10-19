@echo off
REM ========================================
REM Automated Daily Competitive Crawl Setup
REM Creates Windows Task Scheduler job
REM ========================================

echo.
echo ========================================
echo   Daily Competitive Crawl Setup
echo ========================================
echo.

REM Get current directory
set "SCRIPT_DIR=%~dp0"
set "PYTHON_PATH=%SCRIPT_DIR%venv\Scripts\python.exe"
set "CRAWL_SCRIPT=%SCRIPT_DIR%live_crawl_demo.py"

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo [ERROR] Python not found in virtual environment!
    echo Please run quick_start.bat first to set up the environment.
    pause
    exit /b 1
)

echo [1/4] Checking system...
echo       Python: %PYTHON_PATH%
echo       Script: %CRAWL_SCRIPT%
echo.

echo [2/4] Creating batch runner...
REM Create a runner batch file
set "RUNNER_PATH=%SCRIPT_DIR%run_daily_crawl_auto.bat"
(
    echo @echo off
    echo REM Auto-generated daily crawl runner
    echo cd /d "%SCRIPT_DIR%"
    echo call venv\Scripts\activate.bat
    echo python live_crawl_demo.py ^>^> logs\daily_crawl.log 2^>^&1
    echo if errorlevel 1 (
    echo     echo [ERROR] Crawl failed at %%date%% %%time%% ^>^> logs\daily_crawl_errors.log
    echo ^)
) > "%RUNNER_PATH%"
echo       Created: %RUNNER_PATH%
echo.

echo [3/4] Setting up Windows Task Scheduler...
echo.
echo     Choose your preferred schedule:
echo     --------------------------------
echo     1) Daily at 8:00 AM (Recommended)
echo     2) Daily at 6:00 AM (Early bird)
echo     3) Daily at 10:00 AM (Late morning)
echo     4) Twice daily (8:00 AM and 6:00 PM)
echo     5) Custom time
echo     6) Skip automation setup
echo.

set /p choice="     Enter choice (1-6): "

if "%choice%"=="1" set "SCHEDULE_TIME=08:00"
if "%choice%"=="2" set "SCHEDULE_TIME=06:00"
if "%choice%"=="3" set "SCHEDULE_TIME=10:00"
if "%choice%"=="5" (
    set /p SCHEDULE_TIME="     Enter time (HH:MM format): "
)
if "%choice%"=="6" (
    echo.
    echo [SKIPPED] Automation setup skipped.
    echo          You can run manually: python live_crawl_demo.py
    echo.
    pause
    exit /b 0
)

if "%choice%"=="4" (
    echo.
    echo [INFO] Setting up twice-daily schedule...
    
    REM Morning crawl
    schtasks /create /tn "Campervan Competitive Crawl - Morning" /tr "\"%RUNNER_PATH%\"" /sc daily /st 08:00 /f
    if errorlevel 1 (
        echo [ERROR] Failed to create morning scheduled task!
        echo         Run this script as Administrator.
        pause
        exit /b 1
    )
    
    REM Evening crawl
    schtasks /create /tn "Campervan Competitive Crawl - Evening" /tr "\"%RUNNER_PATH%\"" /sc daily /st 18:00 /f
    if errorlevel 1 (
        echo [ERROR] Failed to create evening scheduled task!
        pause
        exit /b 1
    )
    
    echo [SUCCESS] Created two daily tasks:
    echo           - Morning: 8:00 AM
    echo           - Evening: 6:00 PM
    goto :done
)

if not defined SCHEDULE_TIME (
    echo [ERROR] Invalid choice!
    pause
    exit /b 1
)

REM Create the scheduled task
echo       Creating task for %SCHEDULE_TIME%...
schtasks /create /tn "Campervan Competitive Crawl" /tr "\"%RUNNER_PATH%\"" /sc daily /st %SCHEDULE_TIME% /f

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create scheduled task!
    echo         Possible reasons:
    echo         - Not running as Administrator
    echo         - Task Scheduler service not running
    echo.
    echo         Solution: Right-click this file and "Run as administrator"
    echo.
    pause
    exit /b 1
)

:done
echo.
echo [4/4] ========================================
echo        SETUP COMPLETE!
echo       ========================================
echo.
echo       Your automated daily crawl is configured!
echo.
echo       What happens now:
echo       ----------------
echo       - Every day at %SCHEDULE_TIME%, the system will:
echo         1. Crawl all 8 competitors
echo         2. Collect pricing and intelligence
echo         3. Save to database
echo         4. Generate screenshots
echo         5. Log results
echo.
echo       View results:
echo       -------------
echo       - Dashboard:  streamlit run dashboard/app.py
echo       - Logs:       logs\daily_crawl.log
echo       - Database:   database\campervan_intelligence.db
echo.
echo       Manage scheduled task:
echo       ----------------------
echo       - View:       taskschd.msc
echo       - Disable:    schtasks /change /tn "Campervan Competitive Crawl" /disable
echo       - Enable:     schtasks /change /tn "Campervan Competitive Crawl" /enable
echo       - Delete:     schtasks /delete /tn "Campervan Competitive Crawl" /f
echo.
echo       Test it now:
echo       ------------
echo       - Run manually:  python live_crawl_demo.py
echo       - Run scheduled: schtasks /run /tn "Campervan Competitive Crawl"
echo.
echo ========================================
echo.

REM Offer to run immediately
set /p run_now="Would you like to run a test crawl now? (Y/N): "
if /i "%run_now%"=="Y" (
    echo.
    echo [RUNNING] Starting test crawl...
    echo.
    call "%RUNNER_PATH%"
)

echo.
echo Done! Press any key to exit...
pause >nul






