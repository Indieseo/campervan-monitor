"""
Comprehensive Test Script for All Scraper Improvements

This script tests all 5 Tier 1 scrapers and generates a detailed report.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from loguru import logger

# Add parent directory to path
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from scrapers.tier1_scrapers import (
    RoadsurferScraper,
    McRentScraper,
    GoboonyScrap,
    YescapaScraper,
    CamperdaysScraper
)
from database.models import add_price_record, get_session, CompetitorPrice


async def test_single_scraper(scraper_class, use_browserless=False):
    """Test a single scraper and return detailed results"""
    scraper = scraper_class(use_browserless=use_browserless)
    company = scraper.company_name

    logger.info(f"\n{'='*60}")
    logger.info(f"Testing: {company}")
    logger.info(f"{'='*60}")

    try:
        start_time = datetime.now()

        # Add timeout protection (5 minutes max per scraper)
        try:
            data = await asyncio.wait_for(scraper.scrape(), timeout=300.0)
        except asyncio.TimeoutError:
            logger.error(f"❌ {company} timed out after 5 minutes")
            return {
                'company': company,
                'success': False,
                'error': 'Timeout after 5 minutes',
                'issues': [f"❌ CRITICAL: Scraper timed out - may need optimization"]
            }

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Analyze results
        results = {
            'company': company,
            'success': True,
            'duration': duration,
            'data': {
                'base_nightly_rate': data.get('base_nightly_rate', 0),
                'is_estimated': data.get('is_estimated', True),
                'customer_review_avg': data.get('customer_review_avg'),
                'review_count': data.get('review_count'),
                'locations_count': len(data.get('locations_available', [])),
                'insurance_cost': data.get('insurance_cost_per_day'),
                'cleaning_fee': data.get('cleaning_fee'),
                'booking_fee': data.get('booking_fee'),
                'fuel_policy': data.get('fuel_policy'),
                'cancellation_policy': data.get('cancellation_policy'),
                'promotions_count': len(data.get('active_promotions', [])),
                'completeness': data.get('data_completeness_pct', 0)
            },
            'issues': []
        }

        # Check for issues
        price = results['data']['base_nightly_rate']
        if price is None or price == 0:
            results['issues'].append("❌ Price is €0 or None (extraction failed)")
        elif price < 20 or price > 500:
            results['issues'].append(f"⚠️  Price seems unusual: €{price}")

        if results['data']['customer_review_avg'] is None:
            results['issues'].append("⚠️  No reviews extracted")

        if results['data']['locations_count'] == 0:
            results['issues'].append("⚠️  No locations found")
        elif results['data']['locations_count'] < 3:
            results['issues'].append(f"⚠️  Only {results['data']['locations_count']} location(s) found")

        if results['data']['completeness'] < 40:
            results['issues'].append(f"❌ Completeness too low: {results['data']['completeness']:.1f}%")
        elif results['data']['completeness'] < 60:
            results['issues'].append(f"⚠️  Completeness below target: {results['data']['completeness']:.1f}%")

        # Save to database
        try:
            add_price_record(data)
            logger.info(f"✅ Saved to database")
        except Exception as e:
            logger.error(f"❌ Database save failed: {e}")
            results['issues'].append(f"Database save failed: {e}")

        return results

    except KeyboardInterrupt:
        logger.warning(f"⚠️  {company} interrupted by user")
        raise  # Re-raise to stop entire test suite
    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        return {
            'company': company,
            'success': False,
            'error': str(e),
            'issues': [f"❌ CRITICAL: Scraping crashed - {e}"]
        }


async def run_all_tests(use_browserless=False):
    """Run tests on all 5 Tier 1 scrapers"""
    print("\n" + "="*80)
    print("COMPREHENSIVE SCRAPER TEST SUITE")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'Browserless' if use_browserless else 'Local Browser'}")
    print("="*80 + "\n")

    scrapers = [
        RoadsurferScraper,
        McRentScraper,
        GoboonyScrap,
        YescapaScraper,
        CamperdaysScraper
    ]

    results = []
    for scraper_class in scrapers:
        result = await test_single_scraper(scraper_class, use_browserless)
        results.append(result)
        await asyncio.sleep(2)  # Respectful delay

    return results


def generate_report(results):
    """Generate comprehensive test report"""
    report = []
    report.append("\n" + "="*80)
    report.append("TEST RESULTS SUMMARY")
    report.append("="*80)

    # Overall stats
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    report.append(f"\nTotal Scrapers: {len(results)}")
    report.append(f"Successful: {successful} ({successful/len(results)*100:.0f}%)")
    report.append(f"Failed: {failed}")

    # Individual results
    report.append("\n" + "-"*80)
    report.append("INDIVIDUAL SCRAPER RESULTS")
    report.append("-"*80)

    for result in results:
        company = result['company']
        report.append(f"\n{company}:")

        if not result['success']:
            report.append(f"  ❌ FAILED: {result.get('error', 'Unknown error')}")
            continue

        data = result['data']
        report.append(f"  Duration: {result['duration']:.1f}s")

        price = data['base_nightly_rate']
        if price is not None and price > 0:
            report.append(f"  Price: EUR{price:.2f}/night {'(estimated)' if data['is_estimated'] else '(real)'}")
        else:
            report.append(f"  Price: None (extraction failed)")

        if data['customer_review_avg']:
            report.append(f"  Reviews: {data['customer_review_avg']}★ ({data['review_count'] or '?'} reviews)")
        else:
            report.append(f"  Reviews: None")

        report.append(f"  Locations: {data['locations_count']} found")

        if data['insurance_cost']:
            report.append(f"  Insurance: €{data['insurance_cost']}/day")
        if data['cleaning_fee']:
            report.append(f"  Cleaning: €{data['cleaning_fee']}")
        if data['fuel_policy']:
            report.append(f"  Fuel Policy: {data['fuel_policy']}")

        report.append(f"  Completeness: {data['completeness']:.1f}%")

        if result['issues']:
            report.append(f"  Issues:")
            for issue in result['issues']:
                report.append(f"    {issue}")

    # Aggregate metrics
    report.append("\n" + "-"*80)
    report.append("AGGREGATE METRICS")
    report.append("-"*80)

    successful_results = [r for r in results if r['success']]

    if successful_results:
        prices = [r['data']['base_nightly_rate'] for r in successful_results if r['data']['base_nightly_rate'] > 0]
        completeness = [r['data']['completeness'] for r in successful_results]
        reviews = [r for r in successful_results if r['data']['customer_review_avg'] is not None]
        locations = [r['data']['locations_count'] for r in successful_results]

        report.append(f"\nPrice Extraction:")
        report.append(f"  Working: {len(prices)}/{len(successful_results)} ({len(prices)/len(successful_results)*100:.0f}%)")
        if prices:
            report.append(f"  Average: €{sum(prices)/len(prices):.2f}/night")
            report.append(f"  Range: €{min(prices):.2f} - €{max(prices):.2f}")

        report.append(f"\nReview Extraction:")
        report.append(f"  Working: {len(reviews)}/{len(successful_results)} ({len(reviews)/len(successful_results)*100:.0f}%)")

        report.append(f"\nLocation Extraction:")
        if locations:
            report.append(f"  Average: {sum(locations)/len(locations):.1f} locations per scraper")
            report.append(f"  Best: {max(locations)} locations")

        report.append(f"\nData Completeness:")
        report.append(f"  Average: {sum(completeness)/len(completeness):.1f}%")
        report.append(f"  Best: {max(completeness):.1f}%")
        report.append(f"  Worst: {min(completeness):.1f}%")

    # Target assessment
    report.append("\n" + "-"*80)
    report.append("TARGET ASSESSMENT")
    report.append("-"*80)

    if successful_results:
        avg_completeness = sum(r['data']['completeness'] for r in successful_results) / len(successful_results)
        price_working = len([r for r in successful_results if r['data']['base_nightly_rate'] and r['data']['base_nightly_rate'] > 0])
        review_working = len([r for r in successful_results if r['data']['customer_review_avg'] is not None])

        report.append(f"\n✅ = Met target, ⚠️  = Partial, ❌ = Not met")
        report.append(f"\nPrice Extraction: {'✅' if price_working >= 4 else '⚠️' if price_working >= 2 else '❌'} {price_working}/5 working (target: 4/5)")
        report.append(f"Review Extraction: {'✅' if review_working >= 3 else '⚠️' if review_working >= 1 else '❌'} {review_working}/5 working (target: 3/5)")
        report.append(f"Data Completeness: {'✅' if avg_completeness >= 60 else '⚠️' if avg_completeness >= 50 else '❌'} {avg_completeness:.1f}% (target: 60%+)")

        # Overall verdict
        report.append("\n" + "="*80)
        if price_working >= 4 and review_working >= 3 and avg_completeness >= 60:
            report.append("VERDICT: ✅ ALL TARGETS MET - PRODUCTION READY")
        elif price_working >= 3 and avg_completeness >= 50:
            report.append("VERDICT: ⚠️  PARTIAL SUCCESS - Needs minor improvements")
        else:
            report.append("VERDICT: ❌ NEEDS MORE WORK - Critical issues remain")
        report.append("="*80)

    return "\n".join(report)


async def main():
    """Main execution"""
    # Parse command line arguments
    use_browserless = '--browserless' in sys.argv

    # Run tests
    results = await run_all_tests(use_browserless)

    # Generate and print report
    report = generate_report(results)
    print(report)

    # Save report to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = BASE_DIR / f"TEST_REPORT_{timestamp}.txt"
    report_path.write_text(report, encoding='utf-8')
    print(f"\n📄 Report saved to: {report_path}")

    # Print recent database records
    print("\n" + "="*80)
    print("RECENT DATABASE RECORDS")
    print("="*80)

    try:
        session = get_session()
        recent = session.query(CompetitorPrice).order_by(
            CompetitorPrice.scrape_timestamp.desc()
        ).limit(5).all()

        for record in recent:
            print(f"\n{record.company_name}:")
            print(f"  Timestamp: {record.scrape_timestamp}")
            print(f"  Price: €{record.base_nightly_rate}/night")
            print(f"  Reviews: {record.customer_review_avg}★")
            print(f"  Completeness: {record.data_completeness_pct:.1f}%")

        session.close()
    except Exception as e:
        print(f"❌ Could not read database: {e}")

    print("\n✅ Test suite complete!")


if __name__ == "__main__":
    asyncio.run(main())
