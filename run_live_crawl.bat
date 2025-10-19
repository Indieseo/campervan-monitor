@echo off
cd /d C:\Projects\campervan-monitor
call venv\Scripts\activate
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
echo.
echo ================================
echo  CAMPERVAN PRICE MONITOR
echo  Live Crawl - Windows Edition  
echo ================================
echo.
python campervan_price_monitor.py
echo.
pause
