"""Analyze what data is missing for each competitor to reach 90%+"""
from database.models import get_session, CompetitorPrice
from datetime import datetime

# All available fields (41 total)
ALL_FIELDS = [
    'base_nightly_rate', 'weekend_premium_pct', 'seasonal_multiplier',
    'early_bird_discount_pct', 'weekly_discount_pct', 'monthly_discount_pct', 
    'last_minute_discount_pct', 'insurance_cost_per_day', 'cleaning_fee', 'booking_fee',
    'mileage_limit_km', 'mileage_cost_per_km', 'fuel_policy', 'min_rental_days',
    'fleet_size_estimate', 'vehicles_available', 'vehicle_types', 'vehicle_features',
    'popular_vehicle_type', 'locations_available', 'popular_routes',
    'one_way_rental_allowed', 'one_way_fee', 'active_promotions', 'promotion_text',
    'discount_code_available', 'referral_program', 'booking_process_steps',
    'payment_options', 'cancellation_policy', 'customer_review_avg', 'review_count',
    'data_source_url', 'scraping_strategy_used', 'extraction_method'
]

session = get_session()

print("\n" + "="*100)
print("DATA COMPLETENESS ANALYSIS - PATH TO 90%+")
print("="*100 + "\n")

# Get latest data
latest = session.query(CompetitorPrice)\
    .filter(CompetitorPrice.scrape_timestamp >= datetime.now().replace(hour=0, minute=0, second=0))\
    .order_by(CompetitorPrice.scrape_timestamp.desc())\
    .all()

if not latest:
    latest = session.query(CompetitorPrice).order_by(CompetitorPrice.scrape_timestamp.desc()).limit(10).all()

companies = {}
for record in latest:
    if record.company_name not in companies:
        companies[record.company_name] = record

for name in sorted(companies.keys()):
    data = companies[name]
    
    print(f"\n{'-'*100}")
    print(f"COMPANY: {name}")
    print(f"Current Completeness: {data.data_completeness_pct:.1f}%")
    print(f"Target: 90%+ (Need +{90-data.data_completeness_pct:.1f} percentage points)")
    print(f"{'-'*100}")
    
    # Check which fields are filled
    filled = []
    missing = []
    
    for field in ALL_FIELDS:
        value = getattr(data, field, None)
        if value is not None and value != '' and value != [] and value != {}:
            if isinstance(value, (list, dict)):
                if len(value) > 0:
                    filled.append(field)
                else:
                    missing.append(field)
            else:
                filled.append(field)
        else:
            missing.append(field)
    
    print(f"\nFilled Fields: {len(filled)}/{len(ALL_FIELDS)} ({len(filled)/len(ALL_FIELDS)*100:.1f}%)")
    print(f"Missing Fields: {len(missing)}")
    
    # Priority missing fields
    critical_missing = [f for f in missing if f in [
        'base_nightly_rate', 'insurance_cost_per_day', 'cleaning_fee',
        'weekly_discount_pct', 'monthly_discount_pct', 'mileage_limit_km',
        'fuel_policy', 'min_rental_days', 'customer_review_avg', 'review_count'
    ]]
    
    if critical_missing:
        print(f"\n[CRITICAL MISSING] High-value fields:")
        for field in critical_missing:
            print(f"  - {field}")
    
    # Nice-to-have missing
    optional_missing = [f for f in missing if f not in critical_missing]
    if optional_missing:
        print(f"\n[OPTIONAL MISSING] Lower priority:")
        for field in optional_missing[:10]:  # Show first 10
            print(f"  - {field}")
        if len(optional_missing) > 10:
            print(f"  ... and {len(optional_missing)-10} more")
    
    # Show what we have
    print(f"\n[CURRENT DATA]:")
    important_fields = ['base_nightly_rate', 'customer_review_avg', 'review_count', 
                       'fleet_size_estimate', 'locations_available', 'insurance_cost_per_day',
                       'cleaning_fee', 'extraction_method']
    for field in important_fields:
        value = getattr(data, field, None)
        if value:
            if isinstance(value, list):
                print(f"  {field}: {len(value)} items")
            elif isinstance(value, dict):
                print(f"  {field}: {len(value)} keys")
            else:
                print(f"  {field}: {value}")
    
    # Calculate what's needed for 90%
    fields_needed_for_90 = int(0.9 * len(ALL_FIELDS)) - len(filled)
    print(f"\n[ACTION REQUIRED]")
    print(f"  Need {fields_needed_for_90} more fields to reach 90%")
    print(f"  Priority: Fill critical missing fields first")

print(f"\n{'='*100}")
print("SUMMARY")
print(f"{'='*100}\n")

for name, data in sorted(companies.items(), key=lambda x: x[1].data_completeness_pct):
    gap = 90 - data.data_completeness_pct
    status = "[GOOD]" if gap <= 10 else "[NEEDS WORK]"
    print(f"{status} {name:20} {data.data_completeness_pct:5.1f}% (Gap to 90%: {gap:+5.1f} points)")

session.close()

