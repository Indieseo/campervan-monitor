"""
Comprehensive Test Suite for Scrapers
Tests scraper components, data extraction, and error handling
"""

import unittest
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, AsyncMock

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from scrapers.base_scraper import DeepDataScraper
from scrapers.competitor_config import get_competitor_by_name

# Windows async compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class TestScraperImplementation(DeepDataScraper):
    """Test implementation of abstract scraper"""
    
    def __init__(self):
        config = {
            'urls': {'homepage': 'https://example.com'},
            'tier': 1
        }
        super().__init__('Test Company', 1, config, use_browserless=False)
    
    async def scrape_deep_data(self, page):
        """Minimal implementation for testing"""
        self.data['base_nightly_rate'] = 100.0
        self.data['company_name'] = 'Test Company'


class TestBaseScraperInitialization(unittest.TestCase):
    """Test scraper initialization"""
    
    def test_scraper_initialization(self):
        """Test that scraper initializes correctly"""
        scraper = TestScraperImplementation()
        
        self.assertEqual(scraper.company_name, 'Test Company')
        self.assertEqual(scraper.tier, 1)
        self.assertIsNotNone(scraper.data)
        self.assertIn('company_name', scraper.data)
        self.assertIn('base_nightly_rate', scraper.data)
    
    def test_scraper_data_template(self):
        """Test that data template has all required fields"""
        scraper = TestScraperImplementation()
        
        required_fields = [
            'company_name', 'tier', 'base_nightly_rate',
            'vehicle_types', 'locations_available', 'active_promotions',
            'payment_options', 'data_completeness_pct'
        ]
        
        for field in required_fields:
            self.assertIn(field, scraper.data, f"Missing field: {field}")
    
    def test_browserless_configuration(self):
        """Test browserless configuration"""
        scraper = TestScraperImplementation()
        
        self.assertIsNotNone(scraper.browserless_key)
        self.assertIsNotNone(scraper.browserless_region)
        self.assertFalse(scraper.use_browserless)  # Set to False in init


class TestPriceExtraction(unittest.TestCase):
    """Test price extraction utilities"""
    
    def setUp(self):
        """Create scraper instance"""
        self.scraper = TestScraperImplementation()
    
    def test_extract_euro_prices(self):
        """Test extracting prices in EUR format"""
        test_text = "Price: €95.50 per night, weekend €120.00"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        prices = loop.run_until_complete(self.scraper.extract_prices_from_text(test_text))
        loop.close()
        
        self.assertGreater(len(prices), 0)
        self.assertIn(95.50, prices)
        self.assertIn(120.00, prices)
    
    def test_extract_dollar_prices(self):
        """Test extracting prices in USD format"""
        test_text = "Starting from $85 per day, premium $125"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        prices = loop.run_until_complete(self.scraper.extract_prices_from_text(test_text))
        loop.close()
        
        self.assertGreater(len(prices), 0)
        self.assertIn(85.0, prices)
        self.assertIn(125.0, prices)
    
    def test_extract_multiple_formats(self):
        """Test extracting mixed price formats"""
        test_text = "Prices: €95, $120, 85€, 100 EUR"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        prices = loop.run_until_complete(self.scraper.extract_prices_from_text(test_text))
        loop.close()
        
        # Should find at least 3 different prices
        self.assertGreaterEqual(len(prices), 3)
    
    def test_no_prices_found(self):
        """Test handling text with no prices"""
        test_text = "No pricing information available"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        prices = loop.run_until_complete(self.scraper.extract_prices_from_text(test_text))
        loop.close()
        
        self.assertEqual(len(prices), 0)


class TestPromotionDetection(unittest.TestCase):
    """Test promotion detection"""
    
    def setUp(self):
        """Create scraper instance"""
        self.scraper = TestScraperImplementation()
    
    @patch('scrapers.base_scraper.Page')
    def test_detect_promotions_with_keywords(self, mock_page):
        """Test detecting promotions with various keywords"""
        # Mock page methods
        mock_element = MagicMock()
        mock_element.inner_text = AsyncMock(return_value="Save 20% on weekend bookings!")
        
        mock_page.query_selector_all = AsyncMock(return_value=[mock_element])
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        promos = loop.run_until_complete(self.scraper.detect_promotions(mock_page))
        loop.close()
        
        self.assertGreater(len(promos), 0)
        self.assertEqual(promos[0]['text'], "Save 20% on weekend bookings!")
    
    @patch('scrapers.base_scraper.Page')
    def test_no_promotions_found(self, mock_page):
        """Test when no promotions are found"""
        mock_page.query_selector_all = AsyncMock(return_value=[])
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        promos = loop.run_until_complete(self.scraper.detect_promotions(mock_page))
        loop.close()
        
        self.assertEqual(len(promos), 0)


class TestPaymentDetection(unittest.TestCase):
    """Test payment method detection"""
    
    def setUp(self):
        """Create scraper instance"""
        self.scraper = TestScraperImplementation()
    
    @patch('scrapers.base_scraper.Page')
    def test_detect_credit_card(self, mock_page):
        """Test detecting credit card payments"""
        mock_page.evaluate = AsyncMock(return_value="We accept Visa, Mastercard, and American Express")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        methods = loop.run_until_complete(self.scraper.detect_payment_options(mock_page))
        loop.close()
        
        self.assertIn('credit_card', methods)
    
    @patch('scrapers.base_scraper.Page')
    def test_detect_paypal(self, mock_page):
        """Test detecting PayPal"""
        mock_page.evaluate = AsyncMock(return_value="Pay with PayPal for instant checkout")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        methods = loop.run_until_complete(self.scraper.detect_payment_options(mock_page))
        loop.close()
        
        self.assertIn('paypal', methods)
    
    @patch('scrapers.base_scraper.Page')
    def test_detect_multiple_methods(self, mock_page):
        """Test detecting multiple payment methods"""
        mock_page.evaluate = AsyncMock(
            return_value="We accept credit cards, PayPal, Apple Pay, and bank transfer"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        methods = loop.run_until_complete(self.scraper.detect_payment_options(mock_page))
        loop.close()
        
        self.assertGreaterEqual(len(methods), 3)


class TestReviewExtraction(unittest.TestCase):
    """Test customer review extraction"""
    
    def setUp(self):
        """Create scraper instance"""
        self.scraper = TestScraperImplementation()
    
    @patch('scrapers.base_scraper.Page')
    def test_extract_reviews_with_rating(self, mock_page):
        """Test extracting review ratings"""
        mock_element = MagicMock()
        mock_element.inner_text = AsyncMock(return_value="4.5")
        
        mock_page.query_selector = AsyncMock(return_value=mock_element)
        mock_page.evaluate = AsyncMock(return_value="Based on 1250 reviews")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        reviews = loop.run_until_complete(self.scraper.extract_customer_reviews(mock_page))
        loop.close()
        
        self.assertEqual(reviews['avg'], 4.5)
        self.assertEqual(reviews['count'], 1250)
    
    @patch('scrapers.base_scraper.Page')
    def test_no_reviews_found(self, mock_page):
        """Test when no reviews are found"""
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.evaluate = AsyncMock(return_value="No reviews yet")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        reviews = loop.run_until_complete(self.scraper.extract_customer_reviews(mock_page))
        loop.close()
        
        self.assertIsNone(reviews['avg'])
        self.assertIsNone(reviews['count'])


class TestCompletenessCalculation(unittest.TestCase):
    """Test data completeness calculation"""
    
    def setUp(self):
        """Create scraper instance"""
        self.scraper = TestScraperImplementation()
    
    def test_calculate_completeness_empty_data(self):
        """Test completeness with minimal data"""
        # Reset data to minimal
        for key in self.scraper.data:
            if key not in ['company_name', 'tier']:
                self.scraper.data[key] = None
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        completeness = loop.run_until_complete(self.scraper.calculate_completeness())
        loop.close()
        
        self.assertLess(completeness, 20)  # Should be low
    
    def test_calculate_completeness_full_data(self):
        """Test completeness with full data"""
        # Fill all fields with dummy data
        for key in self.scraper.data:
            if self.scraper.data[key] is None or self.scraper.data[key] == []:
                if isinstance(self.scraper.data[key], list):
                    self.scraper.data[key] = ['test']
                elif isinstance(self.scraper.data[key], (int, float)):
                    self.scraper.data[key] = 100
                else:
                    self.scraper.data[key] = 'test'
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        completeness = loop.run_until_complete(self.scraper.calculate_completeness())
        loop.close()
        
        self.assertGreater(completeness, 80)  # Should be high


class TestCompetitorConfig(unittest.TestCase):
    """Test competitor configuration loading"""
    
    def test_load_roadsurfer_config(self):
        """Test loading Roadsurfer configuration"""
        config = get_competitor_by_name("Roadsurfer")
        
        self.assertIsNotNone(config)
        self.assertEqual(config['name'], 'Roadsurfer')
        self.assertEqual(config['tier'], 1)
        self.assertIn('homepage', config['urls'])
    
    def test_load_mcrent_config(self):
        """Test loading McRent configuration"""
        config = get_competitor_by_name("McRent")
        
        self.assertIsNotNone(config)
        self.assertEqual(config['name'], 'McRent')
        self.assertIn('urls', config)
    
    def test_config_has_required_fields(self):
        """Test that config has all required fields"""
        config = get_competitor_by_name("Roadsurfer")
        
        required_fields = ['name', 'tier', 'country', 'business_model', 'urls']
        for field in required_fields:
            self.assertIn(field, config, f"Missing field: {field}")


class TestNavigationStrategies(unittest.TestCase):
    """Test navigation strategies and fallbacks"""
    
    def setUp(self):
        """Create scraper instance"""
        self.scraper = TestScraperImplementation()
    
    @patch('scrapers.base_scraper.Page')
    def test_navigate_smart_success(self, mock_page):
        """Test successful navigation"""
        mock_page.goto = AsyncMock(return_value=None)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            self.scraper.navigate_smart(mock_page, 'https://example.com')
        )
        loop.close()
        
        self.assertTrue(success)
        mock_page.goto.assert_called_once()
    
    @patch('scrapers.base_scraper.Page')
    def test_navigate_smart_with_fallback(self, mock_page):
        """Test navigation with fallback strategy"""
        # First call fails, second succeeds
        mock_page.goto = AsyncMock(
            side_effect=[Exception("Timeout"), None]
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            self.scraper.navigate_smart(mock_page, 'https://example.com')
        )
        loop.close()
        
        self.assertTrue(success)
        self.assertEqual(mock_page.goto.call_count, 2)
    
    @patch('scrapers.base_scraper.Page')
    def test_navigate_smart_all_fail(self, mock_page):
        """Test when all navigation strategies fail"""
        mock_page.goto = AsyncMock(side_effect=Exception("Failed"))
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            self.scraper.navigate_smart(mock_page, 'https://example.com')
        )
        loop.close()
        
        self.assertFalse(success)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in scrapers"""
    
    def setUp(self):
        """Create scraper instance"""
        self.scraper = TestScraperImplementation()
    
    def test_handle_missing_data_gracefully(self):
        """Test that scraper handles missing data gracefully"""
        # This should not raise an exception
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        completeness = loop.run_until_complete(self.scraper.calculate_completeness())
        loop.close()
        
        self.assertIsInstance(completeness, float)
        self.assertGreaterEqual(completeness, 0)
        self.assertLessEqual(completeness, 100)


def run_all_tests():
    """Run all scraper tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBaseScraperInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestPriceExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestPromotionDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestPaymentDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestReviewExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestCompletenessCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestCompetitorConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigationStrategies))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("🔍 SCRAPER TESTS SUMMARY")
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


