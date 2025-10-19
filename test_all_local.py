"""Test all 5 Tier 1 scrapers with local browsers"""
import asyncio
from scrapers.tier1_scrapers import (
    RoadsurferScraper, McRentScraper, GoboonyScrap,
    YescapaScraper, CamperdaysScraper
)

async def test_all():
    scrapers = [
        RoadsurferScraper(use_browserless=False),
        GoboonyScrap(use_browserless=False),
        YescapaScraper(use_browserless=False),
        McRentScraper(use_browserless=False),
        CamperdaysScraper(use_browserless=False)
    ]

    results = []
    for scraper in scrapers:
        print(f"\n{'='*70}")
        print(f"Testing {scraper.company_name}...")
        print('='*70)
        try:
            data = await scraper.scrape()
            results.append(data)
            print(f"[PASS] {scraper.company_name}: {data['data_completeness_pct']:.1f}% complete")
        except Exception as e:
            print(f"[FAIL] {scraper.company_name}: {str(e)[:100]}")
            results.append({
                'company_name': scraper.company_name,
                'data_completeness_pct': 0,
                'base_nightly_rate': None,
                'customer_review_avg': None,
                'review_count': None,
                'locations_available': []
            })

    print('\n' + '='*70)
    print('FINAL RESULTS - ALL 5 SCRAPERS (LOCAL BROWSER)')
    print('='*70)

    for r in results:
        print(f"\nCompany: {r['company_name']}")
        print(f"  Completeness: {r['data_completeness_pct']:.1f}%")
        print(f"  Price: EUR {r['base_nightly_rate']}")
        print(f"  Reviews: {r['customer_review_avg']} / {r['review_count']}")
        print(f"  Locations: {len(r['locations_available'])}")

    avg = sum(r['data_completeness_pct'] for r in results) / len(results)
    print('\n' + '='*70)
    print(f'AVERAGE COMPLETENESS: {avg:.1f}%')
    print(f'TARGET: 60%+')
    print(f'STATUS: {"[PASS] MET" if avg >= 60 else "[FAIL] BELOW"}')
    print('='*70)

    # Detailed breakdown
    print('\nDETAILED METRICS:')
    prices_working = sum(1 for r in results if r['base_nightly_rate'] is not None)
    reviews_working = sum(1 for r in results if r['customer_review_avg'] or r['review_count'])
    locations_working = sum(1 for r in results if len(r['locations_available']) > 0)

    print(f"  Pricing extracted: {prices_working}/5 (target: 4/5)")
    print(f"  Reviews extracted: {reviews_working}/5 (target: 3/5)")
    print(f"  Locations extracted: {locations_working}/5 (target: 4/5)")

if __name__ == "__main__":
    asyncio.run(test_all())
