"""Display your competitive intelligence results"""
import json
from pathlib import Path

# Load the intelligence summary
summary_file = Path("data/daily_summaries/intelligence_2025-10-15.json")
data = json.load(open(summary_file, encoding='utf-8'))

print("\n" + "="*70)
print("YOUR COMPETITIVE INTELLIGENCE RESULTS")
print("="*70)
print(f"\nDate: {data['date']}")
print(f"Competitors Analyzed: {data['competitors_analyzed']}")
print(f"Average Data Completeness: {data['data_completeness_avg']:.1f}%")
print(f"Alerts Generated: {data['alerts_generated']}")

print("\n" + "="*70)
print("COMPETITOR PRICING")
print("="*70)

for r in data['results']:
    price = r.get('base_nightly_rate')
    if price:
        print(f"{r['company_name']:20} EUR{price:6.1f}/night  {r['data_completeness_pct']:.1f}% complete")
    else:
        print(f"{r['company_name']:20} No price    {r['data_completeness_pct']:.1f}% complete")

print("\n" + "="*70)
print("STRATEGIC ALERTS")
print("="*70)

for alert in data['alerts']:
    print(f"\n[{alert['severity'].upper()}] {alert['message']}")
    print(f"Action: {alert['recommended_action']}")

print("\n" + "="*70)
print("ACTIVE PROMOTIONS")
print("="*70)

for r in data['results']:
    if r.get('active_promotions'):
        print(f"\n{r['company_name']}:")
        for promo in r['active_promotions'][:3]:
            if isinstance(promo, dict):
                text = promo.get('text', str(promo))[:70]
                if promo.get('code'):
                    print(f"  - Code: {promo['code']} - {text}")
                else:
                    print(f"  - {text}")
            else:
                print(f"  - {str(promo)[:70]}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

prices_with_data = [r['base_nightly_rate'] for r in data['results'] if r.get('base_nightly_rate')]
if prices_with_data:
    import statistics
    print(f"\nMarket Average: EUR{statistics.mean(prices_with_data):.2f}/night")
    print(f"Price Range: EUR{min(prices_with_data):.0f} - EUR{max(prices_with_data):.0f}")
    print(f"Competitors with Pricing: {len(prices_with_data)}/8")

print(f"\nYour system is working and delivering competitive intelligence!")
print(f"\nDashboard: http://localhost:8501")
print("="*70 + "\n")







