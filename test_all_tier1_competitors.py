"""
Comprehensive Test Suite for All Tier 1 Competitors
Tests all 5 Tier 1 scrapers with detailed validation
"""

import asyncio
import sys
from scrapers.tier1_scrapers import (
    RoadsurferScraper,
    McRentScraper,
    GoboonyScraper,
    YescapaScraper,
    CamperdaysScraper
)
from monitoring.metrics_collector import get_metrics


async def test_competitor(scraper_class, competitor_name):
    """Test a single competitor scraper"""
    print(f"\n{'='*60}")
    print(f"TESTING: {competitor_name}")
    print(f"{'='*60}")

    try:
        scraper = scraper_class(use_browserless=False)
        result = await scraper.scrape()

        # Validate results
        validations = {
            'Price Extracted': result.get('base_nightly_rate') and result['base_nightly_rate'] > 0,
            'Review Rating': result.get('customer_review_avg') is not None,
            'Locations Found': result.get('locations_available') and len(result['locations_available']) > 0,
            'Data Completeness': result.get('data_completeness_pct', 0) > 40,
            'Vehicle Types': result.get('vehicle_types_count', 0) > 0,
        }

        # Print results
        print(f"\nResults for {competitor_name}:")
        print(f"  Price: EUR{result.get('base_nightly_rate', 0)}/night")
        print(f"  Review Rating: {result.get('customer_review_avg', 'None')} stars")
        print(f"  Review Count: {result.get('review_count', 'None')}")
        print(f"  Locations: {len(result.get('locations_available', []))} found")
        print(f"  Vehicle Types: {result.get('vehicle_types_count', 0)}")
        print(f"  Data Completeness: {result.get('data_completeness_pct', 0):.1f}%")

        print(f"\nValidation Results:")
        passed = 0
        failed = 0
        for check, status in validations.items():
            status_str = "[PASS]" if status else "[FAIL]"
            print(f"  {status_str} {check}")
            if status:
                passed += 1
            else:
                failed += 1

        overall_success = passed >= 3  # At least 3/5 checks should pass
        status_str = "[PASS]" if overall_success else "[FAIL]"
        print(f"\n{status_str} {competitor_name}: {passed}/5 validations passed")

        return {
            'competitor': competitor_name,
            'success': overall_success,
            'passed': passed,
            'failed': failed,
            'price': result.get('base_nightly_rate', 0),
            'reviews': result.get('customer_review_avg'),
            'locations': len(result.get('locations_available', [])),
            'completeness': result.get('data_completeness_pct', 0),
            'duration': result.get('scraping_duration_seconds', 0),
        }

    except Exception as e:
        print(f"\n[FAIL] {competitor_name} - Exception: {str(e)}")
        return {
            'competitor': competitor_name,
            'success': False,
            'passed': 0,
            'failed': 5,
            'error': str(e),
        }


async def main():
    """Test all Tier 1 competitors"""
    print("[TARGET] Focused Intelligence Scrapers v2.0.0")
    print("   15 competitors - 35 data points each\n")

    print("="*60)
    print("TIER 1 COMPETITORS END-TO-END TEST SUITE")
    print("="*60)
    print("\nTesting 5 Tier 1 competitors with comprehensive validation")
    print("This will take approximately 2-3 minutes...\n")

    # Define competitors to test
    competitors = [
        (RoadsurferScraper, "Roadsurfer"),
        (McRentScraper, "McRent"),
        (GoboonyScraper, "Goboony"),
        (YescapaScraper, "Yescapa"),
        (CamperdaysScraper, "Camperdays"),
    ]

    # Test each competitor sequentially
    results = []
    for scraper_class, name in competitors:
        result = await test_competitor(scraper_class, name)
        results.append(result)

        # Short delay between tests
        await asyncio.sleep(2)

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    successful = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"\nCompetitors Tested: {total}")
    print(f"Successful: {successful}/{total}")
    print(f"Failed: {total - successful}/{total}")
    print(f"Success Rate: {(successful/total)*100:.1f}%")

    # Detailed summary table
    print(f"\n{'Competitor':<15} {'Pass':<6} {'Price':<10} {'Reviews':<10} {'Locations':<12} {'Complete':<12}")
    print("-"*70)

    for result in results:
        status = "PASS" if result['success'] else "FAIL"
        price = f"EUR{result.get('price', 0)}" if result.get('price') else "N/A"
        reviews = f"{result.get('reviews', 'N/A')}" if result.get('reviews') else "N/A"
        locations = result.get('locations', 0)
        completeness = f"{result.get('completeness', 0):.1f}%"

        print(f"{result['competitor']:<15} {status:<6} {price:<10} {reviews:<10} {locations:<12} {completeness:<12}")

    # Metrics summary
    print("\n" + "="*60)
    print("METRICS SUMMARY")
    print("="*60)

    metrics = get_metrics()
    summary = metrics.get_summary()

    print(f"\nTotal Scrapes: {summary['scrapes_total']}")
    print(f"Successful: {summary['scrapes_successful']}")
    print(f"Failed: {summary['scrapes_failed']}")
    print(f"Success Rate: {summary['success_rate']*100:.1f}%")
    print(f"Avg Duration: {summary['avg_duration_seconds']:.1f}s")
    print(f"Price Extraction Rate: {summary['price_extraction_rate']*100:.1f}%")

    # Final verdict
    print("\n" + "="*60)

    if successful == total:
        print("[PASS] ALL TESTS PASSED! System ready for production.")
    elif successful >= total * 0.8:  # 80%+ success
        print("[PASS] Most tests passed. System ready with minor issues.")
    elif successful >= total * 0.6:  # 60%+ success
        print("[WARN] Some tests failed. Review failures before production.")
    else:
        print("[FAIL] Multiple tests failed. System needs fixes.")

    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest suite error: {e}")
        sys.exit(1)
