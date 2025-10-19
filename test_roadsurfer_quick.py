"""Quick test of Roadsurfer scraper enhancements"""
import asyncio
import sys
from scrapers.tier1_scrapers import RoadsurferScraper

async def test_roadsurfer():
    print("\n" + "="*60)
    print("TESTING ROADSURFER SCRAPER")
    print("="*60 + "\n")

    scraper = RoadsurferScraper(use_browserless=False)
    data = await scraper.scrape()

    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Company: {data['company_name']}")
    print(f"Base Rate: EUR {data['base_nightly_rate']}")
    print(f"Review Avg: {data['customer_review_avg']}")
    print(f"Review Count: {data['review_count']}")
    print(f"Insurance/day: EUR {data['insurance_cost_per_day']}")
    print(f"Cleaning Fee: EUR {data['cleaning_fee']}")
    print(f"Booking Fee: EUR {data['booking_fee']}")
    print(f"Locations: {len(data['locations_available'])} found")
    if data['locations_available']:
        print(f"  Sample: {data['locations_available'][:3]}")
    print(f"Fleet Size: {data['fleet_size_estimate']}")
    print(f"Vehicle Types: {len(data['vehicle_types'])}")
    if data['vehicle_types']:
        print(f"  Sample: {data['vehicle_types'][:2]}")
    print(f"Promotions: {len(data['active_promotions'])}")
    print(f"Fuel Policy: {data['fuel_policy']}")
    print(f"Cancellation: {data['cancellation_policy']}")
    print(f"Min Rental Days: {data['min_rental_days']}")
    print(f"Payment Options: {len(data['payment_options'])}")
    print(f"\nData Completeness: {data['data_completeness_pct']:.1f}%")
    print(f"Is Estimated: {data['is_estimated']}")
    print("="*60)

    # Check success criteria
    print("\n" + "="*60)
    print("SUCCESS CRITERIA CHECK")
    print("="*60)

    success_count = 0
    total_checks = 0

    # Price check
    total_checks += 1
    if data['base_nightly_rate'] and data['base_nightly_rate'] > 0:
        print("[PASS] Price extraction: EUR {}".format(data['base_nightly_rate']))
        success_count += 1
    else:
        print("[FAIL] Price extraction: EUR 0 or None")

    # Reviews check
    total_checks += 1
    if data['customer_review_avg'] or data['review_count']:
        print("[PASS] Review extraction: {} / {} reviews".format(
            data['customer_review_avg'], data['review_count']))
        success_count += 1
    else:
        print("[FAIL] Review extraction: No reviews found")

    # Completeness check
    total_checks += 1
    if data['data_completeness_pct'] >= 60:
        print("[PASS] Data completeness: {:.1f}% >= 60%".format(
            data['data_completeness_pct']))
        success_count += 1
    elif data['data_completeness_pct'] >= 50:
        print("[PARTIAL] Data completeness: {:.1f}% >= 50%".format(
            data['data_completeness_pct']))
        success_count += 0.5
    else:
        print("[FAIL] Data completeness: {:.1f}% < 50%".format(
            data['data_completeness_pct']))

    # Locations check
    total_checks += 1
    if len(data['locations_available']) >= 5:
        print("[PASS] Location extraction: {} locations".format(
            len(data['locations_available'])))
        success_count += 1
    else:
        print("[FAIL] Location extraction: {} locations".format(
            len(data['locations_available'])))

    # Insurance/fees check
    total_checks += 1
    if data['insurance_cost_per_day'] or data['cleaning_fee'] or data['booking_fee']:
        print("[PASS] Fee extraction: at least one fee found")
        success_count += 1
    else:
        print("[FAIL] Fee extraction: no fees found")

    print("\n" + "="*60)
    print("OVERALL: {}/{} checks passed ({:.0f}%)".format(
        success_count, total_checks, (success_count/total_checks)*100))
    print("="*60)

    return data

if __name__ == "__main__":
    asyncio.run(test_roadsurfer())
