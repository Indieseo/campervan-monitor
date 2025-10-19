"""
Test all 8 Tier 1 scrapers (5 European + 3 US)
Complete global competitive intelligence test
"""

import asyncio
import sys
from scrapers.tier1_scrapers import (
    # European
    RoadsurferScraper, McRentScraper, GoboonyScrap,
    YescapaScraper, CamperdaysScraper,
    # US
    OutdoorsyScraper, RVshareScraper, CruiseAmericaScraper
)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def test_all():
    """Test all 8 scrapers (European + US)"""

    scrapers = [
        # European competitors
        RoadsurferScraper(use_browserless=False),
        GoboonyScrap(use_browserless=False),
        YescapaScraper(use_browserless=False),
        McRentScraper(use_browserless=False),
        CamperdaysScraper(use_browserless=False),
        # US competitors
        OutdoorsyScraper(use_browserless=False),
        RVshareScraper(use_browserless=False),
        CruiseAmericaScraper(use_browserless=False)
    ]

    print("\n" + "="*70)
    print("TESTING ALL 8 TIER 1 SCRAPERS (5 EUROPEAN + 3 US)")
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
            print(f"  Base Rate:        {data['currency']} {data['base_nightly_rate'] or 'N/A'}")
            print(f"  Reviews:          {data['customer_review_avg'] or 'N/A'} ({data['review_count'] or 'N/A'} reviews)")
            print(f"  Locations:        {len(data['locations_available']) if data['locations_available'] else 0}")
            print(f"  Fleet Size:       {data['fleet_size_estimate'] or 'N/A'}")
            print(f"  Insurance:        {data['currency']} {data['insurance_cost_per_day'] or 'N/A'}/day")
            print(f"  Cleaning Fee:     {data['currency']} {data['cleaning_fee'] or 'N/A'}")
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
            results.append({
                'company_name': scraper.company_name,
                'data_completeness_pct': 0,
                'notes': f"Error: {str(e)[:200]}"
            })

        # Small delay between scrapers
        await asyncio.sleep(2)

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY - ALL 8 SCRAPERS")
    print(f"{'='*70}\n")

    # Group by region
    print("EUROPEAN COMPETITORS:")
    european = [r for r in results if r['company_name'] in ['Roadsurfer', 'McRent', 'Goboony', 'Yescapa', 'Camperdays']]
    total_eur = 0
    above_60_eur = 0
    for data in european:
        pct = data.get('data_completeness_pct', 0)
        total_eur += pct
        status = "[OK]" if pct >= 60 else "[~]" if pct >= 50 else "[X]"
        print(f"  {status} {data['company_name']:15s} {pct:5.1f}% {'[TARGET MET]' if pct >= 60 else ''}")
        if pct >= 60:
            above_60_eur += 1

    avg_eur = total_eur / len(european) if european else 0
    print(f"\n  Average: {avg_eur:.1f}% | Above 60%: {above_60_eur}/{len(european)}")

    print("\nUS COMPETITORS:")
    us = [r for r in results if r['company_name'] in ['Outdoorsy', 'RVshare', 'Cruise America']]
    total_us = 0
    above_60_us = 0
    for data in us:
        pct = data.get('data_completeness_pct', 0)
        total_us += pct
        status = "[OK]" if pct >= 60 else "[~]" if pct >= 50 else "[X]"
        print(f"  {status} {data['company_name']:15s} {pct:5.1f}% {'[TARGET MET]' if pct >= 60 else ''}")
        if pct >= 60:
            above_60_us += 1

    avg_us = total_us / len(us) if us else 0
    print(f"\n  Average: {avg_us:.1f}% | Above 60%: {above_60_us}/{len(us)}")

    print(f"\n{'-'*70}")
    total_completeness = sum(data.get('data_completeness_pct', 0) for data in results)
    avg_completeness = total_completeness / len(results) if results else 0
    scrapers_above_60 = sum(1 for data in results if data.get('data_completeness_pct', 0) >= 60)

    print(f"GLOBAL AVERAGE:       {avg_completeness:.1f}%")
    print(f"Scrapers >= 60%:      {scrapers_above_60}/8 ({scrapers_above_60/8*100:.0f}%)")
    print(f"{'-'*70}")

    if scrapers_above_60 >= 6:
        print("\n[SUCCESS] 6+ scrapers at 60%+ (75% success rate)!")
    elif scrapers_above_60 >= 5:
        print("\n[GOOD] 5+ scrapers at 60%+ (62% success rate)")
    elif avg_completeness >= 60:
        print("\n[GOOD] Average above 60%!")
    else:
        print("\n[PROGRESS] Good progress, continue optimizing")

    print(f"\n{'='*70}")
    print("TEST COMPLETE - GLOBAL COVERAGE")
    print(f"{'='*70}\n")

    return results


if __name__ == "__main__":
    asyncio.run(test_all())
