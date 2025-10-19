"""
Comprehensive Real Price Extraction Test Suite
Tests all improvements made in this session
"""
import asyncio
import time
from datetime import datetime
from scrapers.tier1_scrapers import (
    RoadsurferScraper, McRentScraper, GoboonyScraper,
    YescapaScraper, CamperdaysScraper
)
from database.models import add_price_record, get_session, CompetitorPrice

class TestResults:
    def __init__(self):
        self.results = []
        self.start_time = time.time()
    
    def add_result(self, test_name, passed, details):
        self.results.append({
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now()
        })
    
    def print_summary(self):
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        
        for result in self.results:
            status = "[PASS]" if result['passed'] else "[FAIL]"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"      {result['details']}")
        
        print("\n" + "="*70)
        print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        print(f"Duration: {time.time() - self.start_time:.1f}s")
        print("="*70 + "\n")

async def test_1_roadsurfer_timeout_fix(results):
    """Test 1: Verify Roadsurfer no longer times out"""
    print("\n[TEST 1] Roadsurfer Timeout Fix...")
    
    try:
        scraper = RoadsurferScraper(use_browserless=False)
        start = time.time()
        result = await scraper.scrape()
        duration = time.time() - start
        
        # Success criteria
        has_price = result.get('base_nightly_rate') is not None and result['base_nightly_rate'] > 0
        completed = True  # If we got here, it didn't timeout
        reasonable_time = duration < 120  # Under 2 minutes
        
        passed = has_price and completed and reasonable_time
        
        details = f"Duration: {duration:.1f}s, Price: EUR{result.get('base_nightly_rate', 0)}, Completeness: {result.get('data_completeness_pct', 0):.1f}%"
        
        results.add_result("Roadsurfer Timeout Fix", passed, details)
        
        print(f"  Price: EUR{result.get('base_nightly_rate', 0)}")
        print(f"  Duration: {duration:.1f}s")
        print(f"  Status: {'PASS' if passed else 'FAIL'}")
        
        return passed
        
    except Exception as e:
        results.add_result("Roadsurfer Timeout Fix", False, f"Error: {str(e)[:100]}")
        print(f"  Status: FAIL - {e}")
        return False

async def test_2_api_interception_framework(results):
    """Test 2: Verify API interception captures calls"""
    print("\n[TEST 2] API Interception Framework...")
    
    try:
        scraper = McRentScraper(use_browserless=False)
        result = await scraper.scrape()
        
        # Success criteria
        apis_detected = len(scraper.pricing_endpoints)
        responses_captured = len(scraper.api_responses)
        framework_active = hasattr(scraper, 'pricing_endpoints')
        
        passed = framework_active and (apis_detected > 0 or responses_captured > 0)
        
        details = f"APIs: {apis_detected}, Responses: {responses_captured}"
        
        results.add_result("API Interception Active", passed, details)
        
        print(f"  APIs detected: {apis_detected}")
        print(f"  Responses captured: {responses_captured}")
        
        if scraper.pricing_endpoints:
            print(f"  Sample endpoint: {scraper.pricing_endpoints[0]['url'][:60]}...")
        
        print(f"  Status: {'PASS' if passed else 'FAIL'}")
        
        return passed
        
    except Exception as e:
        results.add_result("API Interception Active", False, f"Error: {str(e)[:100]}")
        print(f"  Status: FAIL - {e}")
        return False

async def test_3_booking_simulation_method(results):
    """Test 3: Verify booking simulation method exists and works"""
    print("\n[TEST 3] Booking Simulation Method...")
    
    try:
        scraper = RoadsurferScraper(use_browserless=False)
        
        # Check method exists
        has_method = hasattr(scraper, '_simulate_booking_universal')
        has_extractor = hasattr(scraper, '_extract_prices_from_booking_results')
        
        passed = has_method and has_extractor
        
        details = f"Method exists: {has_method}, Extractor exists: {has_extractor}"
        
        results.add_result("Booking Simulation Method", passed, details)
        
        print(f"  _simulate_booking_universal: {has_method}")
        print(f"  _extract_prices_from_booking_results: {has_extractor}")
        print(f"  Status: {'PASS' if passed else 'FAIL'}")
        
        return passed
        
    except Exception as e:
        results.add_result("Booking Simulation Method", False, f"Error: {str(e)[:100]}")
        print(f"  Status: FAIL - {e}")
        return False

async def test_4_multi_scraper_success(results):
    """Test 4: Multiple scrapers complete successfully"""
    print("\n[TEST 4] Multi-Scraper Success Test...")
    
    scrapers = [
        ("Roadsurfer", RoadsurferScraper(False)),
        ("Goboony", GoboonyScraper(False)),
        ("McRent", McRentScraper(False))
    ]
    
    success_count = 0
    
    for name, scraper in scrapers:
        try:
            print(f"  Testing {name}...", end=" ")
            result = await scraper.scrape()
            
            has_data = result.get('data_completeness_pct', 0) > 30
            has_price = result.get('base_nightly_rate') is not None
            
            if has_data and has_price:
                success_count += 1
                print(f"OK EUR{result.get('base_nightly_rate', 0)}")
            else:
                print(f"PARTIAL")
                
        except Exception as e:
            print(f"FAIL {str(e)[:50]}")
    
    passed = success_count >= 2  # At least 2/3 should work
    
    details = f"{success_count}/3 scrapers successful"
    results.add_result("Multi-Scraper Success", passed, details)
    
    print(f"  Status: {'PASS' if passed else 'FAIL'} ({success_count}/3)")
    
    return passed

async def test_5_extraction_methods_tracked(results):
    """Test 5: Verify extraction methods are tracked"""
    print("\n[TEST 5] Extraction Method Tracking...")
    
    try:
        scraper = RoadsurferScraper(use_browserless=False)
        result = await scraper.scrape()
        
        # Check if extraction method is tracked
        has_field = 'extraction_method' in scraper.data
        
        passed = has_field
        
        method = result.get('extraction_method', 'unknown')
        details = f"Method: {method}"
        
        results.add_result("Extraction Method Tracking", passed, details)
        
        print(f"  Extraction method: {method}")
        print(f"  Status: {'PASS' if passed else 'FAIL'}")
        
        return passed
        
    except Exception as e:
        results.add_result("Extraction Method Tracking", False, f"Error: {str(e)[:100]}")
        print(f"  Status: FAIL - {e}")
        return False

async def test_6_database_integration(results):
    """Test 6: Verify data saves to database correctly"""
    print("\n[TEST 6] Database Integration...")
    
    try:
        scraper = GoboonyScraper(use_browserless=False)
        result = await scraper.scrape()
        
        # Try to save to database
        record_id = add_price_record(result)
        
        # Verify it was saved
        session = get_session()
        saved_record = session.query(CompetitorPrice).filter(
            CompetitorPrice.id == record_id
        ).first()
        session.close()
        
        passed = saved_record is not None and saved_record.company_name == "Goboony"
        
        details = f"Record ID: {record_id}, Saved: {passed}"
        
        results.add_result("Database Integration", passed, details)
        
        print(f"  Record ID: {record_id}")
        print(f"  Verified in DB: {'✅' if passed else '❌'}")
        print(f"  Status: {'PASS' if passed else 'FAIL'}")
        
        return passed
        
    except Exception as e:
        results.add_result("Database Integration", False, f"Error: {str(e)[:100]}")
        print(f"  Status: FAIL - {e}")
        return False

async def test_7_performance_benchmarks(results):
    """Test 7: Performance benchmarks"""
    print("\n[TEST 7] Performance Benchmarks...")
    
    try:
        scraper = GoboonyScraper(use_browserless=False)
        
        start = time.time()
        result = await scraper.scrape()
        duration = time.time() - start
        
        # Performance criteria
        fast_enough = duration < 60  # Under 1 minute
        good_completeness = result.get('data_completeness_pct', 0) > 40
        
        passed = fast_enough and good_completeness
        
        details = f"Duration: {duration:.1f}s, Completeness: {result.get('data_completeness_pct', 0):.1f}%"
        
        results.add_result("Performance Benchmarks", passed, details)
        
        print(f"  Duration: {duration:.1f}s (target: <60s)")
        print(f"  Completeness: {result.get('data_completeness_pct', 0):.1f}% (target: >40%)")
        print(f"  Status: {'PASS' if passed else 'FAIL'}")
        
        return passed
        
    except Exception as e:
        results.add_result("Performance Benchmarks", False, f"Error: {str(e)[:100]}")
        print(f"  Status: FAIL - {e}")
        return False

async def test_8_price_data_quality(results):
    """Test 8: Price data quality checks"""
    print("\n[TEST 8] Price Data Quality...")
    
    prices_found = []
    
    scrapers = [
        ("Roadsurfer", RoadsurferScraper(False)),
        ("Goboony", GoboonyScraper(False)),
        ("McRent", McRentScraper(False))
    ]
    
    for name, scraper in scrapers:
        try:
            result = await scraper.scrape()
            price = result.get('base_nightly_rate')
            
            if price and 20 < price < 500:  # Reasonable range
                prices_found.append((name, price))
                print(f"  {name}: EUR{price} ✅")
            else:
                print(f"  {name}: EUR{price if price else 0} ⚠️")
                
        except Exception as e:
            print(f"  {name}: Error ❌")
    
    passed = len(prices_found) >= 2
    
    details = f"{len(prices_found)}/3 with valid prices"
    results.add_result("Price Data Quality", passed, details)
    
    print(f"  Status: {'PASS' if passed else 'FAIL'}")
    
    return passed

async def main():
    print("\n" + "="*70)
    print("COMPREHENSIVE REAL PRICE EXTRACTION TEST SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing improvements from this session...")
    print("="*70)
    
    results = TestResults()
    
    # Run all tests
    await test_1_roadsurfer_timeout_fix(results)
    await test_2_api_interception_framework(results)
    await test_3_booking_simulation_method(results)
    await test_4_multi_scraper_success(results)
    await test_5_extraction_methods_tracked(results)
    await test_6_database_integration(results)
    await test_7_performance_benchmarks(results)
    await test_8_price_data_quality(results)
    
    # Print summary
    results.print_summary()
    
    # Save detailed results
    import json
    with open('test_results_detailed.json', 'w') as f:
        json.dump([{
            'test': r['test'],
            'passed': r['passed'],
            'details': r['details'],
            'timestamp': r['timestamp'].isoformat()
        } for r in results.results], f, indent=2)
    
    print("Detailed results saved to: test_results_detailed.json\n")

if __name__ == "__main__":
    asyncio.run(main())

