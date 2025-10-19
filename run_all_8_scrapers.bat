@echo off
echo ================================================================================
echo CAMPERVAN MONITOR - ALL 8 COMPETITORS SCRAPER
echo ================================================================================
echo.
echo Running scraper for all 8 competitors...
echo This will take approximately 2 minutes.
echo.

python scrapers\simple_working_scraper.py

echo.
echo ================================================================================
echo SCRAPING COMPLETE!
echo ================================================================================
echo.
echo Results saved to: output\simple_working_scraper_[TIMESTAMP].json
echo Screenshots saved to: data\screenshots\
echo.
echo Check 100_PERCENT_SUCCESS_REPORT.md for details.
echo.
pause
