"""Check the JSON summary from last run"""
from pathlib import Path
import json

summary_file = sorted(Path('data/daily_summaries').glob('*.json'))[-1]
data = json.loads(summary_file.read_text())

print('SUMMARY FILE:', summary_file.name)
print('='*70)

for r in data['results']:
    print(f"\nCompany: {r['company_name']}")
    print(f"  Price: {r['base_nightly_rate']}")
    print(f"  Reviews: {r['customer_review_avg']} / {r['review_count']}")
    print(f"  Locations: {len(r['locations_available'])}")
    print(f"  Fleet: {r['fleet_size_estimate']}")
    print(f"  Completeness: {r['data_completeness_pct']}%")

print('='*70)
print(f"\nData completeness avg: {data['data_completeness_avg']:.1f}%")
print(f"Alerts generated: {data['alerts_generated']}")
