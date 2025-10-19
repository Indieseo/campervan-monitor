"""
Master Test Runner
Runs all test suites and generates comprehensive report
"""

import unittest
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

# Import all test modules
from tests import test_database_models
from tests import test_scrapers
from tests import test_integration


def run_all_test_suites():
    """
    Run all test suites and generate comprehensive report
    
    Returns:
        bool: True if all tests passed, False otherwise
    """
    print("\n" + "=" * 80)
    print(" 🧪 CAMPERVAN INTELLIGENCE SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"📅 Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")
    
    # Track overall results
    all_results = {}
    start_time = time.time()
    
    # Test Suite 1: Database Models
    print("\n" + "▶" * 40)
    print("📊 RUNNING DATABASE MODELS TESTS")
    print("▶" * 40 + "\n")
    db_start = time.time()
    db_success = test_database_models.run_all_tests()
    db_duration = time.time() - db_start
    all_results['Database Models'] = {
        'success': db_success,
        'duration': db_duration
    }
    
    # Test Suite 2: Scrapers
    print("\n" + "▶" * 40)
    print("🔍 RUNNING SCRAPER TESTS")
    print("▶" * 40 + "\n")
    scraper_start = time.time()
    scraper_success = test_scrapers.run_all_tests()
    scraper_duration = time.time() - scraper_start
    all_results['Scrapers'] = {
        'success': scraper_success,
        'duration': scraper_duration
    }
    
    # Test Suite 3: Integration
    print("\n" + "▶" * 40)
    print("🔗 RUNNING INTEGRATION TESTS")
    print("▶" * 40 + "\n")
    integration_start = time.time()
    integration_success = test_integration.run_all_tests()
    integration_duration = time.time() - integration_start
    all_results['Integration'] = {
        'success': integration_success,
        'duration': integration_duration
    }
    
    # Calculate total time
    total_duration = time.time() - start_time
    
    # Print comprehensive summary
    print("\n" + "=" * 80)
    print(" 📋 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80 + "\n")
    
    all_passed = True
    for suite_name, result in all_results.items():
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"{suite_name:.<40} {status} ({result['duration']:.2f}s)")
        if not result['success']:
            all_passed = False
    
    print("\n" + "-" * 80)
    print(f"Total Test Duration: {total_duration:.2f} seconds")
    print("-" * 80)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The system is ready for deployment.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please review the failed tests above and fix the issues.")
    
    print("\n" + "=" * 80 + "\n")
    
    return all_passed


def run_specific_suite(suite_name: str):
    """
    Run a specific test suite
    
    Args:
        suite_name: Name of the suite ('database', 'scrapers', or 'integration')
    
    Returns:
        bool: True if tests passed, False otherwise
    """
    suite_map = {
        'database': test_database_models.run_all_tests,
        'scrapers': test_scrapers.run_all_tests,
        'integration': test_integration.run_all_tests
    }
    
    if suite_name.lower() not in suite_map:
        print(f"❌ Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(suite_map.keys())}")
        return False
    
    print(f"\n🧪 Running {suite_name.upper()} tests...\n")
    return suite_map[suite_name.lower()]()


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Run specific suite
        suite_name = sys.argv[1]
        success = run_specific_suite(suite_name)
    else:
        # Run all suites
        success = run_all_test_suites()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()


