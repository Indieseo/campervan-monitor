"""Quick status check - simple output"""
import sys
from database.models import get_session, CompetitorPrice
from datetime import datetime

session = get_session()

print("\n" + "="*80)
print("QUICK STATUS CHECK - CAMPERVAN MONITOR")
print("="*80 + "\n")

# Get today's data
today_data = session.query(CompetitorPrice)\
    .filter(CompetitorPrice.scrape_timestamp >= datetime.now().replace(hour=0, minute=0, second=0))\
    .order_by(CompetitorPrice.company_name, CompetitorPrice.scrape_timestamp.desc())\
    .all()

if not today_data:
    print("[INFO] No data from today. Checking recent data...")
    today_data = session.query(CompetitorPrice)\
        .order_by(CompetitorPrice.scrape_timestamp.desc())\
        .limit(20)\
        .all()

# Group by company
companies = {}
for record in today_data:
    if record.company_name not in companies:
        companies[record.company_name] = record

print(f"TOTAL COMPETITORS: {len(companies)}\n")

for name in sorted(companies.keys()):
    data = companies[name]
    price = data.base_nightly_rate if data.base_nightly_rate else 0
    complete = data.data_completeness_pct
    method = data.extraction_method if data.extraction_method else "N/A"
    estimated = "YES" if data.is_estimated else "NO"
    
    status = "[OK]" if complete >= 40 else "[LOW]"
    
    print(f"{status} {name:20} | Price: ${price:6.2f} | Complete: {complete:5.1f}% | Method: {method:20} | Est: {estimated}")

# Calculate averages
prices = [d.base_nightly_rate for d in companies.values() if d.base_nightly_rate and d.base_nightly_rate > 0]
completeness = [d.data_completeness_pct for d in companies.values()]

if prices:
    avg_price = sum(prices) / len(prices)
    print(f"\n{'='*80}")
    print(f"AVERAGES:")
    print(f"  Market Price: ${avg_price:.2f}/night")
    print(f"  Data Quality: {sum(completeness)/len(completeness):.1f}%")
    print(f"  Real Data: {sum(1 for d in companies.values() if not d.is_estimated)} / {len(companies)}")
    print(f"{'='*80}\n")

session.close()

