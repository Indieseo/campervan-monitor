"""
Test screenshot fixes for Goboony, Outdoorsy, RVshare
Verify that screenshots show actual campervan listings
"""

import asyncio
import sys
from scrapers.tier1_scrapers import GoboonyScrap, OutdoorsyScraper, RVshareScraper

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def test_screenshots():
    """Test 3 scrapers with cookie/listing fixes"""

    scrapers = [
        GoboonyScrap(use_browserless=False),
        OutdoorsyScraper(use_browserless=False),
        RVshareScraper(use_browserless=False)
    ]

    print("\n" + "="*70)
    print("TESTING SCREENSHOT FIXES - 3 SCRAPERS")
    print("="*70)

    for scraper in scrapers:
        print(f"\n{'='*70}")
        print(f"Testing {scraper.company_name}...")
        print('='*70)

        try:
            data = await scraper.scrape()

            print(f"\n[OK] {scraper.company_name} - COMPLETE")
            print(f"  Base Rate: {data['currency']} {data['base_nightly_rate'] or 'N/A'}")
            print(f"  Completeness: {data['data_completeness_pct']:.1f}%")
            print(f"  Screenshot should show actual listings now!")

        except Exception as e:
            print(f"\n[FAIL] {scraper.company_name} - Error: {str(e)[:200]}")

        await asyncio.sleep(2)

    print(f"\n{'='*70}")
    print("TEST COMPLETE - Check screenshots in data/screenshots/")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    asyncio.run(test_screenshots())
