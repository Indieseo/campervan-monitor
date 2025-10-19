"""
Daily Scraping Runner - All 8 Tier 1 Competitors
Collects data and saves to database for dashboard display
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.tier1_scrapers import (
    # European
    RoadsurferScraper, McRentScraper, GoboonyScrap,
    YescapaScraper, CamperdaysScraper,
    # US
    OutdoorsyScraper, RVshareScraper, CruiseAmericaScraper
)
from database.models import get_session, CompetitorPrice, init_database

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def scrape_and_save_all():
    """Scrape all 8 Tier 1 competitors and save to database"""

    # Initialize database
    init_database()

    scrapers = [
        # European competitors
        RoadsurferScraper(use_browserless=False),
        GoboonyScrap(use_browserless=False),
        YescapaScraper(use_browserless=False),
        McRentScraper(use_browserless=False),
        CamperdaysScraper(use_browserless=False),
        # US competitors
        OutdoorsyScraper(use_browserless=False),
        RVshareScraper(use_browserless=False),
        CruiseAmericaScraper(use_browserless=False)
    ]

    print("\n" + "="*70)
    print("DAILY SCRAPING RUN - 8 TIER 1 COMPETITORS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    session = get_session()
    successful = 0
    failed = 0

    for scraper in scrapers:
        print(f"\n{'='*70}")
        print(f"Scraping {scraper.company_name}...")
        print('='*70)

        try:
            # Scrape data
            data = await scraper.scrape()

            # Add tier information
            data['tier'] = 1  # All are Tier 1
            data['scrape_timestamp'] = datetime.now()

            # Save to database
            price_record = CompetitorPrice(**data)
            session.add(price_record)
            session.commit()

            print(f"[OK] {scraper.company_name} - Saved to database")
            print(f"  Completeness: {data['data_completeness_pct']:.1f}%")
            print(f"  Base Rate: {data['currency']} {data['base_nightly_rate'] or 'N/A'}")
            successful += 1

        except Exception as e:
            print(f"[FAIL] {scraper.company_name} - Error: {str(e)[:200]}")
            failed += 1

        # Small delay between scrapers
        await asyncio.sleep(2)

    session.close()

    # Summary
    print(f"\n{'='*70}")
    print("SCRAPING COMPLETE")
    print(f"{'='*70}")
    print(f"Successful: {successful}/8")
    print(f"Failed: {failed}/8")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    return successful, failed


if __name__ == "__main__":
    print("\nIndie Campers Competitive Intelligence")
    print("Running daily scraping job...\n")

    successful, failed = asyncio.run(scrape_and_save_all())

    if successful >= 6:
        print("[OK] Daily scraping completed successfully!")
        sys.exit(0)
    elif successful >= 4:
        print("[WARN] Daily scraping completed with some errors")
        sys.exit(0)
    else:
        print("[FAIL] Daily scraping failed - too many errors")
        sys.exit(1)
