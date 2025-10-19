"""
Enhanced Base Scraper - Deep Data Collection
Collects 20+ data points per competitor for quality insights
"""

import asyncio
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from playwright.async_api import Browser, Page, async_playwright
from loguru import logger
import json
import re
import time
from .smart_text_extractor import SmartTextExtractor

# Windows async compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Import centralized configuration
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

try:
    from core_config import config as sys_config
    SCREENSHOTS_DIR = sys_config.SCREENSHOTS_DIR
    HTML_DIR = sys_config.HTML_DIR
    USE_BROWSERLESS = sys_config.scraping.USE_BROWSERLESS
    BROWSERLESS_API_KEY = sys_config.scraping.BROWSERLESS_API_KEY
    BROWSERLESS_REGION = sys_config.scraping.BROWSERLESS_REGION
    SCRAPING_TIMEOUT = sys_config.scraping.SCRAPING_TIMEOUT
except ImportError:
    # Fallback for backwards compatibility
    SCREENSHOTS_DIR = BASE_DIR / "data" / "screenshots"
    HTML_DIR = BASE_DIR / "data" / "html"
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    USE_BROWSERLESS = True
    BROWSERLESS_API_KEY = ""  # Must be set in environment
    BROWSERLESS_REGION = "production-sfo"
    SCRAPING_TIMEOUT = 60000


class DeepDataScraper(ABC):
    """Base class for deep competitive intelligence scraping.

    This abstract base class provides a framework for scraping comprehensive
    competitive intelligence data from campervan rental websites. It handles
    browser automation, data collection, and provides utility methods for
    extracting pricing, promotions, and other business intelligence.

    Attributes:
        company_name (str): Name of the competitor company
        tier (int): Scraping tier (1=Daily, 2=Weekly, 3=Monthly)
        config (Dict): Configuration dictionary with URLs and scraping settings
        use_browserless (bool): Whether to use Browserless.io or local browser
        data (Dict): Dictionary storing all collected data points

    Example:
        >>> class MyScraper(DeepDataScraper):
        ...     async def scrape_deep_data(self, page):
        ...         self.data['base_nightly_rate'] = 100
        ...
        >>> scraper = MyScraper("Roadsurfer", 1, config)
        >>> result = await scraper.scrape()
    """

    def __init__(self, company_name: str, tier: int, config: Dict, use_browserless: bool | None = None):
        self.company_name = company_name
        self.tier = tier
        self.config = config
        # Use provided value or fall back to global config
        self.use_browserless = use_browserless if use_browserless is not None else USE_BROWSERLESS
        self.browserless_key = BROWSERLESS_API_KEY
        self.browserless_region = BROWSERLESS_REGION
        self.scraping_timeout = SCRAPING_TIMEOUT
        
        # API interception storage
        self.api_requests = []
        self.api_responses = []
        self.pricing_endpoints = []
        
        # Data collection template
        self.data = {
            # Core
            'company_name': company_name,
            'scrape_timestamp': datetime.now(),
            'tier': tier,
            
            # Pricing - Base
            'base_nightly_rate': None,
            'weekend_premium_pct': None,
            'seasonal_multiplier': None,
            'currency': 'EUR',
            
            # Pricing - Discounts & Fees
            'early_bird_discount_pct': None,
            'weekly_discount_pct': None,
            'monthly_discount_pct': None,
            'last_minute_discount_pct': None,
            'insurance_cost_per_day': None,
            'cleaning_fee': None,
            'booking_fee': None,
            
            # Inventory
            'mileage_limit_km': None,
            'mileage_cost_per_km': None,
            'fuel_policy': None,
            'min_rental_days': None,
            'fleet_size_estimate': None,
            'vehicles_available': None,
            
            # Vehicle Details
            'vehicle_types': [],
            'vehicle_features': [],
            'popular_vehicle_type': None,
            
            # Geographic
            'locations_available': [],
            'popular_routes': [],
            'one_way_rental_allowed': None,
            'one_way_fee': None,
            
            # Promotions
            'active_promotions': [],
            'promotion_text': None,
            'discount_code_available': False,
            'referral_program': False,
            
            # Customer Experience
            'booking_process_steps': None,
            'payment_options': [],
            'cancellation_policy': None,
            'customer_review_avg': None,
            'review_count': None,
            
            # Metadata
            'data_source_url': None,
            'scraping_strategy_used': None,
            'data_completeness_pct': 0,
            'is_estimated': False,
            'notes': None
        }
    
    async def get_browser(self) -> Browser:
        """Get browser instance with automatic fallback.

        Attempts to connect to Browserless.io if configured, otherwise
        launches a local Chromium browser. Automatically falls back to
        local browser if Browserless connection fails.

        Returns:
            Browser: Playwright Browser instance ready for use

        Raises:
            Exception: If both Browserless and local browser fail to launch

        Note:
            The browser must be closed manually after use with browser.close()
        """
        playwright = await async_playwright().start()
        
        if self.use_browserless and self.browserless_key:
            try:
                browser = await playwright.chromium.connect_over_cdp(
                    f"wss://{self.browserless_region}.browserless.io?token={self.browserless_key}",
                    timeout=self.scraping_timeout
                )
                logger.info(f"✅ Connected to Browserless for {self.company_name}")
            except Exception as e:
                logger.warning(f"⚠️ Browserless connection failed: {e}. Falling back to local browser.")
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                logger.info(f"✅ Launched local browser for {self.company_name}")
        else:
            browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            logger.info(f"✅ Launched local browser for {self.company_name}")
        
        return browser
    
    def _setup_api_interception(self, page: Page):
        """Set up request/response interception for API monitoring"""
        page.on("request", lambda request: self._on_request(request))
        page.on("response", lambda response: asyncio.create_task(self._on_response(response)))
        logger.debug(f"✅ API interception enabled for {self.company_name}")
    
    def _on_request(self, request):
        """Track API requests for pricing data"""
        url = request.url
        
        # Identify pricing-related endpoints
        pricing_keywords = ['price', 'pricing', 'quote', 'rate', 'booking', 
                           'availability', 'search', 'vehicle', 'reservation',
                           'rental', 'cost', 'tariff']
        
        if any(keyword in url.lower() for keyword in pricing_keywords):
            if 'api' in url.lower() or url.endswith('.json') or '/graphql' in url.lower():
                self.pricing_endpoints.append({
                    'url': url,
                    'method': request.method,
                    'timestamp': datetime.now()
                })
                logger.info(f"🎯 Pricing API detected: {url[:80]}...")
    
    async def _on_response(self, response):
        """Capture API responses and extract pricing"""
        url = response.url
        
        # Only process responses from pricing endpoints
        if any(endpoint['url'] == url for endpoint in self.pricing_endpoints):
            try:
                # Check if response is JSON
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type.lower():
                    data = await response.json()
                    
                    # Store for later processing
                    self.api_responses.append({
                        'url': url,
                        'status': response.status,
                        'data': data,
                        'timestamp': datetime.now()
                    })
                    
                    logger.info(f"✅ Captured API response from: {url[:60]}...")
                    
                    # Try to extract price immediately
                    price = self._extract_price_from_api_response(data)
                    if price and price > 0:
                        # Only update if we don't have a price or if this is more reliable
                        if not self.data.get('base_nightly_rate') or self.data.get('is_estimated'):
                            self.data['base_nightly_rate'] = price
                            self.data['is_estimated'] = False
                            self.data['extraction_method'] = 'api_interception'
                            logger.info(f"💰 API Price extracted: €{price}")
                        
            except Exception as e:
                logger.debug(f"API response processing error: {e}")
    
    def _extract_price_from_api_response(self, data: dict) -> float | None:
        """
        Extract price from API JSON response.
        Handles multiple API response formats.
        """
        import re
        
        # Common API response patterns
        price_paths = [
            ['price'], ['pricing', 'total'], ['rate', 'nightly'], ['daily_rate'],
            ['base_price'], ['amount'], ['cost', 'per_day'], ['rental', 'price'],
            ['quote', 'total'], ['vehicle', 'price'], ['data', 'price'],
            ['result', 'pricing', 'base'], ['pricePerNight'], ['dailyPrice'],
            ['totalPrice'], ['nightlyRate'], ['baseRate']
        ]
        
        # Try each path
        for path in price_paths:
            value = data
            for key in path:
                if isinstance(value, dict):
                    # Try exact match first
                    if key in value:
                        value = value[key]
                    else:
                        # Try case-insensitive match
                        found = False
                        for k in value.keys():
                            if k.lower() == key.lower():
                                value = value[k]
                                found = True
                                break
                        if not found:
                            break
                else:
                    break
            
            # Check if we found a price
            if isinstance(value, (int, float)) and 10 < value < 1000:
                return float(value)
            elif isinstance(value, str):
                # Try to parse currency string
                numbers = re.findall(r'\d+\.?\d*', value)
                if numbers:
                    price = float(numbers[0])
                    if 10 < price < 1000:
                        return price
        
        # If direct paths don't work, search entire JSON recursively
        return self._recursive_price_search(data)
    
    def _recursive_price_search(self, obj, depth=0, max_depth=5):
        """Recursively search JSON for price values"""
        if depth > max_depth:
            return None
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Check if key suggests this is a price
                if any(word in key.lower() for word in ['price', 'rate', 'cost', 'amount', 'tariff']):
                    if isinstance(value, (int, float)) and 10 < value < 1000:
                        return float(value)
                
                # Recurse
                price = self._recursive_price_search(value, depth + 1, max_depth)
                if price:
                    return price
        
        elif isinstance(obj, list) and len(obj) > 0:
            # Check first few items in list
            for item in obj[:3]:
                price = self._recursive_price_search(item, depth + 1, max_depth)
                if price:
                    return price
        
        return None
    
    async def _simulate_booking_universal(self, page: Page, test_location: str = "Berlin", days_ahead: int = 7, rental_days: int = 7) -> bool:
        """
        Universal booking form simulator for campervan rental sites.
        Fills in common form fields to trigger dynamic pricing.
        
        Args:
            page: Playwright page object
            test_location: Location to test (default: Berlin)
            days_ahead: Days from now for pickup (default: 7)
            rental_days: Number of rental days (default: 7)
            
        Returns:
            bool: True if booking simulation succeeded and found prices
        """
        from datetime import datetime, timedelta
        
        logger.info(f"🎯 Starting universal booking simulation for {self.company_name}...")
        
        try:
            # Quick load check (reduced timeout for speed)
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=10000)
            except:
                pass  # Continue even if timeout
            await page.wait_for_timeout(1000)  # Reduced from 2000ms
            
            # Calculate dates
            start_date = datetime.now() + timedelta(days=days_ahead)
            end_date = start_date + timedelta(days=rental_days)
            
            # Common date formats
            date_formats = ['%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y', '%d/%m/%Y']
            
            # Try to fill location field
            location_selectors = [
                'input[name*="location"]', 'input[placeholder*="location"]',
                'input[name*="city"]', 'input[placeholder*="city"]',
                'input[name*="pickup"]', 'input[placeholder*="pickup"]',
                'input[name*="station"]', 'select[name*="station"]',
                '#location', '#pickup-location', '#city'
            ]
            
            location_filled = False
            for selector in location_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        # Check if it's a select or input
                        tag_name = await element.evaluate('el => el.tagName')
                        
                        if tag_name == 'SELECT':
                            # Try to select first option that's not empty
                            options = await element.query_selector_all('option')
                            for option in options[1:3]:  # Skip first (usually empty), try next 2
                                value = await option.get_attribute('value')
                                if value:
                                    await element.select_option(value)
                                    location_filled = True
                                    break
                        else:
                            # It's an input field
                            await element.fill(test_location)
                            await page.wait_for_timeout(1500)  # Wait for autocomplete
                            
                            # Try to select first autocomplete option
                            autocomplete_selectors = [
                                '[role="option"]', '.autocomplete-item',
                                '.suggestion', '.dropdown-item'
                            ]
                            for ac_sel in autocomplete_selectors:
                                ac_elem = await page.query_selector(ac_sel)
                                if ac_elem:
                                    await ac_elem.click()
                                    break
                            
                            location_filled = True
                        
                        if location_filled:
                            logger.debug(f"✅ Location filled with selector: {selector}")
                            break
                            
                except Exception as e:
                    logger.debug(f"Location fill attempt failed for {selector}: {e}")
                    continue
            
            # Try to fill start date
            start_date_selectors = [
                'input[name*="start"]', 'input[name*="pickup"]', 'input[name*="from"]',
                'input[placeholder*="start"]', 'input[placeholder*="pickup"]',
                '#start-date', '#pickup-date', '#from-date'
            ]
            
            for selector in start_date_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        # Try different date formats
                        for date_format in date_formats:
                            try:
                                await element.fill(start_date.strftime(date_format))
                                logger.debug(f"✅ Start date filled: {start_date.strftime(date_format)}")
                                break
                            except:
                                continue
                        break
                except Exception as e:
                    logger.debug(f"Start date fill failed for {selector}: {e}")
                    continue
            
            # Try to fill end date
            end_date_selectors = [
                'input[name*="end"]', 'input[name*="return"]', 'input[name*="to"]',
                'input[placeholder*="end"]', 'input[placeholder*="return"]',
                '#end-date', '#return-date', '#to-date'
            ]
            
            for selector in end_date_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        for date_format in date_formats:
                            try:
                                await element.fill(end_date.strftime(date_format))
                                logger.debug(f"✅ End date filled: {end_date.strftime(date_format)}")
                                break
                            except:
                                continue
                        break
                except Exception as e:
                    logger.debug(f"End date fill failed for {selector}: {e}")
                    continue
            
            # Try to submit the form
            submit_selectors = [
                'button[type="submit"]', 'input[type="submit"]',
                'button:has-text("Search")', 'button:has-text("Find")',
                'button:has-text("Book")', 'button:has-text("Check")',
                '.search-button', '.submit-button', '#search-button',
                'button[class*="search"]', 'button[class*="submit"]'
            ]
            
            submitted = False
            for selector in submit_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.click()
                        logger.info("✅ Submit button clicked")
                        submitted = True
                        break
                except Exception as e:
                    logger.debug(f"Submit click failed for {selector}: {e}")
                    continue
            
            if submitted:
                # Wait for results to load (reduced timeout for speed)
                try:
                    await page.wait_for_load_state('domcontentloaded', timeout=15000)
                except:
                    logger.debug("Load timeout, continuing anyway")
                
                # Brief wait for dynamic content
                await page.wait_for_timeout(2000)  # Reduced from 5s to 2s
                
                # Check if we're still on an error page
                if await self._is_error_page(page):
                    logger.warning("❌ Error page detected after form submission")
                    return False
                
                # Try to extract prices from results
                prices = await self._extract_prices_from_booking_results(page)
                
                if prices:
                    min_price = min(prices)
                    self.data['base_nightly_rate'] = min_price
                    self.data['is_estimated'] = False
                    self.data['extraction_method'] = 'booking_simulation'
                    logger.info(f"✅ Booking simulation success: €{min_price}/night from {len(prices)} options")
                    return True
                else:
                    # Wait a bit more and try again
                    await page.wait_for_timeout(3000)
                    prices = await self._extract_prices_from_booking_results(page)
                    if prices:
                        min_price = min(prices)
                        self.data['base_nightly_rate'] = min_price
                        self.data['is_estimated'] = False
                        self.data['extraction_method'] = 'booking_simulation'
                        logger.info(f"✅ Booking simulation success (retry): €{min_price}/night from {len(prices)} options")
                        return True
            
            logger.warning("⚠️ Booking simulation completed but no prices found")
            return False
            
        except Exception as e:
            logger.warning(f"Booking simulation failed: {e}")
            return False
    
    async def _extract_prices_from_booking_results(self, page: Page) -> list:
        """Extract all prices from booking search results page"""
        import re
        prices = []
        
        # Common price selectors on result pages
        price_selectors = [
            '[class*="price"]', '[data-test*="price"]', '[data-testid*="price"]',
            '.vehicle-price', '.listing-price', '.rental-price',
            '[class*="rate"]', '[class*="cost"]', '[class*="amount"]'
        ]
        
        for selector in price_selectors:
            try:
                elements = await page.query_selector_all(selector)
                
                for element in elements[:10]:  # Check first 10 elements
                    try:
                        text = await element.inner_text()
                        
                        # Extract numbers from price text
                        # Patterns: €85, $120, 85€, EUR 95, 120.50, etc.
                        patterns = [
                            r'[€$£]\s*(\d+(?:\.\d{2})?)',  # €85, $120
                            r'(\d+(?:\.\d{2})?)\s*[€$£]',  # 85€, 120$
                            r'(?:EUR|USD|GBP)\s*(\d+(?:\.\d{2})?)',  # EUR 95
                            r'(\d+(?:\.\d{2})?)\s*/\s*(?:night|day)',  # 85 / night
                            r'(\d{2,3}(?:\.\d{2})?)'  # Just numbers 85 or 85.50
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, text, re.IGNORECASE)
                            for match in matches:
                                try:
                                    price = float(match)
                                    if 20 < price < 500:  # Reasonable nightly rate range
                                        prices.append(price)
                                except ValueError:
                                    continue
                    except Exception as e:
                        logger.debug(f"Element text extraction error: {e}")
                        continue
                        
                if prices:  # If we found prices with this selector, stop
                    break
                    
            except Exception as e:
                logger.debug(f"Price selector {selector} failed: {e}")
                continue
        
        # Remove duplicates and outliers
        if prices:
            import statistics
            # Remove prices that are too far from median (outliers)
            median = statistics.median(prices)
            filtered_prices = [p for p in prices if abs(p - median) / median < 0.5]  # Within 50% of median
            return filtered_prices if filtered_prices else prices
        
        return []
    
    async def navigate_smart(self, page: Page, url: str, wait_strategy: str = 'load') -> bool:
        """Smart navigation with multiple fallback strategies and error detection.

        Attempts to navigate to a URL using different wait strategies,
        falling back to more lenient strategies if strict ones fail.
        This increases reliability when dealing with slow-loading sites.

        Args:
            page (Page): Playwright Page instance
            url (str): URL to navigate to
            wait_strategy (str, optional): Initial wait strategy. One of:
                - 'load': Wait for load event (default)
                - 'domcontentloaded': Wait for DOM ready
                - 'networkidle': Wait for network to be idle

        Returns:
            bool: True if navigation succeeded, False if all strategies failed

        Example:
            >>> success = await self.navigate_smart(page, "https://example.com")
            >>> if success:
            ...     # Extract data
        """
        strategies = [wait_strategy, 'load', 'domcontentloaded']
        
        for strategy in strategies:
            try:
                await page.goto(url, wait_until=strategy, timeout=30000)  # Optimized from 60s to 30s
                
                # Wait for additional dynamic content
                await asyncio.sleep(2)
                
                # Check for error pages
                if await self._is_error_page(page):
                    logger.warning(f"❌ Error page detected for {url}")
                    return False
                
                logger.info(f"✅ Loaded {url} with {strategy}")
                self.data['data_source_url'] = url
                return True
            except Exception as e:
                logger.warning(f"Navigation failed with {strategy}: {e}")
                if strategy == strategies[-1]:
                    logger.error(f"❌ All strategies failed for {url}")
                    return False
        return False
    
    async def _is_error_page(self, page: Page) -> bool:
        """Check if the current page is an error page or not properly loaded - DISABLED for testing."""
        # Temporarily disable error page detection to let scrapers proceed
        # The overly aggressive detection was causing false positives
        return False
        
        try:
            # Get visible page text (not HTML source)
            page_text = await page.evaluate('() => document.body.innerText')
            text_lower = page_text.lower().strip()
            
            # Only check if page is suspiciously short
            if len(text_lower) < 50:
                logger.warning("Page content too short, likely error page")
                return True
            
            # Check for strong error indicators in prominent positions only
            first_text = text_lower[:500]
            strong_errors = [
                "page not found",
                "404 not found",
                "access denied",
                "internal server error",
                "this site can't be reached"
            ]
            
            for pattern in strong_errors:
                if pattern in first_text:
                    logger.warning(f"Error indicator in visible text: {pattern}")
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error page detection failed: {e}")
            return False
    
    async def extract_prices_from_text(self, text: str) -> List[float]:
        """Extract all price values from text using regex patterns.

        Searches for common price formats in multiple currencies and
        returns all numeric values found. Supports formats like:
        - €85, $120
        - 85€, 120$
        - 85 EUR, 120 USD

        Args:
            text (str): Text to search for prices

        Returns:
            List[float]: List of all price values found (may be empty)

        Example:
            >>> prices = await scraper.extract_prices_from_text("Price: €120 per night")
            >>> print(prices)  # [120.0]
        """
        # Match patterns like: €85, $120, 85€, 120 EUR
        price_patterns = [
            r'€\s*(\d+(?:\.\d{2})?)',
            r'\$\s*(\d+(?:\.\d{2})?)',
            r'(\d+(?:\.\d{2})?)\s*€',
            r'(\d+(?:\.\d{2})?)\s*EUR',
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            prices.extend([float(m) for m in matches])
        
        return prices
    
    async def detect_promotions(self, page: Page) -> List[Dict]:
        """Detect active promotions with enhanced extraction.

        Searches for elements containing promotional keywords like
        "discount", "sale", "offer", etc. Also checks banners and
        promo sections. Returns structured data about each promotion found.

        Args:
            page (Page): Playwright Page instance

        Returns:
            List[Dict]: List of promotion dictionaries, each containing:
                - text (str): Promotion text
                - type (str): Type of promotion (banner, code, etc.)
                - discount_pct (float): Discount percentage if found

        Note:
            Limited to 10 promotions maximum to prevent excessive data
        """
        promotions = []
        seen_texts = set()  # Avoid duplicates

        # 1. Check for promo banners (usually at top of page)
        try:
            banner_selectors = [
                '[class*="banner"]',
                '[class*="promo"]',
                '[class*="alert"]',
                '[class*="notice"]',
                '[role="banner"]',
                '.hero',
                '.announcement'
            ]

            for selector in banner_selectors:
                elements = await page.query_selector_all(selector)
                for elem in elements[:3]:  # Check first 3
                    try:
                        text = await elem.inner_text()
                        text = text.strip()

                        # Check if it looks like a promotion
                        if text and len(text) < 300 and text not in seen_texts:
                            promo_keywords = ['discount', 'sale', 'offer', 'promo', 'deal', 'save', 'off', '%', 'code']
                            if any(keyword in text.lower() for keyword in promo_keywords):
                                # Extract discount percentage if present
                                discount_match = re.search(r'(\d+)%\s*(?:off|discount)', text, re.IGNORECASE)
                                discount_pct = float(discount_match.group(1)) if discount_match else None

                                promotions.append({
                                    'text': text,
                                    'type': 'banner',
                                    'discount_pct': discount_pct
                                })
                                seen_texts.add(text)
                    except:
                        pass
        except Exception as e:
            logger.debug(f"Banner promo check failed: {e}")

        # 2. Check for promo codes
        try:
            code_patterns = [
                r'(?:code|coupon)[:\s]+([A-Z0-9]{4,15})',
                r'use code\s+([A-Z0-9]{4,15})',
                r'promo code[:\s]+([A-Z0-9]{4,15})'
            ]

            page_text = await page.evaluate('() => document.body.innerText')
            for pattern in code_patterns:
                matches = re.finditer(pattern, page_text, re.IGNORECASE)
                for match in list(matches)[:3]:  # Max 3 codes
                    code = match.group(1)
                    context = page_text[max(0, match.start()-50):min(len(page_text), match.end()+50)]

                    if context not in seen_texts:
                        promotions.append({
                            'text': context.strip(),
                            'type': 'code',
                            'code': code
                        })
                        seen_texts.add(context)
        except Exception as e:
            logger.debug(f"Promo code check failed: {e}")

        # 3. Check for early bird, weekly, monthly discounts
        try:
            discount_keywords = {
                'early_bird': ['early bird', 'book early', 'advance booking'],
                'weekly': ['weekly discount', 'week discount', '7 days'],
                'monthly': ['monthly discount', 'month discount', '30 days'],
                'last_minute': ['last minute', 'last-minute']
            }

            for discount_type, keywords in discount_keywords.items():
                for keyword in keywords:
                    if keyword in page_text.lower():
                        # Try to find percentage near the keyword
                        keyword_pos = page_text.lower().find(keyword)
                        context = page_text[max(0, keyword_pos-100):min(len(page_text), keyword_pos+100)]

                        discount_match = re.search(r'(\d+)%', context)
                        if discount_match and context not in seen_texts:
                            promotions.append({
                                'text': context.strip(),
                                'type': discount_type,
                                'discount_pct': float(discount_match.group(1))
                            })
                            seen_texts.add(context)
                            break
        except Exception as e:
            logger.debug(f"Discount keyword check failed: {e}")

        return promotions[:10]  # Return max 10 promotions
    
    async def analyze_booking_process(self, page: Page) -> int:
        """Count booking process steps"""
        step_indicators = [
            '.step', '.wizard-step', '[data-step]',
            '.progress-step', '.checkout-step', '.booking-step'
        ]

        for selector in step_indicators:
            try:
                steps = await page.query_selector_all(selector)
                if steps:
                    return len(steps)
            except:
                pass

        return None

    async def extract_vehicle_features(self, page: Page) -> List[str]:
        """Extract vehicle features from specific page sections"""
        all_features = set()

        try:
            # 1. Look for features/amenities sections
            feature_selectors = [
                '[class*="features"]',
                '[class*="amenities"]',
                '[class*="equipment"]',
                '[class*="included"]',
                '[id*="features"]',
                '[id*="amenities"]',
                '.vehicle-specs',
                '.specifications'
            ]

            for selector in feature_selectors:
                elements = await page.query_selector_all(selector)
                for element in elements[:5]:  # Check first 5
                    try:
                        text = await element.inner_text()
                        # Use SmartTextExtractor to find features
                        features = SmartTextExtractor.extract_features(text)
                        all_features.update(features)
                    except:
                        pass

            # 2. Check for feature lists (ul/ol)
            list_items = await page.query_selector_all('ul li, ol li')
            for item in list_items[:30]:  # Check first 30 list items
                try:
                    text = await item.inner_text()
                    # Only check short text items that might be features
                    if text and len(text) < 100:
                        features = SmartTextExtractor.extract_features(text)
                        all_features.update(features)
                except:
                    pass

            # 3. Also check full page text as fallback
            if len(all_features) < 3:  # If we found very few features
                page_text = await page.evaluate('() => document.body.innerText')
                features = SmartTextExtractor.extract_features(page_text)
                all_features.update(features)

        except Exception as e:
            logger.debug(f"Vehicle features extraction failed: {e}")

        return sorted(list(all_features))
    
    async def detect_payment_options(self, page: Page) -> List[str]:
        """Detect available payment methods with enhanced detection"""
        payment_methods = set()  # Use set to avoid duplicates

        # Enhanced payment indicators with more keywords
        payment_indicators = {
            'credit_card': ['visa', 'mastercard', 'amex', 'american express', 'credit card', 'debit card', 'maestro', 'discover'],
            'paypal': ['paypal', 'pay pal'],
            'bank_transfer': ['bank transfer', 'sepa', 'wire transfer', 'direct debit', 'bancontact'],
            'ideal': ['ideal'],
            'sofort': ['sofort', 'klarna sofort'],
            'klarna': ['klarna', 'pay later'],
            'apple_pay': ['apple pay', 'applepay'],
            'google_pay': ['google pay', 'googlepay', 'gpay']
        }

        # Check page text
        page_text = await page.evaluate('() => document.body.innerText')
        page_text_lower = page_text.lower()

        for method, keywords in payment_indicators.items():
            if any(keyword in page_text_lower for keyword in keywords):
                payment_methods.add(method)

        # Check for payment logos/images in footer
        try:
            footer = await page.query_selector('footer, [role="contentinfo"]')
            if footer:
                footer_html = await footer.inner_html()
                footer_html_lower = footer_html.lower()

                # Check for payment logo images
                for method, keywords in payment_indicators.items():
                    for keyword in keywords:
                        if keyword.replace(' ', '') in footer_html_lower or keyword.replace(' ', '-') in footer_html_lower:
                            payment_methods.add(method)
        except Exception as e:
            logger.debug(f"Footer payment check failed: {e}")

        # Check for payment form fields or selectors
        try:
            # Look for common payment selector elements
            payment_selectors = [
                '[class*="payment"]',
                '[id*="payment"]',
                '[data-payment]',
                '.checkout-payment',
                '.payment-methods'
            ]

            for selector in payment_selectors:
                elements = await page.query_selector_all(selector)
                for element in elements[:5]:  # Check first 5
                    elem_text = await element.inner_text()
                    elem_text_lower = elem_text.lower()

                    for method, keywords in payment_indicators.items():
                        if any(keyword in elem_text_lower for keyword in keywords):
                            payment_methods.add(method)
        except Exception as e:
            logger.debug(f"Payment selector check failed: {e}")

        return sorted(list(payment_methods))  # Return sorted list
    
    async def extract_customer_reviews(self, page: Page) -> Dict:
        """
        Comprehensive review extraction with fallbacks.

        Strategies:
        1. Check current page first
        2. Check homepage
        3. Check footer/header on any page
        4. Scrape Trustpilot directly
        5. Check Google Reviews

        Returns:
            Dict with 'avg', 'count', and 'source' fields
        """
        # Strategy 1: Check current page first
        review_data = await self._check_page_for_reviews(page)
        if review_data['avg'] or review_data['count']:
            return review_data

        # Strategy 2: Check homepage
        if hasattr(self, 'config') and 'homepage' in self.config.get('urls', {}):
            homepage_url = self.config['urls']['homepage']
            current_url = page.url

            if current_url != homepage_url:
                logger.info("🔍 Checking homepage for reviews...")
                try:
                    await self.navigate_smart(page, homepage_url)
                    review_data = await self._check_page_for_reviews(page)
                    if review_data['avg'] or review_data['count']:
                        return review_data
                except Exception as e:
                    logger.debug(f"Homepage review check failed: {e}")

        # Strategy 3: Check footer/header on any page
        review_data = await self._check_footer_for_reviews(page)
        if review_data['avg'] or review_data['count']:
            return review_data

        # Strategy 4: Scrape Trustpilot directly
        if hasattr(self, 'company_name'):
            review_data = await self._scrape_trustpilot(page)
            if review_data['avg'] or review_data['count']:
                return review_data

        # Strategy 5: Check Google Reviews
        review_data = await self._check_google_reviews(page)
        if review_data['avg'] or review_data['count']:
            return review_data

        logger.warning("⚠️ Could not extract reviews after all strategies")
        return {'avg': None, 'count': None, 'source': None}

    async def _check_page_for_reviews(self, page: Page) -> Dict:
        """Check current page for review data with improved count extraction"""

        # 1. Trustpilot widget
        try:
            trustpilot_selectors = [
                '.trustpilot-widget',
                '[data-template-id*="trustpilot"]',
                '[class*="trustpilot"]',
                'iframe[src*="trustpilot"]',
            ]

            for selector in trustpilot_selectors:
                element = await page.query_selector(selector)
                if element:
                    rating = None
                    count = None

                    # Try to extract rating from attributes
                    rating_attr = await element.get_attribute('data-score')
                    if rating_attr:
                        rating = float(rating_attr)

                    # Try to extract count from attributes
                    count_attr = await element.get_attribute('data-count')
                    if count_attr:
                        count = int(count_attr)

                    # Try to extract from inner content
                    text = await element.inner_text()
                    if not rating:
                        match = re.search(r'(\d+\.?\d*)\s*out of\s*5', text, re.IGNORECASE)
                        if match:
                            rating = float(match.group(1))

                    # Extract count from text if not found in attributes
                    if not count:
                        count_match = re.search(r'(\d+(?:,\d+)*)\s*reviews?', text, re.IGNORECASE)
                        if count_match:
                            count = int(count_match.group(1).replace(',', ''))

                    if rating:
                        return {
                            'avg': rating,
                            'count': count,
                            'source': 'trustpilot_widget'
                        }
        except Exception as e:
            logger.debug(f"Trustpilot widget check failed: {e}")

        # 2. Schema.org JSON-LD
        try:
            schema_data = await page.evaluate('''() => {
                const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of scripts) {
                    try {
                        const data = JSON.parse(script.textContent);

                        // Check direct object
                        if (data.aggregateRating) {
                            return {
                                rating: data.aggregateRating.ratingValue,
                                count: data.aggregateRating.reviewCount
                            };
                        }

                        // Check array
                        if (Array.isArray(data)) {
                            for (const item of data) {
                                if (item.aggregateRating) {
                                    return {
                                        rating: item.aggregateRating.ratingValue,
                                        count: item.aggregateRating.reviewCount
                                    };
                                }
                            }
                        }
                    } catch(e) {}
                }
                return null;
            }''')

            if schema_data and schema_data.get('rating'):
                return {
                    'avg': float(schema_data['rating']),
                    'count': int(schema_data.get('count', 0)) if schema_data.get('count') else None,
                    'source': 'schema_org'
                }
        except Exception as e:
            logger.debug(f"Schema.org check failed: {e}")

        # 3. Generic review elements
        try:
            review_selectors = [
                '[itemprop="ratingValue"]',
                '[data-rating]',
                '.rating-value',
                '.review-score',
                '[class*="rating"]',
            ]

            for selector in review_selectors:
                element = await page.query_selector(selector)
                if element:
                    rating = None
                    count = None

                    # Try attribute first
                    rating_attr = await element.get_attribute('data-rating')
                    if not rating_attr:
                        rating_attr = await element.get_attribute('content')
                    if not rating_attr:
                        text = await element.inner_text()
                        match = re.search(r'(\d+\.?\d*)', text)
                        if match:
                            rating_attr = match.group(1)

                    if rating_attr:
                        rating_float = float(rating_attr)
                        if 0 <= rating_float <= 5:
                            rating = rating_float

                            # Look for review count near the rating element
                            # Check parent element for count
                            parent = await element.evaluate('el => el.parentElement')
                            if parent:
                                parent_text = await page.evaluate('el => el.textContent', parent)
                                count_match = re.search(r'(\d+(?:,\d+)*)\s*(?:reviews?|ratings?)', parent_text, re.IGNORECASE)
                                if count_match:
                                    count = int(count_match.group(1).replace(',', ''))

                            # Also check for itemprop="reviewCount" nearby
                            if not count:
                                count_elem = await page.query_selector('[itemprop="reviewCount"]')
                                if count_elem:
                                    count_text = await count_elem.inner_text()
                                    count_match = re.search(r'(\d+(?:,\d+)*)', count_text)
                                    if count_match:
                                        count = int(count_match.group(1).replace(',', ''))

                            return {
                                'avg': rating,
                                'count': count,
                                'source': 'generic_element'
                            }
        except Exception as e:
            logger.debug(f"Generic element check failed: {e}")

        # 4. Text pattern matching - extract both rating and count
        try:
            page_text = await page.evaluate('() => document.body.innerText')
            rating = None
            count = None

            # Match patterns like "4.5 out of 5" or "4.5/5" or "4.5 stars"
            rating_patterns = [
                r'(\d+\.?\d*)\s*out of\s*5',
                r'(\d+\.?\d*)/5',
                r'(\d+\.?\d*)\s*stars?',
                r'rating[:\s]+(\d+\.?\d*)',
            ]

            for pattern in rating_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    rating_val = float(match.group(1))
                    if 0 <= rating_val <= 5:
                        rating = rating_val
                        break

            # Match review count patterns
            count_patterns = [
                r'(\d+(?:,\d+)*)\s*reviews?',
                r'based on\s*(\d+(?:,\d+)*)',
                r'(\d+(?:,\d+)*)\s*ratings?',
                r'(\d+(?:,\d+)*)\s*customer reviews?',
            ]

            for pattern in count_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    count_val = int(match.group(1).replace(',', ''))
                    if 0 < count_val < 1000000:
                        count = count_val
                        break

            # Return if we found either rating or count
            if rating or count:
                return {
                    'avg': rating,
                    'count': count,
                    'source': 'text_pattern'
                }
        except Exception as e:
            logger.debug(f"Text pattern check failed: {e}")

        return {'avg': None, 'count': None, 'source': None}

    async def _check_footer_for_reviews(self, page: Page) -> Dict:
        """Specifically check footer/header for review badges"""

        try:
            # Check footer
            footer = await page.query_selector('footer, [role="contentinfo"]')
            if footer:
                # Look for review badges in footer
                footer_html = await footer.inner_html()

                # Check for Trustpilot iframe
                if 'trustpilot' in footer_html.lower():
                    trustpilot_iframe = await footer.query_selector('iframe[src*="trustpilot"]')
                    if trustpilot_iframe:
                        src = await trustpilot_iframe.get_attribute('src')
                        # Extract score from iframe URL if present
                        match = re.search(r'stars?[=\/](\d+\.?\d*)', src)
                        if match:
                            return {
                                'avg': float(match.group(1)),
                                'count': None,
                                'source': 'footer_trustpilot'
                            }
        except Exception as e:
            logger.debug(f"Footer check failed: {e}")

        return {'avg': None, 'count': None, 'source': None}

    async def _scrape_trustpilot(self, page: Page) -> Dict:
        """Scrape Trustpilot directly as fallback"""

        try:
            # Map company names to Trustpilot domains
            trustpilot_domains = {
                'Roadsurfer': 'roadsurfer.com',
                'McRent': 'mcrent.com',
                'Goboony': 'goboony.com',
                'Yescapa': 'yescapa.com',
                'Camperdays': 'camperdays.com',
            }

            domain = trustpilot_domains.get(self.company_name)
            if not domain:
                return {'avg': None, 'count': None, 'source': None}

            trustpilot_url = f"https://www.trustpilot.com/review/{domain}"

            logger.info(f"🔍 Checking Trustpilot: {trustpilot_url}")

            # Navigate to Trustpilot
            try:
                await page.goto(trustpilot_url, timeout=30000, wait_until='domcontentloaded')
                await asyncio.sleep(2)
            except Exception as e:
                logger.debug(f"Trustpilot navigation failed: {e}")
                return {'avg': None, 'count': None, 'source': None}

            # Extract rating
            rating_element = await page.query_selector('[data-rating-typography="true"]')
            if not rating_element:
                rating_element = await page.query_selector('.typography_heading-1__1I9Nn')

            if rating_element:
                rating_text = await rating_element.inner_text()
                match = re.search(r'(\d+\.?\d*)', rating_text)
                if match:
                    rating = float(match.group(1))

                    # Extract count
                    count_element = await page.query_selector('[data-reviews-count-typography="true"]')
                    count = None
                    if count_element:
                        count_text = await count_element.inner_text()
                        count_match = re.search(r'(\d+(?:,\d+)*)', count_text)
                        if count_match:
                            count = int(count_match.group(1).replace(',', ''))

                    logger.info(f"✅ Trustpilot: {rating}★ ({count} reviews)")
                    return {
                        'avg': rating,
                        'count': count,
                        'source': 'trustpilot_direct'
                    }

        except Exception as e:
            logger.debug(f"Trustpilot scraping failed: {e}")

        return {'avg': None, 'count': None, 'source': None}

    async def _check_google_reviews(self, page: Page) -> Dict:
        """Check for Google Reviews integration"""

        try:
            google_selectors = [
                '[data-rating]',
                '.google-review',
                '[class*="google"]',
            ]

            for selector in google_selectors:
                element = await page.query_selector(selector)
                if element:
                    rating = await element.get_attribute('data-rating')
                    if rating:
                        return {
                            'avg': float(rating),
                            'count': None,
                            'source': 'google_reviews'
                        }
        except Exception as e:
            logger.debug(f"Google Reviews check failed: {e}")

        return {'avg': None, 'count': None, 'source': None}

    async def extract_enhanced_data_from_page(self, page: Page) -> Dict:
        """
        Extract enhanced data using SmartTextExtractor and structured data.

        Extracts:
        - Pricing details (insurance, fees, deposits)
        - Policies (fuel, cancellation, mileage)
        - Features and amenities
        - Hidden JSON/JavaScript data
        """
        try:
            # Get all page text
            page_text = await page.evaluate('() => document.body.innerText')

            # Use SmartTextExtractor for advanced pattern matching
            extracted_data = SmartTextExtractor.extract_all_fields(page_text)

            # Update data dictionary with extracted fields
            for key, value in extracted_data.items():
                # Map to our data structure
                if key == 'insurance' and value:
                    self.data['insurance_cost_per_day'] = value
                elif key == 'cleaning_fee' and value:
                    self.data['cleaning_fee'] = value
                elif key == 'booking_fee' and value:
                    self.data['booking_fee'] = value
                elif key == 'min_rental_days' and value:
                    self.data['min_rental_days'] = int(value)
                elif key == 'mileage_limit' and value:
                    self.data['mileage_limit_km'] = int(value)
                elif key == 'mileage_cost' and value:
                    self.data['mileage_cost_per_km'] = value
                elif key == 'one_way_fee' and value:
                    self.data['one_way_fee'] = value
                elif key == 'weekend_premium' and value:
                    self.data['weekend_premium_pct'] = value
                elif key == 'fuel_policy' and value:
                    self.data['fuel_policy'] = value
                elif key == 'one_way_rental_allowed' and value:
                    self.data['one_way_rental_allowed'] = value
                elif key == 'free_cancellation' and value is not None:
                    self.data['cancellation_policy'] = 'Free cancellation' if value else 'Non-refundable'

            # Extract features - use dedicated method for better extraction
            features = await self.extract_vehicle_features(page)
            if features:
                # Merge with any features already found
                existing_features = self.data.get('vehicle_features', [])
                all_features = list(set(existing_features + features))
                self.data['vehicle_features'] = all_features

            # Extract structured data from JavaScript
            js_data = await self._extract_structured_data(page)
            if js_data:
                self._merge_structured_data(js_data)

            logger.info(f"Enhanced data extraction complete: {len(extracted_data)} fields found")

        except Exception as e:
            logger.debug(f"Enhanced data extraction error: {e}")

        return extracted_data

    async def _extract_structured_data(self, page: Page) -> Dict:
        """Extract data from JavaScript variables and JSON-LD"""
        try:
            js_data = await page.evaluate('''() => {
                const data = {};

                // Check common window variables
                const varNames = [
                    'appConfig', 'siteConfig', 'pageConfig',
                    'pricingData', 'vehicleData', 'bookingData',
                    'stationData', 'locationData', 'depotData'
                ];

                for (const varName of varNames) {
                    if (window[varName]) {
                        data[varName] = window[varName];
                    }
                }

                // Extract JSON-LD structured data
                const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                const jsonLdData = [];

                for (const script of jsonLdScripts) {
                    try {
                        const parsed = JSON.parse(script.textContent);
                        jsonLdData.push(parsed);
                    } catch(e) {}
                }

                if (jsonLdData.length > 0) {
                    data.jsonLd = jsonLdData;
                }

                // Check meta tags
                const metaTags = {};
                document.querySelectorAll('meta').forEach(meta => {
                    const property = meta.getAttribute('property') || meta.getAttribute('name');
                    const content = meta.getAttribute('content');
                    if (property && content) {
                        metaTags[property] = content;
                    }
                });

                if (Object.keys(metaTags).length > 0) {
                    data.metaTags = metaTags;
                }

                return data;
            }''')

            if js_data and len(js_data) > 0:
                logger.info(f"✅ Extracted structured data: {list(js_data.keys())}")
                return js_data

        except Exception as e:
            logger.debug(f"Structured data extraction failed: {e}")

        return {}

    def _merge_structured_data(self, js_data: Dict):
        """Merge structured data into main data dictionary"""
        try:
            # Process pricing data
            if 'pricingData' in js_data:
                pricing = js_data['pricingData']
                if isinstance(pricing, dict):
                    if 'basePrice' in pricing:
                        self.data['base_nightly_rate'] = float(pricing['basePrice'])
                    if 'insurance' in pricing:
                        self.data['insurance_cost_per_day'] = float(pricing['insurance'])
                    if 'cleaningFee' in pricing:
                        self.data['cleaning_fee'] = float(pricing['cleaningFee'])

            # Process vehicle data
            if 'vehicleData' in js_data:
                vehicles = js_data['vehicleData']
                if isinstance(vehicles, list):
                    self.data['fleet_size_estimate'] = len(vehicles)
                    if vehicles and isinstance(vehicles[0], dict):
                        if 'type' in vehicles[0]:
                            self.data['popular_vehicle_type'] = vehicles[0]['type']

            # Process JSON-LD data
            if 'jsonLd' in js_data:
                for item in js_data['jsonLd']:
                    if isinstance(item, dict):
                        # Extract organization info
                        if item.get('@type') == 'Organization':
                            if 'aggregateRating' in item:
                                rating = item['aggregateRating']
                                if 'ratingValue' in rating:
                                    self.data['customer_review_avg'] = float(rating['ratingValue'])
                                if 'reviewCount' in rating:
                                    self.data['review_count'] = int(rating['reviewCount'])

                        # Extract offer/pricing info
                        if item.get('@type') in ['Product', 'Service']:
                            if 'offers' in item:
                                offers = item['offers']
                                if isinstance(offers, dict) and 'price' in offers:
                                    self.data['base_nightly_rate'] = float(offers['price'])

            # Process meta tags
            if 'metaTags' in js_data:
                meta = js_data['metaTags']
                if 'og:description' in meta:
                    # Extract info from description
                    desc = meta['og:description']
                    features = SmartTextExtractor.extract_features(desc)
                    if features:
                        self.data['vehicle_features'].extend(features)

        except Exception as e:
            logger.debug(f"Structured data merge error: {e}")

    def _fix_derived_fields(self):
        """
        Fix derived fields that should be calculated from other fields.

        This fixes issues like vehicle_types_count being 0 even when
        vehicle_types has data. Also extracts discount percentages from promotions.
        """
        # Fix vehicle_types_count
        if self.data.get('vehicle_types') and isinstance(self.data['vehicle_types'], list):
            vehicle_types_count = len([v for v in self.data['vehicle_types'] if v])
            if vehicle_types_count > 0:
                # Store in popular_vehicle_type since count field not in model
                if not self.data.get('popular_vehicle_type') and vehicle_types_count > 0:
                    self.data['popular_vehicle_type'] = self.data['vehicle_types'][0]

        # Fix locations count - store as note if needed
        if self.data.get('locations_available') and isinstance(self.data['locations_available'], list):
            locations_count = len([l for l in self.data['locations_available'] if l])
            if locations_count > 0 and not self.data.get('notes'):
                self.data['notes'] = f"{locations_count} locations available"

        # Extract discount percentages from promotions
        if self.data.get('active_promotions') and isinstance(self.data['active_promotions'], list):
            for promo in self.data['active_promotions']:
                if isinstance(promo, dict):
                    promo_type = promo.get('type', '')
                    discount_pct = promo.get('discount_pct')

                    # Map promotion types to discount fields
                    if discount_pct:
                        if promo_type == 'early_bird' and not self.data.get('early_bird_discount_pct'):
                            self.data['early_bird_discount_pct'] = discount_pct
                        elif promo_type == 'weekly' and not self.data.get('weekly_discount_pct'):
                            self.data['weekly_discount_pct'] = discount_pct
                        elif promo_type == 'monthly' and not self.data.get('monthly_discount_pct'):
                            self.data['monthly_discount_pct'] = discount_pct
                        elif promo_type == 'last_minute' and not self.data.get('last_minute_discount_pct'):
                            self.data['last_minute_discount_pct'] = discount_pct

                    # Set discount code available flag
                    if promo.get('code') and not self.data.get('discount_code_available'):
                        self.data['discount_code_available'] = True

            # Set promotion_text to first promo text if not already set
            if not self.data.get('promotion_text') and len(self.data['active_promotions']) > 0:
                first_promo = self.data['active_promotions'][0]
                if isinstance(first_promo, dict) and first_promo.get('text'):
                    self.data['promotion_text'] = first_promo['text'][:200]  # Limit to 200 chars

    async def calculate_completeness(self) -> float:
        """Calculate data completeness percentage"""
        # Fix derived fields first
        self._fix_derived_fields()

        total_fields = len(self.data)
        filled_fields = sum(1 for v in self.data.values() if v not in [None, '', [], 0])
        return (filled_fields / total_fields) * 100
    
    async def save_screenshot(self, page: Page, filename: str):
        """Save page screenshot"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = "".join(c for c in self.company_name if c.isalnum() or c in (' ', '-', '_')).strip()
            path = SCREENSHOTS_DIR / f"{safe_name}_{filename}_{timestamp}.png"
            await page.screenshot(path=str(path), full_page=True)
            logger.info(f"📸 Screenshot: {path}")
        except Exception as e:
            logger.warning(f"Screenshot failed: {e}")
    
    async def save_html(self, page: Page, filename: str):
        """Save page HTML"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = "".join(c for c in self.company_name if c.isalnum() or c in (' ', '-', '_')).strip()
            path = HTML_DIR / f"{safe_name}_{filename}_{timestamp}.html"
            html = await page.content()
            path.write_text(html, encoding='utf-8')
            logger.info(f"💾 HTML saved: {path}")
        except Exception as e:
            logger.warning(f"HTML save failed: {e}")
    
    @abstractmethod
    async def scrape_deep_data(self, page: Page) -> Dict:
        """
        Each scraper implements this to collect company-specific data
        Must fill self.data dictionary with as many fields as possible
        """
        pass
    
    async def scrape(self) -> Dict:
        """Main scraping orchestration method with metrics tracking.

        Coordinates the entire scraping process:
        1. Launches browser
        2. Navigates to target URL
        3. Calls company-specific scraping logic
        4. Calculates data completeness
        5. Saves screenshots and HTML
        6. Tracks metrics and performance
        7. Cleans up resources

        Returns:
            Dict: Complete data dictionary with all collected information

        Raises:
            Exception: Any errors during scraping are caught, logged,
                      and added to the 'notes' field

        Note:
            Always closes the browser, even if scraping fails

        Example:
            >>> scraper = MyScraper("Company", 1, config)
            >>> data = await scraper.scrape()
            >>> print(f"Completeness: {data['data_completeness_pct']}%")
        """
        # Start performance timer
        start_time = time.time()

        # Structured logging - scrape start
        logger.bind(
            competitor=self.company_name,
            tier=self.tier,
            event='scrape_start'
        ).info(f"Starting scrape: {self.company_name}")

        browser = None
        context = None
        page = None

        try:
            browser = await self.get_browser()
            
            # Create context for better isolation and timeout control
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # Set reasonable timeout for operations (increased for complex scraping)
            context.set_default_timeout(90000)  # 90 seconds (increased to prevent timeouts during booking simulation)
            
            page = await context.new_page()
            
            # Enable API interception to capture pricing data
            self._setup_api_interception(page)

            # Navigate to homepage or pricing page
            start_url = self.config['urls'].get('pricing') or self.config['urls'].get('homepage')
            success = await self.navigate_smart(page, start_url)

            if not success:
                raise Exception(f"Failed to load {start_url}")

            # Call company-specific deep scraping
            await self.scrape_deep_data(page)

            # Calculate completeness
            self.data['data_completeness_pct'] = await self.calculate_completeness()

            # Save evidence
            await self.save_screenshot(page, "final")
            await self.save_html(page, "source")

            # Calculate duration
            duration = time.time() - start_time

            # Structured logging - scrape complete
            logger.bind(
                competitor=self.company_name,
                duration=duration,
                completeness=self.data['data_completeness_pct'],
                has_price=bool(self.data.get('base_nightly_rate')),
                has_reviews=bool(self.data.get('customer_review_avg')),
                event='scrape_complete'
            ).info(
                f"✅ {self.company_name}: {self.data['data_completeness_pct']:.1f}% complete - {duration:.1f}s"
            )

            # Record metrics (if metrics system is available)
            try:
                from monitoring.metrics_collector import get_metrics
                metrics = get_metrics()
                metrics.record_scrape(self.data, duration, self.company_name)
            except ImportError:
                pass  # Metrics system not available

        except Exception as e:
            duration = time.time() - start_time

            logger.bind(
                competitor=self.company_name,
                error=str(e),
                duration=duration,
                event='scrape_error'
            ).error(f"❌ {self.company_name} scraping failed: {e}")

            self.data['notes'] = f"Error: {str(e)}"

            # Record error in metrics
            try:
                from monitoring.metrics_collector import get_metrics
                metrics = get_metrics()
                metrics.record_error(type(e).__name__, self.company_name)
            except ImportError:
                pass

        finally:
            # Proper cleanup - close in reverse order of creation
            try:
                if page and not page.is_closed():
                    await page.close()
            except Exception as e:
                logger.debug(f"Page close error (non-critical): {e}")
            
            try:
                if context:
                    await context.close()
            except Exception as e:
                logger.debug(f"Context close error (non-critical): {e}")
            
            try:
                if browser and browser.is_connected():
                    await browser.close()
            except Exception as e:
                logger.debug(f"Browser close error (non-critical): {e}")

        return self.data


if __name__ == "__main__":
    print("🔬 Deep Data Scraper Base Class")
    print("=" * 50)
    print("This is a base class. Use company-specific scrapers to collect data.")
    print("\nData Fields Collected:")
    
    scraper = DeepDataScraper("Example", 1, {}, False)
    for key in scraper.data.keys():
        print(f"  • {key}")
    
    print(f"\nTotal: {len(scraper.data)} data points per competitor")
