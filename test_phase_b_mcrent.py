"""
Test Phase B: McRent Booking Simulation
Verify that the booking simulation extracts REAL prices instead of estimates
"""

import asyncio
from scrapers.tier1_scrapers import McRentScraper
from loguru import logger


async def test_mcrent_booking_simulation():
    """Test Phase B: McRent booking simulation for real prices"""

    print("="*70)
    print("PHASE B: MC RENT BOOKING SIMULATION TEST")
    print("="*70)
    print("\nTesting booking simulation for REAL price extraction...")
    print("Expected: is_estimated = False, real price extracted from search results")
    print("="*70)

    try:
        # Create scraper
        scraper = McRentScraper(use_browserless=False)

        # Run scrape
        print("\nStarting McRent scrape with booking simulation...")
        result = await scraper.scrape()

        # Check results
        print("\n" + "="*70)
        print("RESULTS ANALYSIS")
        print("="*70)

        # 1. Price extraction
        print("\n1. PRICE EXTRACTION:")
        base_price = result.get('base_nightly_rate')
        is_estimated = result.get('is_estimated')
        print(f"   base_nightly_rate: EUR {base_price}")
        print(f"   is_estimated: {is_estimated}")

        if base_price and not is_estimated:
            print("   [PASS] PHASE B SUCCESS: REAL price extracted!")
        elif base_price and is_estimated:
            print("   [PARTIAL] Price extracted but still estimated (booking simulation failed)")
        else:
            print("   [FAIL] No price extracted")

        # 2. Vehicles available (bonus data from booking simulation)
        vehicles_available = result.get('vehicles_available')
        print(f"\n2. VEHICLES AVAILABLE (BONUS):")
        print(f"   vehicles_available: {vehicles_available}")
        if vehicles_available:
            print("   [PASS] Bonus data extracted from booking results")

        # 3. Overall completeness
        print("\n" + "="*70)
        print("OVERALL METRICS")
        print("="*70)
        completeness = result.get('data_completeness_pct', 0)
        print(f"Data Completeness: {completeness:.1f}%")
        print(f"Baseline: 58.5%")
        print(f"Target: 70%+")

        if completeness >= 70:
            print("[PASS] TARGET MET: McRent reached 70%+ completeness!")
        elif completeness >= 65:
            print("[PARTIAL] CLOSE: Approaching target, may need tweaks")
        elif completeness > 58.5:
            print("[PARTIAL] IMPROVED: Better than baseline but below target")
        else:
            print("[FAIL] NO IMPROVEMENT: Phase B needs debugging")

        # 4. Data quality check
        print("\n" + "="*70)
        print("DATA QUALITY CHECK")
        print("="*70)

        # Count real vs estimated fields
        estimated_fields = 0
        real_fields = 0

        key_fields = [
            'base_nightly_rate', 'insurance_cost_per_day', 'cleaning_fee',
            'weekly_discount_pct', 'monthly_discount_pct', 'mileage_limit_km',
            'fuel_policy', 'min_rental_days'
        ]

        print("\nKey Fields Status:")
        for field in key_fields:
            value = result.get(field)
            if value not in [None, '', [], 0]:
                print(f"  {field}: {value}")
                real_fields += 1
            else:
                print(f"  {field}: NOT EXTRACTED")

        print(f"\nReal Data Fields: {real_fields}/{len(key_fields)}")
        print(f"Is Estimated Flag: {is_estimated}")

        if not is_estimated and real_fields >= 6:
            print("[PASS] HIGH QUALITY: Real price + 6+ fields extracted")
        elif not is_estimated and real_fields >= 4:
            print("[PARTIAL] GOOD: Real price + 4+ fields extracted")
        else:
            print("[PARTIAL] NEEDS MORE WORK: More fields needed")

        # 5. Phase B specific success criteria
        print("\n" + "="*70)
        print("PHASE B SUCCESS CRITERIA")
        print("="*70)

        criteria_met = 0
        total_criteria = 3

        print("\n1. Real price extracted (not estimated)")
        if base_price and not is_estimated:
            print("   [PASS]")
            criteria_met += 1
        else:
            print("   [FAIL]")

        print("\n2. Completeness >= 65% (improvement from 58.5%)")
        if completeness >= 65:
            print("   [PASS]")
            criteria_met += 1
        else:
            print("   [FAIL]")

        print("\n3. At least 6+ key fields populated")
        if real_fields >= 6:
            print("   [PASS]")
            criteria_met += 1
        else:
            print("   [FAIL]")

        print(f"\nCriteria Met: {criteria_met}/{total_criteria}")

        if criteria_met == 3:
            print("\n[PASS] PHASE B: COMPLETE SUCCESS!")
        elif criteria_met == 2:
            print("\n[PARTIAL] PHASE B: PARTIAL SUCCESS")
        else:
            print("\n[FAIL] PHASE B: NEEDS MORE WORK")

        return result

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    try:
        asyncio.run(test_mcrent_booking_simulation())
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
    except Exception as e:
        print(f"\n\nTest failed: {e}")
