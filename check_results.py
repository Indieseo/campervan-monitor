"""Check scraping results from database"""
from database.models import get_session, CompetitorPrice

s = get_session()
records = s.query(CompetitorPrice).order_by(CompetitorPrice.scrape_timestamp.desc()).limit(5).all()

print('='*70)
print('TIER 1 SCRAPING RESULTS (Latest 5)')
print('='*70)

for r in records:
    print(f'\nCompany: {r.company_name}')
    print(f'  Price: EUR {r.base_nightly_rate}')
    print(f'  Reviews: {r.customer_review_avg} stars ({r.review_count} reviews)')
    print(f'  Locations: {len(r.locations_available) if r.locations_available else 0}')
    print(f'  Fleet: {r.fleet_size_estimate}')
    print(f'  Insurance: EUR {r.insurance_cost_per_day}')
    print(f'  Cleaning Fee: EUR {r.cleaning_fee}')
    print(f'  Completeness: {r.data_completeness_pct}%')
    print(f'  Timestamp: {r.scrape_timestamp}')

print('='*70)
print('\nSUCCESS METRICS:')
print('='*70)

# Count successes
price_ok = sum(1 for r in records if r.base_nightly_rate and r.base_nightly_rate > 0)
reviews_ok = sum(1 for r in records if r.customer_review_avg or r.review_count)
locations_ok = sum(1 for r in records if r.locations_available and len(r.locations_available) >= 5)
insurance_ok = sum(1 for r in records if r.insurance_cost_per_day or r.cleaning_fee)

avg_completeness = sum(r.data_completeness_pct for r in records) / len(records)

print(f'Pricing extracted: {price_ok}/5 scrapers ({price_ok/5*100:.0f}%)')
print(f'Reviews extracted: {reviews_ok}/5 scrapers ({reviews_ok/5*100:.0f}%)')
print(f'Locations extracted: {locations_ok}/5 scrapers ({locations_ok/5*100:.0f}%)')
print(f'Insurance/fees extracted: {insurance_ok}/5 scrapers ({insurance_ok/5*100:.0f}%)')
print(f'Average completeness: {avg_completeness:.1f}%')

print('\n' + '='*70)
print('TARGET vs ACTUAL:')
print('='*70)
print(f'Price > 0 for 4/5:     TARGET 80% | ACTUAL {price_ok/5*100:.0f}%')
print(f'Reviews for 3/5:       TARGET 60% | ACTUAL {reviews_ok/5*100:.0f}%')
print(f'Completeness >= 60%:   TARGET 60% | ACTUAL {avg_completeness:.1f}%')
print('='*70)

s.close()
