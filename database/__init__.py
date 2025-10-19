"""
Deep Intelligence Database Models
35+ fields per competitor for quality insights
"""

from .models import (
    Base,
    CompetitorPrice,
    CompetitorIntelligence,
    MarketIntelligence,
    PriceAlert,
    init_database,
    get_session,
    add_price_record,
    get_latest_prices,
    get_market_summary,
    get_active_alerts,
    calculate_data_completeness
)

__version__ = "2.0.0"

# Handle Windows console encoding issues
try:
    print(f"🗄️ Intelligence Database v{__version__}")
    print("   Deep data collection • 35+ fields • Quality insights")
except UnicodeEncodeError:
    # Fallback for Windows console without UTF-8 support
    print(f"[DATABASE] Intelligence Database v{__version__}")
    print("   Deep data collection - 35+ fields - Quality insights")
