"""
Quick test of optimized scrapers - Tests the fixes
"""
import asyncio
import sys
from datetime import datetime

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from scrapers.tier1_scrapers import (
    RoadsurferScraper, McRentScraper, GoboonyScrap, 
    YescapaScraper, CamperdaysScraper
)

async def test_fixes():
    """Test the two main fixes: McRent error and speed optimizations"""
    
    print("\n" + "="*70)
    print("TESTING OPTIMIZED SCRAPERS")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Test 1: McRent (fixed week_prices bug)
    print("[1/5] Testing McRent (fixed variable bug)...")
    start = datetime.now()
    try:
        scraper = McRentScraper(use_browserless=False)
        data = await scraper.scrape()
        duration = (datetime.now() - start).total_seconds()
        print(f"      ✅ McRent: {data['data_completeness_pct']:.1f}% in {duration:.1f}s")
        print(f"         Price: €{data.get('base_nightly_rate', 'N/A')}/night")
    except Exception as e:
        duration = (datetime.now() - start).total_seconds()
        print(f"      ❌ McRent FAILED: {str(e)[:100]} ({duration:.1f}s)")
    
    # Test 2: Roadsurfer (speed test)
    print("\n[2/5] Testing Roadsurfer (speed optimized)...")
    start = datetime.now()
    try:
        scraper = RoadsurferScraper(use_browserless=False)
        data = await scraper.scrape()
        duration = (datetime.now() - start).total_seconds()
        print(f"      ✅ Roadsurfer: {data['data_completeness_pct']:.1f}% in {duration:.1f}s")
        if duration < 60:
            print(f"         FAST! (target: <60s)")
        print(f"         Price: €{data.get('base_nightly_rate', 'N/A')}/night")
    except Exception as e:
        duration = (datetime.now() - start).total_seconds()
        print(f"      ❌ Roadsurfer FAILED: {str(e)[:100]} ({duration:.1f}s)")
    
    # Test 3: Goboony (quick test)
    print("\n[3/5] Testing Goboony...")
    start = datetime.now()
    try:
        scraper = GoboonyScrap(use_browserless=False)
        data = await scraper.scrape()
        duration = (datetime.now() - start).total_seconds()
        print(f"      ✅ Goboony: {data['data_completeness_pct']:.1f}% in {duration:.1f}s")
    except Exception as e:
        duration = (datetime.now() - start).total_seconds()
        print(f"      ❌ Goboony FAILED: {str(e)[:100]} ({duration:.1f}s)")
    
    # Test 4: Yescapa
    print("\n[4/5] Testing Yescapa...")
    start = datetime.now()
    try:
        scraper = YescapaScraper(use_browserless=False)
        data = await scraper.scrape()
        duration = (datetime.now() - start).total_seconds()
        print(f"      ✅ Yescapa: {data['data_completeness_pct']:.1f}% in {duration:.1f}s")
    except Exception as e:
        duration = (datetime.now() - start).total_seconds()
        print(f"      ❌ Yescapa FAILED: {str(e)[:100]} ({duration:.1f}s)")
    
    # Test 5: Camperdays
    print("\n[5/5] Testing Camperdays...")
    start = datetime.now()
    try:
        scraper = CamperdaysScraper(use_browserless=False)
        data = await scraper.scrape()
        duration = (datetime.now() - start).total_seconds()
        print(f"      ✅ Camperdays: {data['data_completeness_pct']:.1f}% in {duration:.1f}s")
    except Exception as e:
        duration = (datetime.now() - start).total_seconds()
        print(f"      ❌ Camperdays FAILED: {str(e)[:100]} ({duration:.1f}s)")
    
    print("\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70)
    print(f"Finished: {datetime.now().strftime('%H:%M:%S')}\n")
    print("Next: Run full test with 'python live_crawl_demo.py'")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_fixes())

