"""
Quick test script for critical fixes
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.tier1_scrapers import RoadsurferScraper
from scrapers.resilient_wrapper import ResilientScraper, RetryConfig
from loguru import logger


async def test_price_extraction():
    """Test price extraction"""
    print("\n" + "="*60)
    print("TEST 1: Price Extraction")
    print("="*60)

    scraper = RoadsurferScraper(use_browserless=False)
    result = await scraper.scrape()

    price = result.get('base_nightly_rate')

    if price and price > 0:
        print(f"[PASS] Price extracted = EUR{price}/night")
        return True
    else:
        print(f"[FAIL] Price = {price}")
        return False


async def test_review_extraction():
    """Test review extraction"""
    print("\n" + "="*60)
    print("TEST 2: Review Extraction")
    print("="*60)

    scraper = RoadsurferScraper(use_browserless=False)
    result = await scraper.scrape()

    rating = result.get('customer_review_avg')
    count = result.get('review_count')

    if rating or count:
        print(f"[PASS] Reviews = {rating} stars ({count} reviews)")
        return True
    else:
        print(f"[FAIL] No reviews found")
        return False


async def test_data_completeness():
    """Test data completeness"""
    print("\n" + "="*60)
    print("TEST 3: Data Completeness")
    print("="*60)

    scraper = RoadsurferScraper(use_browserless=False)
    result = await scraper.scrape()

    completeness = result.get('data_completeness_pct', 0)

    if completeness >= 50:
        print(f"[PASS] Completeness = {completeness:.1f}%")
        return True
    else:
        print(f"[PARTIAL] Completeness = {completeness:.1f}% (target: 60%)")
        return False


async def test_resilience():
    """Test retry logic"""
    print("\n" + "="*60)
    print("TEST 4: Resilience & Retry Logic")
    print("="*60)

    base_scraper = RoadsurferScraper(use_browserless=False)
    retry_config = RetryConfig(max_attempts=2)
    resilient_scraper = ResilientScraper(base_scraper, retry_config)

    try:
        result = await resilient_scraper.scrape_with_resilience()
        print(f"[PASS] Resilient scraping succeeded")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("CRITICAL FIXES TEST SUITE")
    print("="*60)

    tests = [
        test_price_extraction,
        test_review_extraction,
        test_data_completeness,
        test_resilience,
    ]

    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            results.append(False)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")

    if passed == total:
        print("\n[PASS] All tests passed! Ready for production.")
    elif passed >= total * 0.75:
        print("\n[WARN] Most tests passed. Minor fixes needed.")
    else:
        print("\n[FAIL] Many tests failed. More work needed.")

    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
