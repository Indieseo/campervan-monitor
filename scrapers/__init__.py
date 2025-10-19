"""
Focused Competitive Intelligence Scrapers
Quality over quantity - Deep insights from key competitors
"""

from .competitor_config import (
    get_all_competitors,
    get_by_tier,
    get_daily_monitoring,
    get_competitor_by_name,
    TIER_1_COMPETITORS,
    TIER_2_COMPETITORS,
    TIER_3_COMPETITORS
)

from .base_scraper import DeepDataScraper

from .tier1_scrapers import (
    RoadsurferScraper,
    McRentScraper,
    GoboonyScrap,
    YescapaScraper,
    CamperdaysScraper,
    scrape_tier_1_competitors
)

__version__ = "2.0.0"
__author__ = "Indie Campers Intelligence Team"

# Quick stats
TOTAL_COMPETITORS = 15
TIER_1_COUNT = 5
TIER_2_COUNT = 5
TIER_3_COUNT = 5
DATA_POINTS_PER_COMPETITOR = 35

import sys

# Handle Windows console encoding issues
try:
    print(f"🎯 Focused Intelligence Scrapers v{__version__}")
    print(f"   {TOTAL_COMPETITORS} competitors • {DATA_POINTS_PER_COMPETITOR} data points each")
except UnicodeEncodeError:
    # Fallback for Windows console without UTF-8 support
    print(f"[TARGET] Focused Intelligence Scrapers v{__version__}")
    print(f"   {TOTAL_COMPETITORS} competitors - {DATA_POINTS_PER_COMPETITOR} data points each")
