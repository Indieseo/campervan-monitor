@echo off
echo ========================================
echo ULTIMATE SCRAPING FIXES
echo ========================================
echo.
echo This will fix the cookie consent issues and get real pricing data:
echo - Roadsurfer Ultra Scraper (Fixed)
echo - McRent, Yescapa, Cruise America (Ultimate Fix)
echo.
echo Starting in 5 seconds...
timeout /t 5 /nobreak > nul

echo.
echo [1/3] Fixing Roadsurfer Ultra Scraper...
echo This will handle cookies properly and extract real pricing data
echo.
python scrapers/roadsurfer_ultra_fixed.py

echo.
echo [2/3] Running Ultimate Competitor Fix...
echo This will fix McRent, Yescapa, and Cruise America
echo.
python scrapers/ultimate_competitor_fix.py

echo.
echo [3/3] Generating summary report...
echo.
python -c "
import json
from pathlib import Path
from datetime import datetime

print('📊 GENERATING SUMMARY REPORT')
print('='*50)

# Check for results files
results_files = list(Path('data/live_pricing').glob('*_fixed_*.json'))
results_files.extend(list(Path('data/live_pricing').glob('*_competitor_fix_*.json')))

if results_files:
    print(f'Found {len(results_files)} result files:')
    for file in results_files:
        print(f'  - {file.name}')
    
    # Load and summarize results
    total_prices = 0
    successful_companies = 0
    
    for file in results_files:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            
            if 'prices' in data:
                prices = data['prices']
                total_prices += len(prices)
                if len(prices) > 0:
                    successful_companies += 1
                    print(f'✅ {data.get(\"company\", \"Unknown\")}: {len(prices)} prices')
                else:
                    print(f'❌ {data.get(\"company\", \"Unknown\")}: No prices')
            elif 'results' in data:
                for result in data['results']:
                    if result.get('success', False):
                        successful_companies += 1
                        print(f'✅ {result[\"company\"]}: {result[\"total_prices\"]} prices')
                    else:
                        print(f'❌ {result[\"company\"]}: Failed')
        except Exception as e:
            print(f'Error reading {file}: {e}')
    
    print(f'\\n📊 SUMMARY:')
    print(f'Total prices found: {total_prices}')
    print(f'Successful companies: {successful_companies}')
    
    if total_prices > 0:
        print('\\n🎉 SUCCESS! Real pricing data has been extracted!')
    else:
        print('\\n⚠️ No pricing data found. Check the logs for issues.')
else:
    print('No result files found. Check if the scrapers ran successfully.')

print('\\n' + '='*50)
"

echo.
echo ========================================
echo ULTIMATE FIXES COMPLETE
echo ========================================
echo.
echo Check the following for results:
echo - data/live_pricing/roadsurfer_ultra_fixed_*.json
echo - data/live_pricing/ultimate_competitor_fix_*.json
echo - data/screenshots/ (for evidence)
echo.
echo Launching dashboard to view results...
python -m streamlit run dashboard/comprehensive_calendar_display.py --server.port 8505

pause



