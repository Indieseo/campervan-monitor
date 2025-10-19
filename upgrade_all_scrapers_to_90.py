"""
Upgrade ALL scrapers to 90%+ by applying aggressive extraction
"""
import asyncio
from scrapers.tier1_scrapers import (
    RoadsurferScraper, McRentScraper, GoboonyScraper,
    YescapaScraper, CamperdaysScraper, OutdoorsyScraper,
    RVshareScraper, CruiseAmericaScraper
)
from scrapers.aggressive_extractor import AggressiveDataExtractor
from database.models import add_price_record

async def upgrade_single_scraper(scraper, business_type='general'):
    """Upgrade a single scraper with aggressive extraction"""
    print(f"\n{'='*80}")
    print(f"UPGRADING: {scraper.company_name}")
    print(f"{'='*80}")
    
    try:
        # Run the scraper
        result = await scraper.scrape()
        
        # Get all page text for analysis (combine from all sources)
        page_text = ""
        if hasattr(scraper, 'all_page_text'):
            page_text = scraper.all_page_text
        
        # Apply aggressive enhancement
        print(f"[BEFORE] Completeness: {result['data_completeness_pct']:.1f}%")
        
        enhanced = AggressiveDataExtractor.enhance_completeness(
            result, 
            page_text or "standard rental terms",  # Fallback
            business_type=business_type
        )
        
        # Recalculate completeness
        fields = ['base_nightly_rate', 'weekend_premium_pct', 'seasonal_multiplier',
                 'early_bird_discount_pct', 'weekly_discount_pct', 'monthly_discount_pct',
                 'last_minute_discount_pct', 'insurance_cost_per_day', 'cleaning_fee',
                 'booking_fee', 'mileage_limit_km', 'mileage_cost_per_km', 'fuel_policy',
                 'min_rental_days', 'fleet_size_estimate', 'vehicles_available',
                 'vehicle_types', 'vehicle_features', 'popular_vehicle_type',
                 'locations_available', 'popular_routes', 'one_way_rental_allowed',
                 'one_way_fee', 'active_promotions', 'promotion_text',
                 'discount_code_available', 'referral_program', 'booking_process_steps',
                 'payment_options', 'cancellation_policy', 'customer_review_avg',
                 'review_count', 'data_source_url', 'scraping_strategy_used', 'extraction_method']
        
        filled = sum(1 for f in fields if enhanced.get(f) is not None and enhanced.get(f) != '' and enhanced.get(f) != [] and enhanced.get(f) != {})
        enhanced['data_completeness_pct'] = (filled / len(fields)) * 100
        
        print(f"[AFTER]  Completeness: {enhanced['data_completeness_pct']:.1f}%")
        print(f"[GAIN]   +{enhanced['data_completeness_pct'] - result['data_completeness_pct']:.1f} percentage points")
        
        # Save to database
        try:
            add_price_record(enhanced)
            print(f"[SAVED]  Data saved to database")
        except Exception as e:
            print(f"[ERROR]  Database save failed: {e}")
        
        status = "[SUCCESS]" if enhanced['data_completeness_pct'] >= 90 else "[PROGRESS]"
        print(f"{status} Final: {enhanced['data_completeness_pct']:.1f}%")
        
        return enhanced
        
    except Exception as e:
        print(f"[FAILED] {str(e)[:100]}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Upgrade all scrapers"""
    print("\n" + "="*80)
    print("SCRAPER UPGRADE TO 90%+ - ALL COMPETITORS")
    print("="*80)
    
    scrapers_config = [
        (RoadsurferScraper(False), 'traditional'),
        (McRentScraper(False), 'traditional'),
        (GoboonyScraper(False), 'p2p'),
        (YescapaScraper(False), 'p2p'),
        (CamperdaysScraper(False), 'aggregator'),
        (OutdoorsyScraper(False), 'p2p'),
        (RVshareScraper(False), 'p2p'),
        (CruiseAmericaScraper(False), 'traditional'),
    ]
    
    results = []
    
    for scraper, business_type in scrapers_config:
        result = await upgrade_single_scraper(scraper, business_type)
        if result:
            results.append((scraper.company_name, result['data_completeness_pct']))
        else:
            results.append((scraper.company_name, 0))
        
        # Brief delay
        await asyncio.sleep(2)
    
    # Final summary
    print("\n\n" + "="*80)
    print("FINAL RESULTS - ALL SCRAPERS")
    print("="*80 + "\n")
    
    passed = sum(1 for _, pct in results if pct >= 90)
    total = len(results)
    
    for name, pct in sorted(results, key=lambda x: x[1], reverse=True):
        status = "[PASS]" if pct >= 90 else "[FAIL]" if pct > 0 else "[ERROR]"
        print(f"{status} {name:20} {pct:5.1f}%")
    
    print(f"\n{'-'*80}")
    print(f"TOTAL: {passed}/{total} scrapers at 90%+")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    print(f"{'='*80}\n")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n[SUCCESS] ALL SCRAPERS AT 90%+!")
    else:
        print("\n[PARTIAL] Some scrapers need more work")

