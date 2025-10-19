"""
Test all 5 enhanced Tier 1 scrapers
Tests improvements to Camperdays, Yescapa, and McRent
"""

import asyncio
import sys
from scrapers.tier1_scrapers import (
    RoadsurferScraper, McRentScraper, GoboonyScrap,
    YescapaScraper, CamperdaysScraper
)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def test_all():
    """Test all 5 scrapers with local browsers"""

    scrapers = [
        RoadsurferScraper(use_browserless=False),
        GoboonyScrap(use_browserless=False),
        YescapaScraper(use_browserless=False),
        McRentScraper(use_browserless=False),
        CamperdaysScraper(use_browserless=False)
    ]

    print("\n" + "="*70)
    print("TESTING ALL 5 ENHANCED TIER 1 SCRAPERS")
    print("="*70)

    results = []

    for scraper in scrapers:
        print(f"\n{'='*70}")
        print(f"Testing {scraper.company_name}...")
        print('='*70)

        try:
            data = await scraper.scrape()
            results.append(data)

            # Display key metrics
            print(f"\n[OK] {scraper.company_name} - COMPLETE")
            print(f"{'-'*70}")
            print(f"  Base Rate:        €{data['base_nightly_rate'] or 'N/A'}")
            print(f"  Reviews:          {data['customer_review_avg'] or 'N/A'}★ ({data['review_count'] or 'N/A'} reviews)")
            print(f"  Locations:        {len(data['locations_available']) if data['locations_available'] else 0}")
            print(f"  Fleet Size:       {data['fleet_size_estimate'] or 'N/A'}")
            print(f"  Insurance:        €{data['insurance_cost_per_day'] or 'N/A'}/day")
            print(f"  Cleaning Fee:     €{data['cleaning_fee'] or 'N/A'}")
            print(f"  Mileage:          {data['mileage_limit_km'] if data['mileage_limit_km'] is not None else 'N/A'} km/day")
            print(f"  One-way:          {'Yes' if data['one_way_rental_allowed'] else 'No'}")
            print(f"  Referral:         {'Yes' if data['referral_program'] else 'No'}")
            print(f"  Discount Codes:   {'Yes' if data['discount_code_available'] else 'No'}")
            print(f"  Payment Options:  {len(data['payment_options'])} methods")
            print(f"  Fuel Policy:      {data['fuel_policy'] or 'N/A'}")
            print(f"  Cancellation:     {data['cancellation_policy'] or 'N/A'}")
            print(f"  {'-'*70}")
            print(f"  Data Completeness: {data['data_completeness_pct']:.1f}%")
            if data.get('is_estimated'):
                print(f"  Note: Some data estimated")
            if data.get('notes'):
                print(f"  Notes: {data['notes']}")

        except Exception as e:
            print(f"\n[FAIL] {scraper.company_name} - FAILED")
            print(f"  Error: {str(e)[:200]}")
            # Still add to results with error
            results.append({
                'company_name': scraper.company_name,
                'data_completeness_pct': 0,
                'notes': f"Error: {str(e)[:200]}"
            })

        # Small delay between scrapers
        await asyncio.sleep(2)

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY - ALL SCRAPERS")
    print(f"{'='*70}\n")

    total_completeness = 0
    scrapers_above_60 = 0

    for data in results:
        pct = data.get('data_completeness_pct', 0)
        total_completeness += pct

        status = "[OK]" if pct >= 60 else "[~]" if pct >= 50 else "[X]"
        print(f"{status} {data['company_name']:15s} {pct:5.1f}% {'[TARGET MET]' if pct >= 60 else ''}")

        if pct >= 60:
            scrapers_above_60 += 1

    avg_completeness = total_completeness / len(results) if results else 0

    print(f"\n{'-'*70}")
    print(f"Average Completeness: {avg_completeness:.1f}%")
    print(f"Scrapers >= 60%:      {scrapers_above_60}/5")
    print(f"{'-'*70}")

    if scrapers_above_60 >= 3:
        print("\n[SUCCESS] 3+ scrapers at 60%+ completeness!")
    elif avg_completeness >= 55:
        print("\n[GOOD] Average above 55%")
    else:
        print("\n[WARN] More work needed to reach 60% average")

    print(f"\n{'='*70}")
    print("TEST COMPLETE")
    print(f"{'='*70}\n")

    return results


if __name__ == "__main__":
    asyncio.run(test_all())
