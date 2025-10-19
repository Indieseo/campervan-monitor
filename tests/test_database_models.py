"""
Comprehensive Test Suite for Database Models
Tests all database operations, models, and data integrity
"""

import unittest
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import json

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from database.models import (
    init_database,
    get_session,
    add_price_record,
    get_latest_prices,
    get_market_summary,
    get_active_alerts,
    calculate_data_completeness,
    CompetitorPrice,
    CompetitorIntelligence,
    MarketIntelligence,
    PriceAlert,
    Base
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestDatabaseInitialization(unittest.TestCase):
    """Test database initialization"""
    
    def setUp(self):
        """Create a temporary database for testing"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        self.engine = create_engine(f'sqlite:///{self.temp_db_path}')
    
    def tearDown(self):
        """Clean up temporary database"""
        # Close all sessions and dispose of engine
        if hasattr(self, 'session') and self.session:
            self.session.close()
        if hasattr(self, 'engine') and self.engine:
            self.engine.dispose()

        # Small delay for Windows to release file handle
        import time
        time.sleep(0.1)

        if os.path.exists(self.temp_db_path):
            try:
                os.unlink(self.temp_db_path)
            except PermissionError:
                # File still in use, skip cleanup
                pass
    
    def test_init_database_creates_tables(self):
        """Test that database initialization creates all tables"""
        Base.metadata.create_all(self.engine)

        # Check that all tables exist
        from sqlalchemy import inspect
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()

        self.assertIn('competitor_prices', table_names)
        self.assertIn('competitor_intelligence', table_names)
        self.assertIn('market_intelligence', table_names)
        self.assertIn('price_alerts', table_names)
    
    def test_database_schema_completeness(self):
        """Test that all expected columns exist in tables"""
        Base.metadata.create_all(self.engine)
        
        # Check CompetitorPrice table
        price_columns = [c.name for c in CompetitorPrice.__table__.columns]
        required_columns = [
            'id', 'company_name', 'scrape_timestamp', 'tier',
            'base_nightly_rate', 'weekend_premium_pct', 'currency',
            'mileage_limit_km', 'vehicle_types', 'locations_available'
        ]
        
        for col in required_columns:
            self.assertIn(col, price_columns, f"Missing column: {col}")


class TestCompetitorPriceModel(unittest.TestCase):
    """Test CompetitorPrice model CRUD operations"""
    
    def setUp(self):
        """Create a temporary database for testing"""
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

    def test_create_price_record(self):
        """Test creating a new price record"""
        price = CompetitorPrice(
            company_name='Test Company',
            tier=1,
            base_nightly_rate=95.0,
            currency='EUR',
            scrape_timestamp=datetime.now()
        )
        
        self.session.add(price)
        self.session.commit()
        
        # Verify record was created
        retrieved = self.session.query(CompetitorPrice).filter_by(
            company_name='Test Company'
        ).first()
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.company_name, 'Test Company')
        self.assertEqual(retrieved.base_nightly_rate, 95.0)
    
    def test_create_price_with_all_fields(self):
        """Test creating a price record with all fields populated"""
        price = CompetitorPrice(
            company_name='Roadsurfer',
            tier=1,
            base_nightly_rate=125.0,
            weekend_premium_pct=15.0,
            seasonal_multiplier=1.2,
            currency='EUR',
            early_bird_discount_pct=10.0,
            weekly_discount_pct=15.0,
            monthly_discount_pct=25.0,
            insurance_cost_per_day=20.0,
            cleaning_fee=50.0,
            booking_fee=15.0,
            mileage_limit_km=200,
            mileage_cost_per_km=0.25,
            fuel_policy='full-to-full',
            min_rental_days=3,
            fleet_size_estimate=150,
            vehicles_available=45,
            vehicle_types=json.dumps(['Van', 'Motorhome', 'Campervan']),
            vehicle_features=json.dumps(['Kitchen', 'Shower', 'Bed']),
            popular_vehicle_type='Campervan',
            locations_available=json.dumps(['Berlin', 'Munich', 'Hamburg']),
            popular_routes=json.dumps(['Germany Tour', 'Alps Route']),
            one_way_rental_allowed=True,
            one_way_fee=100.0,
            active_promotions=json.dumps([{'text': '20% off summer'}]),
            promotion_text='Summer Sale',
            discount_code_available=True,
            referral_program=True,
            booking_process_steps=4,
            payment_options=json.dumps(['Credit Card', 'PayPal']),
            cancellation_policy='Flexible',
            customer_review_avg=4.5,
            review_count=1250,
            data_source_url='https://roadsurfer.com',
            scraping_strategy_used='interactive',
            data_completeness_pct=95.0,
            is_estimated=False,
            notes='Full scrape successful'
        )
        
        self.session.add(price)
        self.session.commit()
        
        # Verify all fields
        retrieved = self.session.query(CompetitorPrice).filter_by(
            company_name='Roadsurfer'
        ).first()
        
        self.assertEqual(retrieved.base_nightly_rate, 125.0)
        self.assertEqual(retrieved.weekend_premium_pct, 15.0)
        self.assertEqual(retrieved.insurance_cost_per_day, 20.0)
        self.assertEqual(retrieved.customer_review_avg, 4.5)
        self.assertEqual(retrieved.data_completeness_pct, 95.0)
    
    def test_update_price_record(self):
        """Test updating an existing price record"""
        price = CompetitorPrice(
            company_name='Test Company',
            tier=1,
            base_nightly_rate=100.0
        )
        self.session.add(price)
        self.session.commit()
        
        # Update the price
        price.base_nightly_rate = 110.0
        self.session.commit()
        
        # Verify update
        retrieved = self.session.query(CompetitorPrice).filter_by(
            company_name='Test Company'
        ).first()
        self.assertEqual(retrieved.base_nightly_rate, 110.0)
    
    def test_delete_price_record(self):
        """Test deleting a price record"""
        price = CompetitorPrice(
            company_name='Test Company',
            tier=1,
            base_nightly_rate=100.0
        )
        self.session.add(price)
        self.session.commit()
        
        # Delete the record
        self.session.delete(price)
        self.session.commit()
        
        # Verify deletion
        retrieved = self.session.query(CompetitorPrice).filter_by(
            company_name='Test Company'
        ).first()
        self.assertIsNone(retrieved)
    
    def test_query_by_tier(self):
        """Test querying prices by tier"""
        # Add multiple records with different tiers
        for tier in [1, 1, 2, 2, 3]:
            price = CompetitorPrice(
                company_name=f'Company Tier {tier}',
                tier=tier,
                base_nightly_rate=100.0
            )
            self.session.add(price)
        self.session.commit()
        
        # Query Tier 1
        tier1_prices = self.session.query(CompetitorPrice).filter_by(tier=1).all()
        self.assertEqual(len(tier1_prices), 2)
    
    def test_query_latest_prices(self):
        """Test querying latest prices ordered by timestamp"""
        # Add records with different timestamps
        now = datetime.now()
        for i in range(5):
            price = CompetitorPrice(
                company_name=f'Company {i}',
                tier=1,
                base_nightly_rate=100.0,
                scrape_timestamp=now - timedelta(days=i)
            )
            self.session.add(price)
        self.session.commit()
        
        # Query latest 3
        latest = self.session.query(CompetitorPrice)\
            .order_by(CompetitorPrice.scrape_timestamp.desc())\
            .limit(3)\
            .all()
        
        self.assertEqual(len(latest), 3)
        self.assertEqual(latest[0].company_name, 'Company 0')  # Most recent


class TestMarketIntelligenceModel(unittest.TestCase):
    """Test MarketIntelligence model"""
    
    def setUp(self):
        """Create a temporary database for testing"""
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

    def test_create_market_intelligence(self):
        """Test creating market intelligence record"""
        intel = MarketIntelligence(
            market_avg_price=95.0,
            market_median_price=90.0,
            price_range_min=60.0,
            price_range_max=150.0,
            market_volatility=12.5,
            indie_campers_rank=3,
            indie_campers_price=85.0,
            trend_direction='stable',
            market_summary='Market is stable with good competition'
        )
        
        self.session.add(intel)
        self.session.commit()
        
        # Verify
        retrieved = self.session.query(MarketIntelligence).first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.market_avg_price, 95.0)
        self.assertEqual(retrieved.indie_campers_rank, 3)


class TestPriceAlertModel(unittest.TestCase):
    """Test PriceAlert model"""
    
    def setUp(self):
        """Create a temporary database for testing"""
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

    def test_create_price_alert(self):
        """Test creating a price alert"""
        alert = PriceAlert(
            alert_type='price_drop',
            severity='high',
            company_name='Roadsurfer',
            old_value=100.0,
            new_value=85.0,
            change_pct=-15.0,
            alert_message='Price dropped 15%',
            recommended_action='Review pricing strategy'
        )
        
        self.session.add(alert)
        self.session.commit()
        
        # Verify
        retrieved = self.session.query(PriceAlert).first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.alert_type, 'price_drop')
        self.assertEqual(retrieved.severity, 'high')
        self.assertFalse(retrieved.is_acknowledged)
    
    def test_acknowledge_alert(self):
        """Test acknowledging an alert"""
        alert = PriceAlert(
            alert_type='price_drop',
            severity='high',
            company_name='Test Company',
            alert_message='Test alert'
        )
        self.session.add(alert)
        self.session.commit()
        
        # Acknowledge alert
        alert.is_acknowledged = True
        alert.action_taken = 'Reviewed and adjusted pricing'
        alert.resolved_at = datetime.now()
        self.session.commit()
        
        # Verify
        retrieved = self.session.query(PriceAlert).first()
        self.assertTrue(retrieved.is_acknowledged)
        self.assertIsNotNone(retrieved.resolved_at)
    
    def test_query_unacknowledged_alerts(self):
        """Test querying only unacknowledged alerts"""
        # Add multiple alerts
        for i in range(5):
            alert = PriceAlert(
                alert_type='price_drop',
                severity='medium',
                company_name=f'Company {i}',
                alert_message=f'Alert {i}',
                is_acknowledged=(i % 2 == 0)  # Acknowledge even-numbered alerts
            )
            self.session.add(alert)
        self.session.commit()
        
        # Query unacknowledged
        unack = self.session.query(PriceAlert)\
            .filter_by(is_acknowledged=False)\
            .all()
        
        self.assertEqual(len(unack), 2)  # Should have 2 unacknowledged (1, 3)


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and constraints"""
    
    def setUp(self):
        """Create a temporary database for testing"""
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

    def test_json_fields_serialization(self):
        """Test that JSON fields are properly serialized"""
        price = CompetitorPrice(
            company_name='Test',
            tier=1,
            vehicle_types=json.dumps(['Van', 'Motorhome']),
            locations_available=json.dumps(['Berlin', 'Munich']),
            active_promotions=json.dumps([{'text': 'Summer sale', 'discount': 20}])
        )
        
        self.session.add(price)
        self.session.commit()
        
        # Retrieve and verify JSON fields
        retrieved = self.session.query(CompetitorPrice).first()
        vehicle_types = json.loads(retrieved.vehicle_types)
        locations = json.loads(retrieved.locations_available)
        promos = json.loads(retrieved.active_promotions)
        
        self.assertEqual(len(vehicle_types), 2)
        self.assertIn('Van', vehicle_types)
        self.assertEqual(len(locations), 2)
        self.assertEqual(promos[0]['discount'], 20)
    
    def test_timestamp_auto_population(self):
        """Test that timestamps are auto-populated"""
        price = CompetitorPrice(
            company_name='Test',
            tier=1
        )
        self.session.add(price)
        self.session.commit()
        
        # Verify timestamp was set
        retrieved = self.session.query(CompetitorPrice).first()
        self.assertIsNotNone(retrieved.scrape_timestamp)
        self.assertIsInstance(retrieved.scrape_timestamp, datetime)


def run_all_tests():
    """Run all database tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestCompetitorPriceModel))
    suite.addTests(loader.loadTestsFromTestCase(TestMarketIntelligenceModel))
    suite.addTests(loader.loadTestsFromTestCase(TestPriceAlertModel))
    suite.addTests(loader.loadTestsFromTestCase(TestDataIntegrity))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 DATABASE TESTS SUMMARY")
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











