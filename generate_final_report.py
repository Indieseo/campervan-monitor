"""Generate comprehensive final report from all scraped data"""
import json
from pathlib import Path
from datetime import datetime
from database.models import get_session, CompetitorPrice
from sqlalchemy import func, desc

def generate_report():
    """Generate comprehensive intelligence report"""
    print("\n" + "="*80)
    print("CAMPERVAN COMPETITIVE INTELLIGENCE - COMPREHENSIVE REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    session = get_session()
    
    # Get latest data for each competitor
    latest_prices = session.query(CompetitorPrice)\
        .filter(CompetitorPrice.scrape_timestamp >= datetime.now().replace(hour=0, minute=0, second=0))\
        .order_by(CompetitorPrice.scrape_timestamp.desc())\
        .all()
    
    if not latest_prices:
        print("[WARNING] No data found for today. Checking last 7 days...")
        latest_prices = session.query(CompetitorPrice)\
            .order_by(CompetitorPrice.scrape_timestamp.desc())\
            .limit(10)\
            .all()
    
    # Group by company (get most recent for each)
    companies = {}
    for price in latest_prices:
        if price.company_name not in companies:
            companies[price.company_name] = price
    
    print(f"TOTAL COMPETITORS ANALYZED: {len(companies)}\n")
    print("="*80)
    print("DETAILED COMPETITOR ANALYSIS")
    print("="*80 + "\n")
    
    for company_name, data in sorted(companies.items()):
        print(f"\n{'-'*80}")
        print(f"COMPANY: {company_name}")
        print(f"{'-'*80}")
        print(f"Last Updated: {data.scrape_timestamp.strftime('%Y-%m-%d %H:%M')}")
        print(f"Data Completeness: {data.data_completeness_pct:.1f}%")
        
        # Pricing
        print(f"\n[PRICING]")
        if data.base_nightly_rate:
            estimated_flag = " (ESTIMATED)" if data.is_estimated else " (REAL DATA)"
            print(f"  Base Rate: ${data.base_nightly_rate:.2f}/night{estimated_flag}")
            if data.extraction_method:
                print(f"  Extraction Method: {data.extraction_method}")
        else:
            print(f"  Base Rate: NOT AVAILABLE")
        
        if data.weekend_premium_pct:
            print(f"  Weekend Premium: +{data.weekend_premium_pct}%")
        if data.weekly_discount_pct:
            print(f"  Weekly Discount: -{data.weekly_discount_pct}%")
        if data.monthly_discount_pct:
            print(f"  Monthly Discount: -{data.monthly_discount_pct}%")
        
        # Fees
        if data.insurance_cost_per_day or data.cleaning_fee or data.booking_fee:
            print(f"\n[FEES]")
            if data.insurance_cost_per_day:
                print(f"  Insurance: ${data.insurance_cost_per_day:.2f}/day")
            if data.cleaning_fee:
                print(f"  Cleaning: ${data.cleaning_fee:.2f}")
            if data.booking_fee:
                print(f"  Booking: ${data.booking_fee:.2f}")
        
        # Policies
        if data.mileage_limit_km or data.fuel_policy or data.min_rental_days:
            print(f"\n[POLICIES]")
            if data.mileage_limit_km:
                print(f"  Mileage Limit: {data.mileage_limit_km} km/day")
                if data.mileage_cost_per_km:
                    print(f"  Overage: ${data.mileage_cost_per_km:.2f}/km")
            if data.fuel_policy:
                print(f"  Fuel Policy: {data.fuel_policy}")
            if data.min_rental_days:
                print(f"  Minimum Rental: {data.min_rental_days} days")
        
        # Fleet & Locations
        if data.fleet_size_estimate or data.locations_available:
            print(f"\n[OPERATIONS]")
            if data.fleet_size_estimate:
                print(f"  Fleet Size: ~{data.fleet_size_estimate} vehicles")
            if data.locations_available and isinstance(data.locations_available, list):
                print(f"  Locations: {len(data.locations_available)} stations")
        
        # Reviews
        if data.customer_review_avg or data.review_count:
            print(f"\n[CUSTOMER SATISFACTION]")
            if data.customer_review_avg:
                print(f"  Rating: {data.customer_review_avg:.1f}/5.0 stars")
            if data.review_count:
                print(f"  Reviews: {data.review_count:,}")
        
        # Promotions
        if data.active_promotions and isinstance(data.active_promotions, list) and len(data.active_promotions) > 0:
            print(f"\n[ACTIVE PROMOTIONS]")
            for promo in data.active_promotions[:3]:  # Show first 3
                if isinstance(promo, dict):
                    print(f"  - {promo.get('text', 'Promotion available')}")
    
    # Market Analysis
    print(f"\n\n{'='*80}")
    print("MARKET ANALYSIS")
    print(f"{'='*80}\n")
    
    prices = [p.base_nightly_rate for p in companies.values() if p.base_nightly_rate and p.base_nightly_rate > 0]
    
    if prices:
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        print(f"Average Market Price: ${avg_price:.2f}/night")
        print(f"Price Range: ${min_price:.2f} - ${max_price:.2f}")
        print(f"Price Spread: ${max_price - min_price:.2f} ({((max_price/min_price - 1)*100):.1f}%)")
        
        # Find cheapest and most expensive
        cheapest = min(companies.values(), key=lambda x: x.base_nightly_rate if x.base_nightly_rate else float('inf'))
        most_expensive = max(companies.values(), key=lambda x: x.base_nightly_rate if x.base_nightly_rate else 0)
        
        print(f"\nCheapest: {cheapest.company_name} at ${cheapest.base_nightly_rate:.2f}/night")
        print(f"Most Expensive: {most_expensive.company_name} at ${most_expensive.base_nightly_rate:.2f}/night")
    
    # Data Quality Summary
    print(f"\n\n{'='*80}")
    print("DATA QUALITY SUMMARY")
    print(f"{'='*80}\n")
    
    completeness_scores = [(p.company_name, p.data_completeness_pct) for p in companies.values()]
    completeness_scores.sort(key=lambda x: x[1], reverse=True)
    
    avg_completeness = sum(c[1] for c in completeness_scores) / len(completeness_scores)
    print(f"Average Data Completeness: {avg_completeness:.1f}%\n")
    
    for name, score in completeness_scores:
        status = "[EXCELLENT]" if score >= 60 else "[GOOD]" if score >= 40 else "[NEEDS WORK]"
        print(f"  {status} {name:20} {score:5.1f}%")
    
    # Real vs Estimated Data
    real_data_count = sum(1 for p in companies.values() if not p.is_estimated and p.base_nightly_rate)
    estimated_count = sum(1 for p in companies.values() if p.is_estimated and p.base_nightly_rate)
    
    print(f"\n\nReal Data: {real_data_count} competitors")
    print(f"Estimated Data: {estimated_count} competitors")
    print(f"Real Data Rate: {(real_data_count/(real_data_count+estimated_count)*100):.1f}%")
    
    print(f"\n{'='*80}")
    print("END OF REPORT")
    print(f"{'='*80}\n")
    
    session.close()
    
    return {
        'competitors': len(companies),
        'avg_price': avg_price if prices else 0,
        'avg_completeness': avg_completeness,
        'real_data_rate': (real_data_count/(real_data_count+estimated_count)*100) if (real_data_count+estimated_count) > 0 else 0
    }

if __name__ == "__main__":
    stats = generate_report()
    print(f"\n[SUMMARY] {stats['competitors']} competitors | Avg Price: ${stats['avg_price']:.2f} | Data Quality: {stats['avg_completeness']:.1f}% | Real Data: {stats['real_data_rate']:.1f}%\n")

