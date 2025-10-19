"""
Comprehensive test of all websites - Check each one individually
"""
import asyncio
import sys
from scrapers.tier1_scrapers import (
    RoadsurferScraper, McRentScraper, GoboonyScraper,
    YescapaScraper, CamperdaysScraper, OutdoorsyScraper,
    RVshareScraper, CruiseAmericaScraper
)

async def test_single_scraper(scraper, name):
    """Test a single scraper"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"{'='*70}")
    
    try:
        result = await scraper.scrape()
        
        price = result.get('base_nightly_rate', 0)
        completeness = result.get('data_completeness_pct', 0)
        method = result.get('extraction_method', 'N/A')
        estimated = result.get('is_estimated', True)
        
        print(f"[PASS] SUCCESS")
        print(f"   Price: EUR/USD {price}")
        print(f"   Method: {method}")
        print(f"   Estimated: {estimated}")
        print(f"   Completeness: {completeness:.1f}%")
        print(f"   Reviews: {result.get('review_count', 'N/A')}")
        print(f"   Fleet: {result.get('fleet_size_estimate', 'N/A')}")
        
        return True, result
        
    except Exception as e:
        print(f"[FAIL] FAILED: {str(e)[:100]}")
        import traceback
        traceback.print_exc()
        return False, None

async def main():
    """Test all scrapers"""
    print("\n" + "="*70)
    print("COMPREHENSIVE WEBSITE TEST - ALL COMPETITORS")
    print("="*70)
    
    scrapers_to_test = [
        (RoadsurferScraper(False), "Roadsurfer"),
        (McRentScraper(False), "McRent"),
        (GoboonyScraper(False), "Goboony"),
        (YescapaScraper(False), "Yescapa"),
        (CamperdaysScraper(False), "Camperdays"),
        (OutdoorsyScraper(False), "Outdoorsy"),
        (RVshareScraper(False), "RVshare"),
        (CruiseAmericaScraper(False), "Cruise America"),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for scraper, name in scrapers_to_test:
        success, data = await test_single_scraper(scraper, name)
        results.append((name, success, data))
        
        if success:
            passed += 1
        else:
            failed += 1
        
        # Brief delay between tests
        await asyncio.sleep(2)
    
    # Summary
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"\nTotal Tests: {len(scrapers_to_test)}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    print(f"Success Rate: {(passed/len(scrapers_to_test)*100):.1f}%")
    
    print("\n" + "-"*70)
    print("Detailed Results:")
    print("-"*70)
    
    for name, success, data in results:
        status = "[PASS]" if success else "[FAIL]"
        if success and data:
            price = data.get('base_nightly_rate', 0)
            complete = data.get('data_completeness_pct', 0)
            print(f"{status} | {name:20} | Price: ${price:6.2f} | Complete: {complete:5.1f}%")
        else:
            print(f"{status} | {name:20} | ERROR")
    
    print("\n" + "="*70)
    
    if failed == 0:
        print("[SUCCESS] ALL TESTS PASSED!")
    else:
        print(f"[WARNING] {failed} test(s) failed - needs attention")
    
    print("="*70 + "\n")
    
    return passed == len(scrapers_to_test)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

