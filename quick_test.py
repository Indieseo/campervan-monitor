"""Quick test of all 5 scrapers - Simple output"""
import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from scrapers.tier1_scrapers import (
    RoadsurferScraper,
    McRentScraper,
    GoboonyScrap,
    YescapaScraper,
    CamperdaysScraper
)

async def test_all():
    """Test all scrapers and show simple results"""
    scrapers = [
        RoadsurferScraper(use_browserless=False),
        McRentScraper(use_browserless=False),
        GoboonyScrap(use_browserless=False),
        YescapaScraper(use_browserless=False),
        CamperdaysScraper(use_browserless=False)
    ]

    results = []
    for scraper in scrapers:
        print(f"\nTesting {scraper.company_name}...")
        try:
            data = await scraper.scrape()
            price = data.get('base_nightly_rate', 0)
            locations = len(data.get('locations_available', []))
            completeness = data.get('data_completeness_pct', 0)
            reviews = data.get('customer_review_avg')

            result = {
                'company': scraper.company_name,
                'price': price,
                'locations': locations,
                'completeness': completeness,
                'reviews': reviews,
                'success': price is not None and price > 0
            }
            results.append(result)

            status = "OK" if result['success'] else "FAIL"
            print(f"  [{status}] Price: EUR{price if price else 0}/night")
            print(f"  Locations: {locations}, Completeness: {completeness:.1f}%")

        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append({
                'company': scraper.company_name,
                'success': False,
                'error': str(e)
            })

        await asyncio.sleep(2)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    working = sum(1 for r in results if r.get('success', False))
    print(f"Price Extraction: {working}/5 ({working*20}%)")
    print(f"Target: 4/5 (80%) - {'MET' if working >= 4 else 'NOT MET'}")

    for r in results:
        if r.get('success'):
            print(f"  [OK] {r['company']}: EUR{r['price']}/night")
        else:
            print(f"  [FAIL] {r['company']}")

    return results

if __name__ == "__main__":
    asyncio.run(test_all())
