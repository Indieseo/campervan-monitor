"""
Analyze data completeness across all competitors
Identify gaps and missing fields for targeted improvement
"""

import asyncio
from scrapers.tier1_scrapers import (
    RoadsurferScraper,
    McRentScraper,
    GoboonyScraper,
    YescapaScraper,
    CamperdaysScraper
)


async def analyze_single_competitor(scraper_class, name):
    """Analyze one competitor's data completeness"""
    print(f"\n{'='*70}")
    print(f"ANALYZING: {name}")
    print(f"{'='*70}")

    try:
        scraper = scraper_class(use_browserless=False)
        result = await scraper.scrape()

        # Categorize fields
        populated = {}
        missing = []
        zero_values = []

        for key, value in result.items():
            if key in ['scrape_timestamp', 'scraping_duration_seconds', 'company_name', 'tier']:
                continue  # Skip metadata fields

            if value and value != 0 and value != '' and value != [] and value != 'None':
                populated[key] = value
            elif value == 0 or value == [] or value == 'None':
                zero_values.append(key)
            else:
                missing.append(key)

        # Print summary
        total_fields = len(populated) + len(missing) + len(zero_values)
        completeness = (len(populated) / total_fields * 100) if total_fields > 0 else 0

        print(f"\n📊 SUMMARY:")
        print(f"  Total Fields: {total_fields}")
        print(f"  ✅ Populated: {len(populated)} ({len(populated)/total_fields*100:.1f}%)")
        print(f"  ⚠️  Zero/Empty: {len(zero_values)} ({len(zero_values)/total_fields*100:.1f}%)")
        print(f"  ❌ Missing: {len(missing)} ({len(missing)/total_fields*100:.1f}%)")
        print(f"  📈 Completeness: {completeness:.1f}%")

        # Show what's missing
        if missing:
            print(f"\n❌ MISSING FIELDS ({len(missing)}):")
            for field in sorted(missing):
                print(f"  - {field}")

        if zero_values:
            print(f"\n⚠️  ZERO/EMPTY FIELDS ({len(zero_values)}):")
            for field in sorted(zero_values):
                print(f"  - {field}")

        # Show key populated fields
        print(f"\n✅ KEY POPULATED FIELDS:")
        key_fields = ['base_nightly_rate', 'customer_review_avg', 'review_count',
                     'locations_available', 'vehicle_types', 'insurance_cost_per_day',
                     'cleaning_fee', 'min_rental_days']
        for field in key_fields:
            if field in populated:
                val = populated[field]
                if isinstance(val, list):
                    print(f"  ✓ {field}: {len(val)} items")
                else:
                    print(f"  ✓ {field}: {val}")
            else:
                print(f"  ✗ {field}: NOT EXTRACTED")

        return {
            'name': name,
            'total': total_fields,
            'populated': len(populated),
            'missing': len(missing),
            'zero': len(zero_values),
            'completeness': completeness,
            'missing_fields': missing,
            'zero_fields': zero_values
        }

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {
            'name': name,
            'error': str(e)
        }


async def main():
    """Analyze all competitors"""
    print("="*70)
    print("DATA COMPLETENESS ANALYSIS")
    print("Identifying gaps for targeted improvement")
    print("="*70)

    competitors = [
        (RoadsurferScraper, "Roadsurfer"),
        (McRentScraper, "McRent"),
        (GoboonyScraper, "Goboony"),
        (YescapaScraper, "Yescapa"),
        (CamperdaysScraper, "Camperdays"),
    ]

    results = []
    for scraper_class, name in competitors:
        result = await analyze_single_competitor(scraper_class, name)
        results.append(result)
        await asyncio.sleep(2)  # Delay between scrapes

    # Overall summary
    print("\n" + "="*70)
    print("OVERALL ANALYSIS")
    print("="*70)

    avg_completeness = sum(r.get('completeness', 0) for r in results) / len(results)
    print(f"\nAverage Completeness: {avg_completeness:.1f}%")
    print(f"Target: 70%+")
    print(f"Gap: {max(0, 70 - avg_completeness):.1f} percentage points to close")

    # Show completeness by competitor
    print(f"\n{'Competitor':<15} {'Complete':<12} {'Missing':<10} {'Status':<15}")
    print("-"*55)
    for r in results:
        if 'error' not in r:
            status = "✅ Good" if r['completeness'] >= 70 else f"⚠️  Need +{70-r['completeness']:.1f}%"
            print(f"{r['name']:<15} {r['completeness']:<11.1f}% {r['missing']:<10} {status:<15}")

    # Find common missing fields
    print("\n" + "="*70)
    print("COMMON MISSING FIELDS (High Priority Fixes)")
    print("="*70)

    all_missing = {}
    for r in results:
        if 'missing_fields' in r:
            for field in r['missing_fields']:
                all_missing[field] = all_missing.get(field, 0) + 1

    # Show fields missing in 3+ competitors
    critical_missing = {k: v for k, v in all_missing.items() if v >= 3}
    if critical_missing:
        print("\n🔴 CRITICAL (Missing in 3+ competitors):")
        for field, count in sorted(critical_missing.items(), key=lambda x: -x[1]):
            print(f"  - {field}: missing in {count}/5 competitors")

    # Show fields missing in 1-2 competitors
    moderate_missing = {k: v for k, v in all_missing.items() if 1 <= v < 3}
    if moderate_missing:
        print("\n🟡 MODERATE (Missing in 1-2 competitors):")
        for field, count in sorted(moderate_missing.items(), key=lambda x: -x[1]):
            print(f"  - {field}: missing in {count}/5 competitors")

    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS TO REACH 70%+ COMPLETENESS")
    print("="*70)

    print("\n1. FIX CRITICAL MISSING FIELDS (3+ competitors)")
    print("   Priority: HIGH")
    print("   Impact: +10-15% completeness")

    print("\n2. FIX MODERATE MISSING FIELDS (1-2 competitors)")
    print("   Priority: MEDIUM")
    print("   Impact: +5-10% completeness")

    print("\n3. FIX ZERO/EMPTY FIELDS")
    print("   Priority: MEDIUM")
    print("   Impact: +5-8% completeness")

    print("\n4. COMPETITOR-SPECIFIC FIXES")
    for r in results:
        if 'error' not in r and r['completeness'] < 70:
            gap = 70 - r['completeness']
            fields_needed = int(gap / 100 * r['total'])
            print(f"   - {r['name']}: Need {fields_needed}+ more fields (gap: {gap:.1f}%)")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted")
    except Exception as e:
        print(f"\n\nError: {e}")
