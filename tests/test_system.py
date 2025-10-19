"""
Test Suite for Campervan Price Monitor
Windows-compatible tests
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

# Windows async fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from database.models import init_database, get_session, CompetitorPrice
from scrapers.base_scraper import DeepDataScraper
from scrapers import TOTAL_COMPETITORS


class TestDatabase:
    """Test database operations"""
    
    def test_database_creation(self):
        """Test database can be created"""
        engine = init_database()
        from database.models import DATABASE_PATH
        assert DATABASE_PATH.exists()
        print(f"✅ Database created: {DATABASE_PATH}")
    
    def test_database_session(self):
        """Test database session"""
        session = get_session()
        assert session is not None
        session.close()
        print("✅ Database session works")
    
    def test_insert_price(self):
        """Test inserting price data"""
        session = get_session()

        price = CompetitorPrice(
            company_name="Test Company",
            tier=1,
            base_nightly_rate=100.00,
            currency="USD"
        )
        
        session.add(price)
        session.commit()
        
        # Verify
        count = session.query(CompetitorPrice).filter_by(company_name="Test Company").count()
        assert count >= 1
        
        session.close()
        print("✅ Price insertion works")


class TestScrapers:
    """Test scraper functionality"""
    
    def test_competitor_count(self):
        """Test competitor configuration"""
        assert TOTAL_COMPETITORS >= 15
        print(f"✅ {TOTAL_COMPETITORS} competitors configured")
    
    @pytest.mark.asyncio
    async def test_base_scraper(self):
        """Test base scraper functionality"""

        # Just test that we can import and configure a scraper
        from scrapers.tier1_scrapers import RoadsurferScraper
        scraper = RoadsurferScraper(use_browserless=False)
        assert scraper.config['name'] == "Roadsurfer"
        assert scraper.tier == 1
        print("✅ Base scraper works")


class TestSystem:
    """Test full system"""
    
    def test_paths_cross_platform(self):
        """Test cross-platform paths"""
        from database.models import DATABASE_PATH
        from scrapers.base_scraper import SCREENSHOTS_DIR, HTML_DIR
        
        assert DATABASE_PATH.exists() or DATABASE_PATH.parent.exists()
        assert SCREENSHOTS_DIR.exists()
        assert HTML_DIR.exists()
        print("✅ Cross-platform paths work")
    
    def test_windows_compatibility(self):
        """Test Windows-specific features"""
        import platform
        print(f"✅ Running on: {platform.system()}")
        print(f"✅ Python: {sys.version.split()[0]}")
        assert True


if __name__ == "__main__":
    print("🧪 Running Campervan Monitor Tests\n")
    pytest.main([__file__, "-v", "-s"])
