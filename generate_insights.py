"""Generate comprehensive competitive insights from scraped data"""
from database.models import get_session, CompetitorPrice
from datetime import datetime
import statistics

def generate_comprehensive_insights():
    """Generate detailed competitive intelligence insights"""
    session = get_session()
    
    # Get latest records
    competitors = session.query(CompetitorPrice).order_by(CompetitorPrice.id.desc()).limit(8).all()
    
    if not competitors:
        print("No data available. Run `python run_intelligence.py` first.")
        return
    
    print("\n" + "="*80)
    print("COMPREHENSIVE COMPETITIVE INTELLIGENCE REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Competitors Analyzed: {len(competitors)}")
    
    # === PRICING INSIGHTS ===
    print("\n" + "="*80)
    print("PRICING INTELLIGENCE")
    print("="*80)
    
    prices = [c.base_nightly_rate for c in competitors if c.base_nightly_rate]
    if prices:
        avg_price = statistics.mean(prices)
        median_price = statistics.median(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        print(f"\n[Market Pricing]")
        print(f"   Average: EUR{avg_price:.2f}/night")
        print(f"   Median:  EUR{median_price:.2f}/night")
        print(f"   Range:   EUR{min_price:.2f} - EUR{max_price:.2f}")
        print(f"   Spread:  EUR{max_price - min_price:.2f} ({((max_price/min_price - 1) * 100):.1f}% variance)")
        
        print(f"\n[Price Leaders]")
        sorted_by_price = sorted(competitors, key=lambda x: x.base_nightly_rate or 999)
        for i, comp in enumerate(sorted_by_price[:3], 1):
            if comp.base_nightly_rate:
                vs_market = ((comp.base_nightly_rate / avg_price) - 1) * 100
                indicator = "LOW" if vs_market < -10 else "MARKET" if abs(vs_market) <= 10 else "HIGH"
                print(f"   {i}. {comp.company_name}: EUR{comp.base_nightly_rate:.2f}/night ({vs_market:+.1f}% vs market) [{indicator}]")
    
    # === INSURANCE & FEES INSIGHTS ===
    print("\n" + "="*80)
    print("INSURANCE & FEES INTELLIGENCE")
    print("="*80)
    
    insurance_costs = [c.insurance_cost_per_day for c in competitors if c.insurance_cost_per_day]
    cleaning_fees = [c.cleaning_fee for c in competitors if c.cleaning_fee]
    
    if insurance_costs:
        avg_insurance = statistics.mean(insurance_costs)
        print(f"\n[Insurance Costs]")
        print(f"   Average: EUR{avg_insurance:.2f}/day")
        print(f"   Range: EUR{min(insurance_costs):.2f} - EUR{max(insurance_costs):.2f}/day")
        print(f"\n   By Competitor:")
        for comp in sorted(competitors, key=lambda x: x.insurance_cost_per_day or 999):
            if comp.insurance_cost_per_day:
                vs_avg = ((comp.insurance_cost_per_day / avg_insurance) - 1) * 100
                indicator = "Affordable" if vs_avg < -10 else "Premium" if vs_avg > 10 else "Standard"
                print(f"      {comp.company_name}: EUR{comp.insurance_cost_per_day:.2f}/day ({vs_avg:+.1f}% vs avg) [{indicator}]")
    
    if cleaning_fees:
        avg_cleaning = statistics.mean(cleaning_fees)
        print(f"\n[Cleaning Fees]")
        print(f"   Average: EUR{avg_cleaning:.2f}")
        print(f"   Range: EUR{min(cleaning_fees):.2f} - EUR{max(cleaning_fees):.2f}")
        print(f"\n   Lowest: {[c.company_name for c in competitors if c.cleaning_fee == min(cleaning_fees)][0]} (EUR{min(cleaning_fees):.2f})")
        print(f"   Highest: {[c.company_name for c in competitors if c.cleaning_fee == max(cleaning_fees)][0]} (EUR{max(cleaning_fees):.2f})")
    
    # === DISCOUNT INSIGHTS ===
    print("\n" + "="*80)
    print("DISCOUNT & PROMOTIONS INTELLIGENCE")
    print("="*80)
    
    weekly_discounts = [c.weekly_discount_pct for c in competitors if c.weekly_discount_pct]
    monthly_discounts = [c.monthly_discount_pct for c in competitors if c.monthly_discount_pct]
    
    if weekly_discounts:
        print(f"\n[Weekly Discounts]")
        print(f"   Average: {statistics.mean(weekly_discounts):.1f}%")
        print(f"   Best: {max(weekly_discounts):.1f}% ({[c.company_name for c in competitors if c.weekly_discount_pct == max(weekly_discounts)][0]})")
    
    if monthly_discounts:
        print(f"\n[Monthly Discounts]")
        print(f"   Average: {statistics.mean(monthly_discounts):.1f}%")
        print(f"   Best: {max(monthly_discounts):.1f}% ({[c.company_name for c in competitors if c.monthly_discount_pct == max(monthly_discounts)][0]})")
    
    # Promotion counts
    promo_counts = [(c.company_name, len(c.active_promotions or [])) for c in competitors]
    active_promos = [p for p in promo_counts if p[1] > 0]
    if active_promos:
        print(f"\n[Active Promotions]")
        for name, count in sorted(active_promos, key=lambda x: x[1], reverse=True):
            print(f"   {name}: {count} active promotion(s)")
    
    # === REVIEW INSIGHTS ===
    print("\n" + "="*80)
    print("CUSTOMER SATISFACTION INTELLIGENCE")
    print("="*80)
    
    reviews = [(c.company_name, c.customer_review_avg, c.review_count) for c in competitors if c.customer_review_avg]
    if reviews:
        avg_rating = statistics.mean([r[1] for r in reviews])
        print(f"\n[Market Average Rating]: {avg_rating:.2f} stars")
        
        print(f"\n[Top Rated]")
        for i, (name, rating, count) in enumerate(sorted(reviews, key=lambda x: x[1], reverse=True)[:3], 1):
            medal = "[GOLD]" if i == 1 else "[SILVER]" if i == 2 else "[BRONZE]"
            count_str = f"({count:,} reviews)" if count else "(reviews available)"
            print(f"   {medal} {name}: {rating:.1f} stars {count_str}")
        
        # Trust indicators
        print(f"\n[Trust Indicators]")
        for name, rating, count in sorted(reviews, key=lambda x: x[2] if x[2] else 0, reverse=True):
            if count and count > 10000:
                print(f"   [HIGHLY TRUSTED] {name}: {count:,} reviews")
            elif count and count > 1000:
                print(f"   [ESTABLISHED] {name}: {count:,} reviews")
    
    # === FLEET INSIGHTS ===
    print("\n" + "="*80)
    print("FLEET & SCALE INTELLIGENCE")
    print("="*80)
    
    fleets = [(c.company_name, c.fleet_size_estimate) for c in competitors if c.fleet_size_estimate]
    if fleets:
        print(f"\n[Fleet Sizes]")
        for name, size in sorted(fleets, key=lambda x: x[1], reverse=True):
            if size >= 1000:
                scale = "[ENTERPRISE]"
            elif size >= 100:
                scale = "[MID-SIZE]"
            else:
                scale = "[BOUTIQUE/P2P]"
            print(f"   {name}: {size:,} vehicles {scale}")
    
    # === RENTAL TERMS INSIGHTS ===
    print("\n" + "="*80)
    print("RENTAL TERMS INTELLIGENCE")
    print("="*80)
    
    min_rentals = [(c.company_name, c.min_rental_days) for c in competitors if c.min_rental_days]
    if min_rentals:
        print(f"\n[Minimum Rental Periods]")
        for name, days in sorted(min_rentals, key=lambda x: x[1]):
            flexibility = "[FLEXIBLE]" if days == 1 else "[STANDARD]" if days <= 2 else "[RESTRICTIVE]"
            print(f"   {name}: {days} day(s) {flexibility}")
    
    mileage_policies = [(c.company_name, c.mileage_limit_km, c.mileage_cost_per_km) for c in competitors if c.mileage_limit_km is not None]
    if mileage_policies:
        print(f"\n[Mileage Policies]")
        for name, limit, cost in mileage_policies:
            if limit == 0:
                print(f"   {name}: Unlimited [BEST FOR ROAD TRIPS]")
            else:
                overage = f"EUR{cost:.2f}/km overage" if cost else "overage charges apply"
                print(f"   {name}: {limit} km/day, {overage}")
    
    # === VALUE ANALYSIS ===
    print("\n" + "="*80)
    print("VALUE PROPOSITION ANALYSIS")
    print("="*80)
    
    print("\n[Best Overall Value]")
    # Calculate value score: price + insurance + cleaning - discounts
    value_scores = []
    for c in competitors:
        if c.base_nightly_rate:
            daily_cost = c.base_nightly_rate
            if c.insurance_cost_per_day:
                daily_cost += c.insurance_cost_per_day
            
            weekly_value = daily_cost * 7
            if c.weekly_discount_pct:
                weekly_value *= (1 - c.weekly_discount_pct/100)
            
            cleaning = c.cleaning_fee or 0
            total_week_cost = weekly_value + cleaning
            
            value_scores.append({
                'name': c.company_name,
                'total': total_week_cost,
                'daily': total_week_cost / 7,
                'rating': c.customer_review_avg or 0
            })
    
    if value_scores:
        # Sort by daily cost (lower is better)
        for i, score in enumerate(sorted(value_scores, key=lambda x: x['daily'])[:3], 1):
            rating_str = f"{score['rating']:.1f} stars" if score['rating'] else "No rating"
            print(f"   {i}. {score['name']}: EUR{score['daily']:.2f}/day (7-day trip) - {rating_str}")
    
    # === MARKET SEGMENTS ===
    print("\n" + "="*80)
    print("MARKET SEGMENTATION")
    print("="*80)
    
    print(f"\n[Competitive Positioning]")
    for c in competitors:
        if c.base_nightly_rate:
            # Determine segment
            price = c.base_nightly_rate
            rating = c.customer_review_avg or 0
            
            if price < 100 and rating >= 4.5:
                segment = "[BUDGET PREMIUM]"
            elif price < 100:
                segment = "[BUDGET]"
            elif price >= 200:
                segment = "[PREMIUM]"
            else:
                segment = "[MID-MARKET]"
            
            print(f"   {c.company_name}: {segment} (EUR{price:.0f}/night, {rating:.1f} stars)")
    
    # === DATA QUALITY ===
    print("\n" + "="*80)
    print("DATA QUALITY METRICS")
    print("="*80)
    
    completeness_scores = [(c.company_name, c.data_completeness_pct) for c in competitors]
    avg_completeness = statistics.mean([s[1] for s in completeness_scores])
    
    print(f"\n[Average Data Completeness]: {avg_completeness:.1f}%")
    print(f"\n[By Competitor]")
    for name, score in sorted(completeness_scores, key=lambda x: x[1], reverse=True):
        quality = "[EXCELLENT]" if score >= 65 else "[GOOD]" if score >= 50 else "[FAIR]" if score >= 35 else "[POOR]"
        print(f"   {name}: {score:.1f}% {quality}")
    
    # === KEY INSIGHTS SUMMARY ===
    print("\n" + "="*80)
    print("KEY STRATEGIC INSIGHTS")
    print("="*80)
    
    if prices:
        lowest_price_comp = min(competitors, key=lambda x: x.base_nightly_rate or 999)
        highest_rated = max([c for c in competitors if c.customer_review_avg], key=lambda x: x.customer_review_avg)
        
        print(f"\n1. PRICE LEADERSHIP: {lowest_price_comp.company_name} offers the lowest base rate (EUR{lowest_price_comp.base_nightly_rate:.2f}/night)")
        print(f"2. QUALITY LEADERSHIP: {highest_rated.company_name} has the highest customer rating ({highest_rated.customer_review_avg:.1f} stars)")
        
        if insurance_costs:
            best_insurance = min([c for c in competitors if c.insurance_cost_per_day], key=lambda x: x.insurance_cost_per_day)
            print(f"3. INSURANCE VALUE: {best_insurance.company_name} offers most affordable insurance (EUR{best_insurance.insurance_cost_per_day:.2f}/day)")
        
        if monthly_discounts:
            best_longterm = max([c for c in competitors if c.monthly_discount_pct], key=lambda x: x.monthly_discount_pct)
            print(f"4. LONG-TERM VALUE: {best_longterm.company_name} offers best monthly discount ({best_longterm.monthly_discount_pct:.0f}%)")
        
        unlimited_mileage = [c for c in competitors if c.mileage_limit_km == 0]
        if unlimited_mileage:
            print(f"5. ROAD TRIP WINNERS: {', '.join([c.company_name for c in unlimited_mileage])} offer unlimited mileage")
    
    print("\n" + "="*80)
    print("Report Complete - Use these insights for strategic positioning!")
    print("="*80 + "\n")
    
    session.close()

if __name__ == "__main__":
    generate_comprehensive_insights()
