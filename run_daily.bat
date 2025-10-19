@echo off
REM Daily Intelligence Gathering Script
REM Runs automatically via Windows Task Scheduler

echo ========================================
echo Campervan Intelligence - Daily Run
echo Started: %date% %time%
echo ========================================

cd /d C:\Projects\campervan-monitor

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set encoding for proper output
set PYTHONIOENCODING=utf-8

REM Run intelligence gathering
echo.
echo Running intelligence gathering...
python run_intelligence.py

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS: Intelligence gathering complete
    echo Completed: %date% %time%
    echo ========================================
    echo Success: %date% %time% >> logs\daily_success.log
) else (
    echo.
    echo ========================================
    echo ERROR: Intelligence gathering failed
    echo Error Code: %ERRORLEVEL%
    echo Time: %date% %time%
    echo ========================================
    echo Error: %date% %time% - Code: %ERRORLEVEL% >> logs\daily_errors.log
)

REM Optional: Send completion notification
REM Uncomment next line to get email notifications
REM python scripts\send_completion_email.py

exit /b %ERRORLEVEL%
