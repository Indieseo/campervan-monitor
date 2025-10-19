"""
Focused Competitor Configuration - Quality Over Quantity
10-15 key Indie Campers competitors with deep data collection
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class CompetitorConfig:
    """Rich competitor configuration"""
    name: str
    tier: int  # 1=Daily, 2=Weekly, 3=Monthly
    country: str
    business_model: str
    urls: Dict[str, str]
    target_data_points: List[str]
    scraping_strategy: str
    priority_score: int  # 1-10


# Core Competitors - Tier 1 (Daily Monitoring)
TIER_1_COMPETITORS = [
    {
        'name': 'Roadsurfer',
        'tier': 1,
        'country': 'Germany',
        'business_model': 'Own Fleet + P2P Hybrid',
        'priority_score': 10,
        'urls': {
            'homepage': 'https://roadsurfer.com/',
            'search': 'https://roadsurfer.com/',
            'pricing': 'https://roadsurfer.com/',
            'vehicles': 'https://roadsurfer.com/',
            'booking': 'https://roadsurfer.com/',
            'locations': 'https://roadsurfer.com/'
        },
        'target_data_points': [
            'base_nightly_rate',
            'weekend_premium_pct',
            'seasonal_multiplier',
            'active_promotions',
            'early_bird_discount',
            'insurance_cost',
            'cleaning_fee',
            'mileage_limit',
            'fleet_size_estimate',
            'vehicle_types',
            'booking_availability',
            'popular_routes',
            'customer_review_avg',
            'website_ux_score',
            'mobile_app_rating'
        ],
        'scraping_strategy': 'interactive_booking_flow',
        'notes': 'Main competitor - similar model, strong brand'
    },
    {
        'name': 'McRent',
        'tier': 1,
        'country': 'Germany',
        'business_model': 'Traditional Rental (Own Fleet)',
        'priority_score': 9,
        'urls': {
            'homepage': 'https://www.mcrent.de/',
            'search': 'https://www.mcrent.de/en/motorhome-rental/germany',
            'pricing': 'https://www.mcrent.de/',
            'vehicles': 'https://www.mcrent.de/',
            'booking': 'https://www.mcrent.de/'
        },
        'target_data_points': [
            'base_nightly_rate',
            'weekly_discount_pct',
            'monthly_discount_pct',
            'insurance_packages',
            'addon_costs',
            'vehicle_types',
            'location_coverage',
            'one_way_fees',
            'cancellation_policy',
            'booking_process_steps'
        ],
        'scraping_strategy': 'form_simulation',
        'notes': 'Established player - corporate/family focused'
    },
    {
        'name': 'Camperdays',
        'tier': 1,
        'country': 'Netherlands',
        'business_model': 'Booking Platform (Aggregator)',
        'priority_score': 8,
        'urls': {
            'homepage': 'https://www.camperdays.com/',
            'search': 'https://www.camperdays.com/en/motorhome-rental/germany/munich',
            'comparison': 'https://www.camperdays.com/'
        },
        'target_data_points': [
            'price_range_min',
            'price_range_max',
            'avg_market_price',
            'num_suppliers_listed',
            'top_ranked_suppliers',
            'filter_options',
            'booking_commission',
            'user_ratings_avg'
        ],
        'scraping_strategy': 'search_aggregation',
        'notes': 'Aggregator threat - shows all competitor prices'
    },
    {
        'name': 'Goboony',
        'tier': 1,
        'country': 'Netherlands',
        'business_model': 'P2P Platform',
        'priority_score': 9,
        'urls': {
            'homepage': 'https://www.goboony.com/',
            'search': 'https://www.goboony.com/',
            'pricing': 'https://www.goboony.com/'
        },
        'target_data_points': [
            'base_nightly_rate',
            'owner_commission_pct',
            'insurance_included',
            'platform_fee',
            'total_listings',
            'avg_listing_price',
            'popular_destinations',
            'cancellation_flexibility'
        ],
        'scraping_strategy': 'search_sampling',
        'notes': 'Direct P2P competitor - fast growing'
    },
    {
        'name': 'Yescapa',
        'tier': 1,
        'country': 'France',
        'business_model': 'P2P Platform',
        'priority_score': 8,
        'urls': {
            'homepage': 'https://www.yescapa.com/',
            'search': 'https://www.yescapa.com/',
            'pricing': 'https://www.yescapa.com/'
        },
        'target_data_points': [
            'base_nightly_rate',
            'platform_commission',
            'insurance_cost',
            'num_active_listings',
            'avg_response_time',
            'verification_level',
            'trust_score'
        ],
        'scraping_strategy': 'search_sampling',
        'notes': 'Strong in France/Spain - community driven'
    },
    {
        'name': 'Outdoorsy',
        'tier': 1,
        'country': 'United States',
        'business_model': 'P2P Platform',
        'priority_score': 10,
        'urls': {
            'homepage': 'https://www.outdoorsy.com/',
            'search': 'https://www.outdoorsy.com/rv-search?address=Los%20Angeles%2C%20CA',
            'pricing': 'https://www.outdoorsy.com/how-it-works/pricing'
        },
        'target_data_points': [
            'base_nightly_rate',
            'platform_commission',
            'insurance_cost',
            'service_fee',
            'total_listings',
            'avg_listing_price',
            'roadside_assistance',
            'cancellation_policy',
            'booking_protection'
        ],
        'scraping_strategy': 'search_sampling',
        'notes': 'Largest P2P RV rental in North America - direct competitor'
    },
    {
        'name': 'RVshare',
        'tier': 1,
        'country': 'United States',
        'business_model': 'P2P Platform',
        'priority_score': 10,
        'urls': {
            'homepage': 'https://www.rvshare.com/',
            'search': 'https://www.rvshare.com/rv-search?location=Los+Angeles,+CA',
            'pricing': 'https://www.rvshare.com/how-it-works'
        },
        'target_data_points': [
            'base_nightly_rate',
            'owner_fee',
            'service_fee',
            'insurance_included',
            'total_listings',
            'popular_destinations',
            'instant_book_available',
            'cancellation_flexibility'
        ],
        'scraping_strategy': 'search_sampling',
        'notes': 'Major US P2P platform - strong marketplace'
    },
    {
        'name': 'Cruise America',
        'tier': 1,
        'country': 'United States',
        'business_model': 'Traditional Rental (Own Fleet)',
        'priority_score': 9,
        'urls': {
            'homepage': 'https://www.cruiseamerica.com/',
            'search': 'https://www.cruiseamerica.com/',
            'pricing': 'https://www.cruiseamerica.com/',
            'locations': 'https://www.cruiseamerica.com/',
            'vehicles': 'https://www.cruiseamerica.com/'
        },
        'target_data_points': [
            'base_nightly_rate',
            'weekly_rate',
            'monthly_rate',
            'mileage_included',
            'insurance_packages',
            'convenience_kits',
            'generator_fee',
            'location_count',
            'fleet_size',
            'one_way_rentals'
        ],
        'scraping_strategy': 'form_simulation',
        'notes': 'Largest traditional RV rental in North America - 50+ years'
    }
]

# Major Players - Tier 2 (Weekly Monitoring)
TIER_2_COMPETITORS = [
    {
        'name': 'Campanda',
        'tier': 2,
        'country': 'Germany',
        'business_model': 'Aggregator Platform',
        'priority_score': 7,
        'urls': {
            'homepage': 'https://www.campanda.com/',
            'search': 'https://www.campanda.com/search'
        },
        'target_data_points': [
            'avg_market_price',
            'supplier_count',
            'geographic_coverage',
            'booking_flow_quality'
        ],
        'scraping_strategy': 'search_aggregation'
    },
    {
        'name': 'Motorhome Republic',
        'tier': 2,
        'country': 'Global',
        'business_model': 'Aggregator',
        'priority_score': 6,
        'urls': {
            'homepage': 'https://www.motorhomerepublic.com/',
            'search': 'https://www.motorhomerepublic.com/motorhome-hire'
        },
        'target_data_points': [
            'global_price_comparison',
            'regional_pricing',
            'supplier_diversity'
        ],
        'scraping_strategy': 'api_if_available'
    },
    {
        'name': 'Sun Living',
        'tier': 2,
        'country': 'Europe',
        'business_model': 'Manufacturer Direct',
        'priority_score': 6,
        'urls': {
            'homepage': 'https://www.sunliving.com/',
            'rental': 'https://www.sunliving.com/rental'
        },
        'target_data_points': [
            'manufacturer_pricing',
            'direct_rental_model',
            'fleet_composition'
        ],
        'scraping_strategy': 'standard_scrape'
    },
    {
        'name': 'Bunk Campers',
        'tier': 2,
        'country': 'Ireland/UK',
        'business_model': 'Regional Fleet',
        'priority_score': 7,
        'urls': {
            'homepage': 'https://www.bunkcampers.com/',
            'booking': 'https://www.bunkcampers.com/book'
        },
        'target_data_points': [
            'uk_ireland_pricing',
            'regional_strategy',
            'fleet_quality'
        ],
        'scraping_strategy': 'regional_focus'
    },
    {
        'name': 'Touring Cars',
        'tier': 2,
        'country': 'Belgium',
        'business_model': 'Regional Rental',
        'priority_score': 6,
        'urls': {
            'homepage': 'https://www.touring.be/',
            'campers': 'https://www.touring.be/campers'
        },
        'target_data_points': [
            'benelux_pricing',
            'membership_benefits',
            'loyalty_program'
        ],
        'scraping_strategy': 'standard_scrape'
    }
]

# Watch List - Tier 3 (Monthly Check)
TIER_3_COMPETITORS = [
    {
        'name': 'Spaceship',
        'tier': 3,
        'country': 'Australia/NZ',
        'business_model': 'Budget Fleet',
        'priority_score': 4,
        'urls': {
            'homepage': 'https://www.spaceshiprentals.com.au/'
        },
        'scraping_strategy': 'quarterly_check'
    },
    {
        'name': 'Apollo Campers',
        'tier': 3,
        'country': 'Global',
        'business_model': 'Large Fleet Operator',
        'priority_score': 5,
        'urls': {
            'homepage': 'https://www.apollocamper.com/'
        },
        'scraping_strategy': 'quarterly_check'
    },
    {
        'name': 'Jucy Rentals',
        'tier': 3,
        'country': 'NZ/Australia',
        'business_model': 'Budget Focused',
        'priority_score': 4,
        'urls': {
            'homepage': 'https://www.jucy.com/'
        },
        'scraping_strategy': 'quarterly_check'
    },
    {
        'name': 'Wild Campers',
        'tier': 3,
        'country': 'Europe',
        'business_model': 'Niche P2P',
        'priority_score': 5,
        'urls': {
            'homepage': 'https://www.wildcampers.com/'
        },
        'scraping_strategy': 'quarterly_check'
    },
    {
        'name': 'CamperBoys',
        'tier': 3,
        'country': 'Germany',
        'business_model': 'Regional Rental',
        'priority_score': 4,
        'urls': {
            'homepage': 'https://www.camperboys.com/'
        },
        'scraping_strategy': 'quarterly_check'
    }
]


def get_all_competitors() -> List[Dict]:
    """Get all competitors sorted by priority"""
    all_competitors = TIER_1_COMPETITORS + TIER_2_COMPETITORS + TIER_3_COMPETITORS
    return sorted(all_competitors, key=lambda x: x['priority_score'], reverse=True)


def get_by_tier(tier: int) -> List[Dict]:
    """Get competitors by monitoring tier"""
    all_competitors = get_all_competitors()
    return [c for c in all_competitors if c['tier'] == tier]


def get_daily_monitoring() -> List[Dict]:
    """Get Tier 1 competitors for daily monitoring"""
    return get_by_tier(1)


def get_competitor_by_name(name: str) -> Dict:
    """Get specific competitor config"""
    all_competitors = get_all_competitors()
    for comp in all_competitors:
        if comp['name'].lower() == name.lower():
            return comp
    return None


# Summary stats
def get_stats():
    """Get configuration statistics"""
    return {
        'total_competitors': len(get_all_competitors()),
        'tier_1_daily': len(TIER_1_COMPETITORS),
        'tier_2_weekly': len(TIER_2_COMPETITORS),
        'tier_3_monthly': len(TIER_3_COMPETITORS),
        'countries_covered': len(set(c['country'] for c in get_all_competitors())),
        'business_models': len(set(c['business_model'] for c in get_all_competitors()))
    }


if __name__ == "__main__":
    print("🎯 Focused Competitor Configuration")
    print("=" * 50)
    stats = get_stats()
    print(f"\nTotal Competitors: {stats['total_competitors']}")
    print(f"Tier 1 (Daily): {stats['tier_1_daily']}")
    print(f"Tier 2 (Weekly): {stats['tier_2_weekly']}")
    print(f"Tier 3 (Monthly): {stats['tier_3_monthly']}")
    print(f"\nCountries: {stats['countries_covered']}")
    print(f"Business Models: {stats['business_models']}")
    
    print("\n📊 Tier 1 Competitors (Daily Monitoring):")
    for comp in TIER_1_COMPETITORS:
        print(f"  • {comp['name']} ({comp['country']}) - Score: {comp['priority_score']}/10")
