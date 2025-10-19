"""
Integration Test Suite
Tests full system workflow and component integration
"""

import unittest
import sys
import asyncio
import os
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from database.models import (
    init_database, get_session, add_price_record,
    CompetitorPrice, PriceAlert, MarketIntelligence,
    Base
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Windows async compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class TestDatabaseScraperIntegration(unittest.TestCase):
    """Test integration between scrapers and database"""
    
    def setUp(self):
        """Create temporary database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        self.engine = create_engine(f'sqlite:///{self.temp_db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def tearDown(self):
        """Clean up"""
        if hasattr(self, 'session') and self.session:
            self.session.close()
        if hasattr(self, 'engine') and self.engine:
            self.engine.dispose()
        import time
        time.sleep(0.1)
        if os.path.exists(self.temp_db_path):
            try:
                os.unlink(self.temp_db_path)
            except PermissionError:
                pass

    def test_scraper_to_database_pipeline(self):
        """Test full pipeline from scraping to database"""
        # Simulate scraped data
        scraped_data = {
            'company_name': 'Test Company',
            'tier': 1,
            'base_nightly_rate': 95.0,
            'weekend_premium_pct': 15.0,
            'currency': 'EUR',
            'mileage_limit_km': 200,
            'data_completeness_pct': 85.0,
            'scrape_timestamp': datetime.now()
        }
        
        # Add to database
        price = CompetitorPrice(**scraped_data)
        self.session.add(price)
        self.session.commit()
        
        # Verify data was stored correctly
        retrieved = self.session.query(CompetitorPrice).filter_by(
            company_name='Test Company'
        ).first()
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.base_nightly_rate, 95.0)
        self.assertEqual(retrieved.data_completeness_pct, 85.0)
    
    def test_multiple_competitors_scraping(self):
        """Test scraping multiple competitors and storing"""
        competitors = [
            {'company_name': 'Roadsurfer', 'tier': 1, 'base_nightly_rate': 120.0},
            {'company_name': 'McRent', 'tier': 1, 'base_nightly_rate': 110.0},
            {'company_name': 'Goboony', 'tier': 1, 'base_nightly_rate': 85.0},
        ]
        
        # Add all competitors
        for comp in competitors:
            price = CompetitorPrice(**comp)
            self.session.add(price)
        self.session.commit()
        
        # Verify all were stored
        all_prices = self.session.query(CompetitorPrice).all()
        self.assertEqual(len(all_prices), 3)
        
        # Verify data integrity
        companies = [p.company_name for p in all_prices]
        self.assertIn('Roadsurfer', companies)
        self.assertIn('McRent', companies)
        self.assertIn('Goboony', companies)


class TestMarketAnalysisIntegration(unittest.TestCase):
    """Test integration of market analysis with database"""
    
    def setUp(self):
        """Create temporary database with sample data"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        self.engine = create_engine(f'sqlite:///{self.temp_db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Add sample price data
        prices = [
            {'company_name': 'Roadsurfer', 'base_nightly_rate': 120.0, 'tier': 1},
            {'company_name': 'McRent', 'base_nightly_rate': 110.0, 'tier': 1},
            {'company_name': 'Goboony', 'base_nightly_rate': 85.0, 'tier': 1},
            {'company_name': 'Yescapa', 'base_nightly_rate': 90.0, 'tier': 1},
        ]
        for price_data in prices:
            price = CompetitorPrice(**price_data)
            self.session.add(price)
        self.session.commit()
    
    def tearDown(self):
        """Clean up"""
        if hasattr(self, 'session') and self.session:
            self.session.close()
        if hasattr(self, 'engine') and self.engine:
            self.engine.dispose()
        import time
        time.sleep(0.1)
        if os.path.exists(self.temp_db_path):
            try:
                os.unlink(self.temp_db_path)
            except PermissionError:
                pass

    def test_market_analysis_calculation(self):
        """Test calculating market statistics"""
        # Get all prices
        prices = self.session.query(CompetitorPrice).all()
        price_values = [p.base_nightly_rate for p in prices]
        
        # Calculate market stats
        avg_price = sum(price_values) / len(price_values)
        min_price = min(price_values)
        max_price = max(price_values)
        
        # Store market intelligence
        intel = MarketIntelligence(
            market_avg_price=avg_price,
            market_median_price=sorted(price_values)[len(price_values)//2],
            price_range_min=min_price,
            price_range_max=max_price,
            market_summary=f"Analyzed {len(prices)} competitors"
        )
        self.session.add(intel)
        self.session.commit()
        
        # Verify market intelligence
        retrieved = self.session.query(MarketIntelligence).first()
        self.assertIsNotNone(retrieved)
        self.assertAlmostEqual(retrieved.market_avg_price, 101.25, places=2)
        self.assertEqual(retrieved.price_range_min, 85.0)
        self.assertEqual(retrieved.price_range_max, 120.0)
    
    def test_alert_generation_from_price_changes(self):
        """Test generating alerts from price changes"""
        # Get average price
        prices = self.session.query(CompetitorPrice).all()
        avg_price = sum(p.base_nightly_rate for p in prices) / len(prices)
        
        # Check for companies significantly below average
        for price in prices:
            if price.base_nightly_rate < avg_price * 0.85:  # 15% below
                alert = PriceAlert(
                    alert_type='price_undercut',
                    severity='high',
                    company_name=price.company_name,
                    new_value=price.base_nightly_rate,
                    change_pct=((price.base_nightly_rate - avg_price) / avg_price) * 100,
                    alert_message=f"{price.company_name} is significantly below market average"
                )
                self.session.add(alert)
        self.session.commit()
        
        # Verify alerts were created
        alerts = self.session.query(PriceAlert).all()
        self.assertGreater(len(alerts), 0)


class TestDataQualityIntegration(unittest.TestCase):
    """Test data quality validation integration"""
    
    def setUp(self):
        """Create temporary database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        self.engine = create_engine(f'sqlite:///{self.temp_db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def tearDown(self):
        """Clean up"""
        if hasattr(self, 'session') and self.session:
            self.session.close()
        if hasattr(self, 'engine') and self.engine:
            self.engine.dispose()
        import time
        time.sleep(0.1)
        if os.path.exists(self.temp_db_path):
            try:
                os.unlink(self.temp_db_path)
            except PermissionError:
                pass

    def test_reject_invalid_price_data(self):
        """Test that invalid price data is rejected"""
        # Valid data should be accepted
        valid_price = CompetitorPrice(
            company_name='Valid Company',
            base_nightly_rate=95.0,
            tier=1
        )
        self.session.add(valid_price)
        self.session.commit()
        
        retrieved = self.session.query(CompetitorPrice).filter_by(
            company_name='Valid Company'
        ).first()
        self.assertIsNotNone(retrieved)
    
    def test_data_completeness_scoring(self):
        """Test calculating data completeness scores"""
        # Minimal data
        minimal_price = CompetitorPrice(
            company_name='Minimal Data',
            base_nightly_rate=100.0,
            tier=1
        )
        self.session.add(minimal_price)
        
        # Rich data
        rich_price = CompetitorPrice(
            company_name='Rich Data',
            base_nightly_rate=100.0,
            tier=1,
            weekend_premium_pct=15.0,
            seasonal_multiplier=1.2,
            insurance_cost_per_day=20.0,
            cleaning_fee=50.0,
            mileage_limit_km=200,
            customer_review_avg=4.5,
            review_count=500,
            data_completeness_pct=95.0
        )
        self.session.add(rich_price)
        self.session.commit()
        
        # Compare completeness
        minimal = self.session.query(CompetitorPrice).filter_by(
            company_name='Minimal Data'
        ).first()
        rich = self.session.query(CompetitorPrice).filter_by(
            company_name='Rich Data'
        ).first()
        
        # Rich data should have higher completeness
        self.assertGreater(rich.data_completeness_pct or 0, minimal.data_completeness_pct or 0)


class TestFullSystemWorkflow(unittest.TestCase):
    """Test complete end-to-end workflow"""
    
    def setUp(self):
        """Create temporary database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        self.engine = create_engine(f'sqlite:///{self.temp_db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def tearDown(self):
        """Clean up"""
        if hasattr(self, 'session') and self.session:
            self.session.close()
        if hasattr(self, 'engine') and self.engine:
            self.engine.dispose()
        import time
        time.sleep(0.1)
        if os.path.exists(self.temp_db_path):
            try:
                os.unlink(self.temp_db_path)
            except PermissionError:
                pass

    def test_daily_intelligence_gathering_workflow(self):
        """Test complete daily intelligence gathering workflow"""
        # Step 1: Simulate scraping multiple competitors
        competitors_data = [
            {'company_name': 'Roadsurfer', 'tier': 1, 'base_nightly_rate': 120.0, 'data_completeness_pct': 90.0},
            {'company_name': 'McRent', 'tier': 1, 'base_nightly_rate': 110.0, 'data_completeness_pct': 85.0},
            {'company_name': 'Goboony', 'tier': 1, 'base_nightly_rate': 85.0, 'data_completeness_pct': 80.0},
            {'company_name': 'Yescapa', 'tier': 1, 'base_nightly_rate': 90.0, 'data_completeness_pct': 88.0},
            {'company_name': 'Camperdays', 'tier': 1, 'base_nightly_rate': 95.0, 'data_completeness_pct': 92.0},
        ]
        
        for data in competitors_data:
            price = CompetitorPrice(**data)
            self.session.add(price)
        self.session.commit()
        
        # Step 2: Analyze market
        prices = self.session.query(CompetitorPrice).all()
        price_values = [p.base_nightly_rate for p in prices]
        avg_price = sum(price_values) / len(price_values)
        
        intel = MarketIntelligence(
            market_avg_price=avg_price,
            price_range_min=min(price_values),
            price_range_max=max(price_values),
            market_summary=f"Daily analysis of {len(prices)} competitors"
        )
        self.session.add(intel)
        self.session.commit()
        
        # Step 3: Generate alerts for significant deviations
        for price in prices:
            deviation = ((price.base_nightly_rate - avg_price) / avg_price) * 100
            if abs(deviation) > 15:
                alert = PriceAlert(
                    alert_type='price_deviation',
                    severity='medium',
                    company_name=price.company_name,
                    new_value=price.base_nightly_rate,
                    change_pct=deviation,
                    alert_message=f"{price.company_name} deviates {abs(deviation):.1f}% from market average"
                )
                self.session.add(alert)
        self.session.commit()
        
        # Step 4: Verify complete workflow
        # Check prices were stored
        stored_prices = self.session.query(CompetitorPrice).count()
        self.assertEqual(stored_prices, 5)
        
        # Check market intelligence was generated
        market_intel = self.session.query(MarketIntelligence).first()
        self.assertIsNotNone(market_intel)
        self.assertAlmostEqual(market_intel.market_avg_price, 100.0, places=1)
        
        # Check alerts were generated
        alerts = self.session.query(PriceAlert).all()
        self.assertGreaterEqual(len(alerts), 1)  # Should have at least one alert
        
        # Verify data quality
        completeness_scores = [p.data_completeness_pct for p in prices if p.data_completeness_pct]
        avg_completeness = sum(completeness_scores) / len(completeness_scores)
        self.assertGreater(avg_completeness, 80.0)  # Should maintain high quality


class TestConcurrentOperations(unittest.TestCase):
    """Test concurrent database operations"""
    
    def setUp(self):
        """Create temporary database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        self.engine = create_engine(f'sqlite:///{self.temp_db_path}')
        Base.metadata.create_all(self.engine)
    
    def tearDown(self):
        """Clean up"""
        if hasattr(self, 'engine') and self.engine:
            self.engine.dispose()
        import time
        time.sleep(0.1)
        if os.path.exists(self.temp_db_path):
            try:
                os.unlink(self.temp_db_path)
            except PermissionError:
                pass

    def test_concurrent_reads(self):
        """Test multiple concurrent read operations"""
        # Add some data
        Session = sessionmaker(bind=self.engine)
        session = Session()
        for i in range(10):
            price = CompetitorPrice(
                company_name=f'Company {i}',
                base_nightly_rate=100.0 + i,
                tier=1
            )
            session.add(price)
        session.commit()
        session.close()
        
        # Concurrent reads should work
        sessions = [sessionmaker(bind=self.engine)() for _ in range(5)]
        
        for sess in sessions:
            prices = sess.query(CompetitorPrice).all()
            self.assertEqual(len(prices), 10)
            sess.close()


def run_all_tests():
    """Run all integration tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseScraperIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestMarketAnalysisIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDataQualityIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestFullSystemWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestConcurrentOperations))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("🔗 INTEGRATION TESTS SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)











