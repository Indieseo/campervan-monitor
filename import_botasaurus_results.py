"""
Import Botasaurus scraping results into database
"""

import json
from datetime import datetime
from pathlib import Path
from database.models import get_session, CompetitorPrice, init_database

# Initialize database (creates tables if needed)
init_database()

# Load the latest Botasaurus results
result_file = "output/all_competitors_20251017_105925.json"

print("="*80)
print("IMPORTING BOTASAURUS RESULTS TO DATABASE")
print("="*80)
print(f"Source: {result_file}\n")

with open(result_file, 'r') as f:
    results = json.load(f)

session = get_session()

imported_count = 0
for result in results:
    try:
        # Create database entry
        price_entry = CompetitorPrice(
            company_name=result['company_name'],
            scrape_timestamp=datetime.fromisoformat(result['timestamp']),
            tier=1,  # All are Tier-1
            
            # Pricing
            base_nightly_rate=result.get('base_nightly_rate'),
            currency=result.get('currency', 'EUR'),
            insurance_cost_per_day=result.get('insurance_cost_per_day'),
            cleaning_fee=result.get('cleaning_fee'),
            
            # Inventory
            mileage_limit_km=result.get('mileage_limit_km'),
            min_rental_days=result.get('min_rental_days'),
            fleet_size_estimate=result.get('fleet_size_estimate'),
            fuel_policy=result.get('fuel_policy'),
            
            # Vehicle details
            vehicle_types=result.get('vehicle_types', []),
            
            # Geographic
            locations_available=result.get('locations_available', []),
            one_way_rental_allowed=result.get('one_way_rental_allowed', False),
            
            # Customer experience
            payment_options=result.get('payment_options', []),
            cancellation_policy=result.get('cancellation_policy'),
            customer_review_avg=result.get('customer_review_avg'),
            review_count=result.get('review_count'),
            
            # Metadata
            data_source_url=result.get('url'),
            scraping_strategy_used=result.get('scraping_strategy_used', 'botasaurus_headless'),
            data_completeness_pct=result.get('data_completeness_pct'),
            is_estimated=result.get('is_estimated', False),
            notes=result.get('notes', '')
        )
        
        session.add(price_entry)
        imported_count += 1
        print(f"[OK] Imported: {result['company_name']:20} - {result['currency']}{result['base_nightly_rate']}/night")
        
    except Exception as e:
        print(f"[ERROR] Error importing {result.get('company_name', 'Unknown')}: {e}")

# Commit all changes
session.commit()
session.close()

print("\n" + "="*80)
print(f"IMPORT COMPLETE: {imported_count}/{len(results)} entries imported")
print("="*80)
print("\nDatabase ready! Launch dashboard with:")
print("  launch_dashboard.bat")
print("\nOr run:")
print("  streamlit run dashboard/app.py")
print()

