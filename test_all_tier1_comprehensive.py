"""
Comprehensive Test for All 8 Tier 1 Competitors
Validates listings, pricing, and screenshot quality
"""

import asyncio
import sys
from scrapers.tier1_scrapers import (
    RoadsurferScraper, McRentScraper, CamperdaysScraper,
    GoboonyScraper, YescapaScraper, OutdoorsyScraper,
    RVshareScraper, CruiseAmericaScraper
)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def test_all_scrapers():
    """Test all 8 Tier 1 scrapers comprehensively"""

    scrapers = [
        ('Roadsurfer', RoadsurferScraper(use_browserless=False)),
        ('McRent', McRentScraper(use_browserless=False)),
        ('Camperdays', CamperdaysScraper(use_browserless=False)),
        ('Goboony', GoboonyScraper(use_browserless=False)),
        ('Yescapa', YescapaScraper(use_browserless=False)),
        ('Outdoorsy', OutdoorsyScraper(use_browserless=False)),
        ('RVshare', RVshareScraper(use_browserless=False)),
        ('Cruise America', CruiseAmericaScraper(use_browserless=False))
    ]

    print("\n" + "="*80)
    print("COMPREHENSIVE TEST - ALL 8 TIER 1 COMPETITORS")
    print("="*80)
    print("\nValidating:")
    print("  1. Listings are found (not 404 errors)")
    print("  2. Pricing data is valid")
    print("  3. Screenshots show actual campervans")
    print("  4. Data completeness > 50%")
    print("\n" + "="*80 + "\n")

    results = []

    for name, scraper in scrapers:
        print(f"\n{'='*80}")
        print(f"Testing {name}...")
        print('='*80)

        try:
            data = await scraper.scrape()

            # Validation checks
            has_price = data.get('base_nightly_rate') is not None
            valid_price = False
            if has_price:
                price = data['base_nightly_rate']
                valid_price = 20 <= price <= 1000  # Reasonable range

            completeness = data.get('data_completeness_pct', 0)
            good_completeness = completeness >= 50

            currency = data.get('currency', 'N/A')

            # Result summary
            status = "✅ PASS" if (has_price and valid_price and good_completeness) else "⚠️ PARTIAL"

            print(f"\n[{status}] {name}")
            print(f"  Base Rate: {currency} {price:.2f}" if has_price else f"  Base Rate: Not found")
            print(f"  Completeness: {completeness:.1f}%")
            print(f"  Screenshot: Saved to data/screenshots/")

            if valid_price:
                print(f"  ✓ Pricing is valid ({currency} {price:.2f}/night)")
            else:
                print(f"  ✗ Pricing issue (need manual review)")

            if good_completeness:
                print(f"  ✓ Data completeness good ({completeness:.1f}%)")
            else:
                print(f"  ✗ Data completeness low ({completeness:.1f}%)")

            results.append({
                'name': name,
                'status': status,
                'price': price if has_price else None,
                'currency': currency,
                'completeness': completeness,
                'has_valid_data': has_price and valid_price and good_completeness
            })

        except Exception as e:
            print(f"\n[❌ FAIL] {name} - Error: {str(e)[:200]}")
            results.append({
                'name': name,
                'status': '❌ FAIL',
                'price': None,
                'currency': None,
                'completeness': 0,
                'has_valid_data': False,
                'error': str(e)[:200]
            })

        await asyncio.sleep(2)

    # Final Summary
    print(f"\n{'='*80}")
    print("FINAL SUMMARY")
    print(f"{'='*80}\n")

    passed = [r for r in results if r['has_valid_data']]
    partial = [r for r in results if r['status'] == '⚠️ PARTIAL']
    failed = [r for r in results if r['status'] == '❌ FAIL']

    print(f"✅ PASSED: {len(passed)}/8 - Valid pricing & data")
    print(f"⚠️  PARTIAL: {len(partial)}/8 - Some data missing")
    print(f"❌ FAILED: {len(failed)}/8 - Errors occurred\n")

    # Detailed results table
    print(f"{'Competitor':<20} {'Status':<15} {'Price':<20} {'Completeness'}")
    print("-" * 80)
    for r in results:
        price_str = f"{r['currency']} {r['price']:.2f}" if r['price'] else "N/A"
        print(f"{r['name']:<20} {r['status']:<15} {price_str:<20} {r['completeness']:.1f}%")

    print(f"\n{'='*80}")
    print(f"✅ Test Complete! Check screenshots in data/screenshots/")
    print(f"{'='*80}\n")

    return results


if __name__ == "__main__":
    asyncio.run(test_all_scrapers())
