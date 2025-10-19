"""
Test Phase A improvements
Verify that the quick wins are working:
1. vehicle_types_count -> popular_vehicle_type
2. review_count extraction improved
3. payment_options extraction enhanced
4. vehicle_features extraction enhanced
5. promotions extraction enhanced with discount extraction
"""

import asyncio
from scrapers.tier1_scrapers import RoadsurferScraper
from loguru import logger


async def test_phase_a_improvements():
    """Test Phase A improvements with Roadsurfer"""

    print("="*70)
    print("PHASE A: QUICK WINS TEST")
    print("="*70)
    print("\nTesting improvements with Roadsurfer scraper...")
    print("Expected improvements:")
    print("1. popular_vehicle_type populated from vehicle_types")
    print("2. review_count extracted alongside rating")
    print("3. payment_options: more methods detected")
    print("4. vehicle_features: better extraction from page sections")
    print("5. promotions: enhanced with discount % extraction")
    print("="*70)

    try:
        # Create scraper
        scraper = RoadsurferScraper(use_browserless=False)

        # Run scrape
        print("\nStarting scrape...")
        result = await scraper.scrape()

        # Check improvements
        print("\n" + "="*70)
        print("RESULTS ANALYSIS")
        print("="*70)

        # 1. Vehicle types
        print("\n1. VEHICLE TYPES:")
        vehicle_types = result.get('vehicle_types', [])
        popular_vehicle = result.get('popular_vehicle_type')
        print(f"   vehicle_types: {vehicle_types}")
        print(f"   popular_vehicle_type: {popular_vehicle}")
        if vehicle_types and popular_vehicle:
            print("   [PASS] IMPROVED: popular_vehicle_type populated from list")
        else:
            print("   [FAIL] NOT IMPROVED: Still missing data")

        # 2. Review count
        print("\n2. REVIEW DATA:")
        review_avg = result.get('customer_review_avg')
        review_count = result.get('review_count')
        print(f"   customer_review_avg: {review_avg}")
        print(f"   review_count: {review_count}")
        if review_avg and review_count:
            print("   [PASS] IMPROVED: Both rating AND count extracted")
        elif review_avg:
            print("   [PARTIAL] Rating extracted but count still missing")
        else:
            print("   [FAIL] NOT IMPROVED: No review data")

        # 3. Payment options
        print("\n3. PAYMENT OPTIONS:")
        payment_options = result.get('payment_options', [])
        print(f"   payment_options: {payment_options}")
        if len(payment_options) >= 3:
            print(f"   [PASS] IMPROVED: {len(payment_options)} payment methods detected")
        elif len(payment_options) > 0:
            print(f"   [PARTIAL] {len(payment_options)} payment methods (expected 3+)")
        else:
            print("   [FAIL] NOT IMPROVED: No payment options detected")

        # 4. VEHICLE FEATURES:")
        print("\n4. VEHICLE FEATURES:")
        vehicle_features = result.get('vehicle_features', [])
        print(f"   vehicle_features: {vehicle_features}")
        if len(vehicle_features) >= 5:
            print(f"   [PASS] IMPROVED: {len(vehicle_features)} features extracted")
        elif len(vehicle_features) > 0:
            print(f"   [PARTIAL] {len(vehicle_features)} features (expected 5+)")
        else:
            print("   [FAIL] NOT IMPROVED: No features extracted")

        # 5. Promotions and discounts
        print("\n5. PROMOTIONS:")
        active_promotions = result.get('active_promotions', [])
        promotion_text = result.get('promotion_text')
        discount_code_available = result.get('discount_code_available')
        early_bird = result.get('early_bird_discount_pct')
        weekly = result.get('weekly_discount_pct')
        monthly = result.get('monthly_discount_pct')

        print(f"   active_promotions: {len(active_promotions)} found")
        if len(active_promotions) > 0:
            for i, promo in enumerate(active_promotions[:3], 1):
                promo_type = promo.get('type', 'unknown')
                promo_discount = promo.get('discount_pct', 'N/A')
                promo_text = promo.get('text', '')[:50] + '...'
                print(f"     {i}. Type: {promo_type}, Discount: {promo_discount}%, Text: {promo_text}")

        print(f"   promotion_text: {promotion_text}")
        print(f"   discount_code_available: {discount_code_available}")
        print(f"   early_bird_discount_pct: {early_bird}")
        print(f"   weekly_discount_pct: {weekly}")
        print(f"   monthly_discount_pct: {monthly}")

        if len(active_promotions) > 0:
            print("   [PASS] IMPROVED: Promotions detected with enhanced data")
        else:
            print("   [FAIL] NOT IMPROVED: No promotions found")

        # Overall completeness
        print("\n" + "="*70)
        print("OVERALL METRICS")
        print("="*70)
        completeness = result.get('data_completeness_pct', 0)
        print(f"Data Completeness: {completeness:.1f}%")
        print(f"Expected Target: 55% (baseline) -> 58%+ (with improvements)")

        if completeness >= 58:
            print("[PASS] TARGET MET: Completeness improved by Phase A changes")
        elif completeness >= 55:
            print("[PARTIAL] CLOSE: Some improvement, may need more work")
        else:
            print("[FAIL] BELOW TARGET: Phase A improvements need debugging")

        # Count populated fields in target categories
        improvements = 0
        if popular_vehicle: improvements += 1
        if review_count: improvements += 1
        if len(payment_options) >= 3: improvements += 1
        if len(vehicle_features) >= 5: improvements += 1
        if len(active_promotions) > 0: improvements += 1

        print(f"\nPhase A Improvements Applied: {improvements}/5")

        if improvements >= 4:
            print("[PASS] PHASE A: SUCCESSFUL")
        elif improvements >= 2:
            print("[PARTIAL] PHASE A: PARTIAL SUCCESS")
        else:
            print("[FAIL] PHASE A: NEEDS MORE WORK")

        return result

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    try:
        asyncio.run(test_phase_a_improvements())
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
    except Exception as e:
        print(f"\n\nTest failed: {e}")
