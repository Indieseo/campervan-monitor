# 🛠️ Implementation Guide - Critical Fixes
**Quick reference for implementing the most important improvements**

---

## 🎯 PRIORITY 1: Fix Price Extraction

### Current Problem
```python
# Returns this:
base_nightly_rate: 0.0

# Should return:
base_nightly_rate: 85.0
```

### Solution: Enhanced Booking Simulation

**File:** `scrapers/tier1_scrapers.py`

#### Step 1: Improve API Monitoring
Replace the current `_simulate_booking_for_pricing()` method:

```python
async def _simulate_booking_for_pricing(self, page):
    """Enhanced booking simulation with comprehensive strategies"""
    
    # Strategy 1: Monitor API requests (IMPROVED)
    api_prices = []
    booking_api_responses = []
    
    async def handle_response(response):
        """Monitor ALL responses for pricing data"""
        try:
            url = response.url.lower()
            
            # Check if this might contain pricing
            pricing_keywords = [
                'price', 'booking', 'search', 'quote', 'availability',
                'vehicle', 'rent', 'rate', 'cost', 'api', 'graphql'
            ]
            
            if any(keyword in url for keyword in pricing_keywords):
                if response.status == 200:
                    try:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'json' in content_type:
                            data = await response.json()
                            booking_api_responses.append({
                                'url': url,
                                'data': data
                            })
                            
                            # Extract prices from JSON
                            prices = self._extract_prices_from_json_recursive(data)
                            if prices:
                                api_prices.extend(prices)
                                logger.info(f"📡 Found {len(prices)} prices in API: {url[:60]}...")
                                
                    except Exception as e:
                        logger.debug(f"Could not parse response: {e}")
        except Exception as e:
            logger.debug(f"Response handler error: {e}")
    
    # Attach listener BEFORE any interactions
    page.on('response', handle_response)
    
    # Strategy 2: Wait for page to fully load
    await asyncio.sleep(3)
    
    # Strategy 3: Look for and click booking triggers
    await self._click_booking_trigger(page)
    
    # Strategy 4: Try to fill booking form
    form_filled = await self._fill_booking_form_comprehensive(page)
    
    if form_filled:
        # Wait for results to load
        await asyncio.sleep(5)
        
        # Check for price in results
        price = await self._extract_price_from_results(page)
        if price:
            self.data['base_nightly_rate'] = price
            self.data['is_estimated'] = False
            logger.info(f"✅ Booking simulation price: €{price}/night")
            return
    
    # Strategy 5: Check collected API prices
    if api_prices:
        # Filter reasonable prices and take median
        valid_prices = [p for p in api_prices if 30 <= p <= 400]
        if valid_prices:
            price = statistics.median(valid_prices)
            self.data['base_nightly_rate'] = price
            self.data['is_estimated'] = False
            logger.info(f"✅ API extracted price: €{price}/night")
            return
    
    # Strategy 6: Parse embedded JSON-LD
    price = await self._extract_from_json_ld(page)
    if price:
        self.data['base_nightly_rate'] = price
        self.data['is_estimated'] = True
        logger.info(f"✅ JSON-LD price: €{price}/night")
        return
    
    # Strategy 7: Static page scraping (fallback)
    await self._scrape_pricing_page_static(page)
    
    if not self.data.get('base_nightly_rate') or self.data['base_nightly_rate'] == 0:
        logger.warning("⚠️ Could not extract pricing after all strategies")


async def _extract_prices_from_json_recursive(self, data, depth=0, max_depth=5):
    """Recursively search JSON for price values"""
    if depth > max_depth:
        return []
    
    prices = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if this is a price field
            if any(keyword in key_lower for keyword in [
                'price', 'rate', 'cost', 'total', 'amount', 'nightly'
            ]):
                if isinstance(value, (int, float)) and 20 <= value <= 500:
                    prices.append(float(value))
                elif isinstance(value, str):
                    # Try to extract number from string
                    match = re.search(r'(\d+(?:\.\d{2})?)', value)
                    if match:
                        price = float(match.group(1))
                        if 20 <= price <= 500:
                            prices.append(price)
            
            # Recurse into nested structures
            if isinstance(value, (dict, list)):
                prices.extend(self._extract_prices_from_json_recursive(value, depth+1, max_depth))
    
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                prices.extend(self._extract_prices_from_json_recursive(item, depth+1, max_depth))
    
    return prices


async def _click_booking_trigger(self, page):
    """Try to click booking/search trigger buttons"""
    
    # Comprehensive list of possible triggers
    triggers = [
        # Text-based selectors
        'button:has-text("Book")',
        'button:has-text("Search")',
        'button:has-text("Find")',
        'button:has-text("Check availability")',
        'button:has-text("Get quote")',
        'button:has-text("Reserve")',
        'a:has-text("Book now")',
        'a:has-text("Search")',
        
        # Class/ID-based selectors
        '[class*="booking-button"]',
        '[class*="search-button"]',
        '[class*="cta-button"]',
        '[class*="book-now"]',
        '[id*="booking"]',
        '[id*="search"]',
        
        # Data attribute selectors
        '[data-testid*="booking"]',
        '[data-testid*="search"]',
        '[data-action="booking"]',
        '[data-action="search"]',
        
        # Specific competitor patterns
        '.booking-widget-trigger',
        '.search-form-trigger',
        '#open-booking',
    ]
    
    for trigger in triggers:
        try:
            if await page.locator(trigger).count() > 0:
                await page.click(trigger, timeout=3000)
                logger.info(f"✅ Clicked trigger: {trigger}")
                await asyncio.sleep(2)
                return True
        except Exception as e:
            logger.debug(f"Trigger {trigger} failed: {e}")
            continue
    
    logger.debug("No booking trigger found")
    return False


async def _fill_booking_form_comprehensive(self, page):
    """Fill booking form with multiple strategies"""
    
    # Sample dates (7 days from now, 7-day rental)
    start_date = datetime.now() + timedelta(days=7)
    end_date = start_date + timedelta(days=7)
    
    # Date format variations
    date_formats = [
        start_date.strftime('%Y-%m-%d'),
        start_date.strftime('%d/%m/%Y'),
        start_date.strftime('%m/%d/%Y'),
        start_date.strftime('%d.%m.%Y'),
    ]
    
    # Strategy 1: Fill input[type="date"]
    date_inputs = await page.query_selector_all('input[type="date"]')
    if len(date_inputs) >= 2:
        try:
            await date_inputs[0].fill(date_formats[0])
            await date_inputs[1].fill((start_date + timedelta(days=7)).strftime('%Y-%m-%d'))
            logger.info("✅ Filled date inputs (type=date)")
            success = True
        except Exception as e:
            logger.debug(f"Date input fill failed: {e}")
            success = False
    
    # Strategy 2: Fill named inputs
    start_input = await page.query_selector(
        'input[name*="start"], input[name*="pickup"], input[name*="from"]'
    )
    end_input = await page.query_selector(
        'input[name*="end"], input[name*="dropoff"], input[name*="to"]'
    )
    
    if start_input and end_input:
        for date_format in date_formats:
            try:
                await start_input.fill(date_format)
                await asyncio.sleep(0.3)
                await end_input.fill(end_date.strftime('%Y-%m-%d'))
                await asyncio.sleep(0.3)
                logger.info(f"✅ Filled named inputs with format: {date_format}")
                success = True
                break
            except Exception as e:
                logger.debug(f"Named input fill failed: {e}")
                continue
    
    # Strategy 3: JavaScript value setting (bypass validation)
    try:
        await page.evaluate('''(dates) => {
            const startInputs = document.querySelectorAll('input[name*="start"], input[name*="pickup"]');
            const endInputs = document.querySelectorAll('input[name*="end"], input[name*="dropoff"]');
            
            if (startInputs[0]) startInputs[0].value = dates.start;
            if (endInputs[0]) endInputs[0].value = dates.end;
        }''', {
            'start': date_formats[0],
            'end': end_date.strftime('%Y-%m-%d')
        })
        logger.info("✅ Set dates via JavaScript")
    except Exception as e:
        logger.debug(f"JavaScript date setting failed: {e}")
    
    # Fill location if needed
    await self._fill_location_field(page)
    
    # Try to submit form
    submit_success = await self._submit_booking_form(page)
    
    return submit_success


async def _fill_location_field(self, page):
    """Fill location/station field"""
    
    location_selectors = [
        'select[name*="location"]',
        'select[name*="station"]',
        'select[name*="pickup"]',
        'input[name*="location"]',
        '[data-testid*="location"]',
    ]
    
    for selector in location_selectors:
        try:
            element = await page.query_selector(selector)
            if not element:
                continue
            
            tag_name = await element.evaluate('el => el.tagName')
            
            if tag_name.lower() == 'select':
                # Select first real option (skip placeholder)
                await element.select_option(index=1)
                logger.info("✅ Selected location from dropdown")
                return True
            else:
                # For input, try to trigger autocomplete
                await element.click()
                await asyncio.sleep(0.5)
                await page.keyboard.press('ArrowDown')
                await asyncio.sleep(0.3)
                await page.keyboard.press('Enter')
                logger.info("✅ Selected location from autocomplete")
                return True
                
        except Exception as e:
            logger.debug(f"Location fill failed for {selector}: {e}")
            continue
    
    return False


async def _submit_booking_form(self, page):
    """Try to submit the booking form"""
    
    submit_selectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Search")',
        'button:has-text("Submit")',
        'button:has-text("Continue")',
        'button:has-text("Next")',
        '[data-testid*="submit"]',
        '[data-testid*="search"]',
    ]
    
    for selector in submit_selectors:
        try:
            if await page.locator(selector).count() > 0:
                await page.click(selector, timeout=3000)
                logger.info(f"✅ Clicked submit: {selector}")
                await asyncio.sleep(3)  # Wait for results
                return True
        except Exception as e:
            logger.debug(f"Submit failed for {selector}: {e}")
            continue
    
    # Try pressing Enter in form
    try:
        await page.keyboard.press('Enter')
        logger.info("✅ Submitted via Enter key")
        await asyncio.sleep(3)
        return True
    except Exception as e:
        logger.debug(f"Enter key submit failed: {e}")
    
    return False


async def _extract_price_from_results(self, page):
    """Extract price from booking results page"""
    
    # Wait for results to appear
    result_selectors = [
        '.vehicle-card',
        '.search-result',
        '.booking-result',
        '[class*="vehicle"]',
        '[class*="result"]',
    ]
    
    for selector in result_selectors:
        try:
            if await page.locator(selector).count() > 0:
                await page.wait_for_selector(selector, timeout=5000)
                break
        except:
            continue
    
    # Extract all visible prices
    page_text = await page.evaluate('() => document.body.innerText')
    prices = await self.extract_prices_from_text(page_text)
    
    if prices:
        # Filter for per-night prices
        night_prices = [p for p in prices if 30 <= p <= 400]
        if night_prices:
            # Take the minimum (usually base price)
            return min(night_prices)
    
    # Try specific price selectors
    price_selectors = [
        '[class*="price"]',
        '[class*="rate"]',
        '[class*="cost"]',
        '[data-testid*="price"]',
    ]
    
    for selector in price_selectors:
        try:
            elements = await page.query_selector_all(selector)
            for element in elements[:5]:  # Check first 5
                text = await element.inner_text()
                matches = re.findall(r'€?\s*(\d+(?:\.\d{2})?)', text)
                for match in matches:
                    price = float(match)
                    if 30 <= price <= 400:
                        return price
        except Exception as e:
            logger.debug(f"Price selector {selector} failed: {e}")
            continue
    
    return None


async def _extract_from_json_ld(self, page):
    """Extract price from JSON-LD structured data"""
    
    try:
        json_ld_data = await page.evaluate('''() => {
            const scripts = document.querySelectorAll('script[type="application/ld+json"]');
            return Array.from(scripts).map(s => {
                try {
                    return JSON.parse(s.textContent);
                } catch(e) {
                    return null;
                }
            }).filter(d => d !== null);
        }''')
        
        for data in json_ld_data:
            # Check for Product or Service type with offers
            if isinstance(data, dict):
                if 'offers' in data:
                    offers = data['offers']
                    if isinstance(offers, dict) and 'price' in offers:
                        price = float(offers['price'])
                        if 30 <= price <= 400:
                            return price
                    elif isinstance(offers, list):
                        for offer in offers:
                            if 'price' in offer:
                                price = float(offer['price'])
                                if 30 <= price <= 400:
                                    return price
    
    except Exception as e:
        logger.debug(f"JSON-LD extraction failed: {e}")
    
    return None
```

**Testing:**
```python
# Test with Roadsurfer
scraper = RoadsurferScraper(use_browserless=False)
result = await scraper.scrape()
assert result['base_nightly_rate'] > 0, "Price extraction failed!"
print(f"✅ Price: €{result['base_nightly_rate']}")
```

---

## 🎯 PRIORITY 2: Fix Review Extraction

### Current Problem
```python
customer_review_avg: None
review_count: None
```

### Solution: Multi-Page Review Search

**File:** `scrapers/base_scraper.py`

Replace `extract_customer_reviews()` method:

```python
async def extract_customer_reviews(self, page: Page) -> Dict:
    """Comprehensive review extraction with fallbacks"""
    
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
            await self.navigate_smart(page, homepage_url)
            review_data = await self._check_page_for_reviews(page)
            if review_data['avg'] or review_data['count']:
                return review_data
    
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
    """Check current page for review data"""
    
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
                # Try to extract from attributes
                rating = await element.get_attribute('data-score')
                if rating:
                    return {
                        'avg': float(rating),
                        'count': None,
                        'source': 'trustpilot_widget'
                    }
                
                # Try to extract from inner content
                text = await element.inner_text()
                match = re.search(r'(\d+\.?\d*)\s*out of\s*5', text, re.IGNORECASE)
                if match:
                    return {
                        'avg': float(match.group(1)),
                        'count': None,
                        'source': 'trustpilot_text'
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
                # Try attribute first
                rating = await element.get_attribute('data-rating')
                if not rating:
                    rating = await element.get_attribute('content')
                if not rating:
                    text = await element.inner_text()
                    match = re.search(r'(\d+\.?\d*)', text)
                    if match:
                        rating = match.group(1)
                
                if rating:
                    rating_float = float(rating)
                    if 0 <= rating_float <= 5:
                        return {
                            'avg': rating_float,
                            'count': None,
                            'source': 'generic_element'
                        }
    except Exception as e:
        logger.debug(f"Generic element check failed: {e}")
    
    # 4. Text pattern matching
    try:
        page_text = await page.evaluate('() => document.body.innerText')
        
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
                rating = float(match.group(1))
                if 0 <= rating <= 5:
                    return {
                        'avg': rating,
                        'count': None,
                        'source': 'text_pattern'
                    }
        
        # Match review count patterns
        count_patterns = [
            r'(\d+)\s*reviews?',
            r'based on\s*(\d+)',
            r'(\d+)\s*ratings?',
        ]
        
        for pattern in count_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                count = int(match.group(1))
                if 0 < count < 1000000:
                    return {
                        'avg': None,
                        'count': count,
                        'source': 'text_count'
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
```

**Testing:**
```python
# Test review extraction
scraper = RoadsurferScraper(use_browserless=False)
browser = await scraper.get_browser()
page = await browser.new_page()
await page.goto("https://roadsurfer.com")

reviews = await scraper.extract_customer_reviews(page)
assert reviews['avg'] is not None or reviews['count'] is not None
print(f"✅ Reviews: {reviews['avg']}★ ({reviews['count']} reviews)")
```

---

## 🎯 PRIORITY 3: Add Retry Logic & Error Handling

### Create Resilient Scraper Wrapper

**File:** `scrapers/resilient_wrapper.py` (NEW FILE)

```python
"""
Resilient scraper wrapper with retry logic and error handling
"""

import asyncio
import time
from typing import Dict, Callable, Any
from loguru import logger
from functools import wraps


class RetryConfig:
    """Retry configuration"""
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 5.0,
        backoff_multiplier: float = 2.0,
        max_delay: float = 60.0
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay


def with_retry(retry_config: RetryConfig = None):
    """Decorator to add retry logic to async functions"""
    
    if retry_config is None:
        retry_config = RetryConfig()
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = retry_config.initial_delay
            
            for attempt in range(1, retry_config.max_attempts + 1):
                try:
                    logger.info(f"Attempt {attempt}/{retry_config.max_attempts}: {func.__name__}")
                    result = await func(*args, **kwargs)
                    
                    # Validate result
                    if _is_valid_result(result):
                        if attempt > 1:
                            logger.info(f"✅ Success on attempt {attempt}")
                        return result
                    else:
                        logger.warning(f"Invalid result on attempt {attempt}, retrying...")
                        raise ValueError("Invalid result returned")
                
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt} failed: {e}")
                    
                    if attempt < retry_config.max_attempts:
                        logger.info(f"Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        delay = min(delay * retry_config.backoff_multiplier, retry_config.max_delay)
                    else:
                        logger.error(f"All {retry_config.max_attempts} attempts failed")
            
            # All attempts failed
            raise last_exception
        
        return wrapper
    return decorator


def _is_valid_result(result: Any) -> bool:
    """Check if scraping result is valid"""
    
    if not result:
        return False
    
    if not isinstance(result, dict):
        return False
    
    # Check for critical fields
    if 'company_name' not in result:
        return False
    
    # Check data completeness
    completeness = result.get('data_completeness_pct', 0)
    if completeness < 20:  # At least 20% complete
        return False
    
    return True


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 300.0,
        expected_exception: Exception = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    async def call(self, func: Callable, *args, **kwargs):
        """Call function with circuit breaker protection"""
        
        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half-open'
                logger.info("Circuit breaker: half-open, attempting reset")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is open. Too many failures. "
                    f"Will retry after {self.recovery_timeout}s"
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = 'closed'
        logger.debug("Circuit breaker: closed")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
            logger.error(
                f"Circuit breaker: OPEN after {self.failure_count} failures"
            )


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class ResilientScraper:
    """Wrapper for scrapers with resilience patterns"""
    
    def __init__(self, scraper, retry_config: RetryConfig = None):
        self.scraper = scraper
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker = CircuitBreaker()
    
    @with_retry()
    async def scrape_with_resilience(self) -> Dict:
        """Scrape with retry logic and circuit breaker"""
        
        return await self.circuit_breaker.call(
            self.scraper.scrape
        )
```

**Usage:**
```python
from scrapers.resilient_wrapper import ResilientScraper, RetryConfig
from scrapers.tier1_scrapers import RoadsurferScraper

# Create scraper
base_scraper = RoadsurferScraper(use_browserless=False)

# Wrap with resilience
retry_config = RetryConfig(max_attempts=3, initial_delay=5.0)
resilient_scraper = ResilientScraper(base_scraper, retry_config)

# Scrape with automatic retries
try:
    result = await resilient_scraper.scrape_with_resilience()
    print(f"✅ Success: {result['company_name']}")
except Exception as e:
    print(f"❌ Failed after all retries: {e}")
```

---

## 📝 Quick Testing Script

**File:** `test_critical_fixes.py` (NEW FILE)

```python
"""
Quick test script for critical fixes
"""

import asyncio
from scrapers.tier1_scrapers import RoadsurferScraper
from scrapers.resilient_wrapper import ResilientScraper, RetryConfig
from loguru import logger


async def test_price_extraction():
    """Test price extraction"""
    print("\n" + "="*60)
    print("TEST 1: Price Extraction")
    print("="*60)
    
    scraper = RoadsurferScraper(use_browserless=False)
    result = await scraper.scrape()
    
    price = result.get('base_nightly_rate')
    
    if price and price > 0:
        print(f"✅ PASS: Price extracted = €{price}/night")
        return True
    else:
        print(f"❌ FAIL: Price = {price}")
        return False


async def test_review_extraction():
    """Test review extraction"""
    print("\n" + "="*60)
    print("TEST 2: Review Extraction")
    print("="*60)
    
    scraper = RoadsurferScraper(use_browserless=False)
    result = await scraper.scrape()
    
    rating = result.get('customer_review_avg')
    count = result.get('review_count')
    
    if rating or count:
        print(f"✅ PASS: Reviews = {rating}★ ({count} reviews)")
        return True
    else:
        print(f"❌ FAIL: No reviews found")
        return False


async def test_data_completeness():
    """Test data completeness"""
    print("\n" + "="*60)
    print("TEST 3: Data Completeness")
    print("="*60)
    
    scraper = RoadsurferScraper(use_browserless=False)
    result = await scraper.scrape()
    
    completeness = result.get('data_completeness_pct', 0)
    
    if completeness >= 50:
        print(f"✅ PASS: Completeness = {completeness:.1f}%")
        return True
    else:
        print(f"⚠️  PARTIAL: Completeness = {completeness:.1f}% (target: 60%)")
        return False


async def test_resilience():
    """Test retry logic"""
    print("\n" + "="*60)
    print("TEST 4: Resilience & Retry Logic")
    print("="*60)
    
    base_scraper = RoadsurferScraper(use_browserless=False)
    retry_config = RetryConfig(max_attempts=2)
    resilient_scraper = ResilientScraper(base_scraper, retry_config)
    
    try:
        result = await resilient_scraper.scrape_with_resilience()
        print(f"✅ PASS: Resilient scraping succeeded")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 CRITICAL FIXES TEST SUITE")
    print("="*60)
    
    tests = [
        test_price_extraction,
        test_review_extraction,
        test_data_completeness,
        test_resilience,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n✅ All tests passed! Ready for production.")
    elif passed >= total * 0.75:
        print("\n⚠️  Most tests passed. Minor fixes needed.")
    else:
        print("\n❌ Many tests failed. More work needed.")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
```

**Run tests:**
```bash
python test_critical_fixes.py
```

---

## 🚀 Implementation Checklist

### Day 1: Price Extraction
- [ ] Update `_simulate_booking_for_pricing()` with enhanced API monitoring
- [ ] Add `_extract_prices_from_json_recursive()` method
- [ ] Add `_click_booking_trigger()` method
- [ ] Add `_fill_booking_form_comprehensive()` method
- [ ] Add `_extract_price_from_results()` method
- [ ] Add `_extract_from_json_ld()` method
- [ ] Test on Roadsurfer
- [ ] Verify price > 0

### Day 2: Review Extraction
- [ ] Replace `extract_customer_reviews()` method
- [ ] Add `_check_page_for_reviews()` method
- [ ] Add `_check_footer_for_reviews()` method
- [ ] Add `_scrape_trustpilot()` method
- [ ] Add `_check_google_reviews()` method
- [ ] Test on Roadsurfer
- [ ] Verify rating or count > 0

### Day 3: Error Handling
- [ ] Create `scrapers/resilient_wrapper.py`
- [ ] Implement `RetryConfig` class
- [ ] Implement `with_retry` decorator
- [ ] Implement `CircuitBreaker` class
- [ ] Implement `ResilientScraper` class
- [ ] Update `run_intelligence.py` to use resilient scraper
- [ ] Test failure scenarios

### Day 4: Testing
- [ ] Create `test_critical_fixes.py`
- [ ] Implement all test functions
- [ ] Run test suite
- [ ] Fix any failing tests
- [ ] Achieve 100% pass rate

### Day 5: Rollout to Other Competitors
- [ ] Test McRent scraper
- [ ] Test Goboony scraper
- [ ] Test Yescapa scraper
- [ ] Test Camperdays scraper
- [ ] Verify all 5 competitors working

---

## 📊 Expected Results

### Before Fixes
```
Company: Roadsurfer
base_nightly_rate: €0.0           ❌
customer_review_avg: None          ❌
data_completeness_pct: 31.7%       ⚠️
```

### After Fixes
```
Company: Roadsurfer
base_nightly_rate: €85.0           ✅
customer_review_avg: 4.3★          ✅
review_count: 2,451                ✅
data_completeness_pct: 62.8%       ✅
```

---

## 🆘 Troubleshooting

### If price extraction still fails:
1. Check logs for "Found X prices in API"
2. Manually test booking form on website
3. Use browser DevTools to find correct selectors
4. Add company-specific logic if needed

### If review extraction still fails:
1. Check if reviews exist on the website
2. Try Trustpilot URL manually
3. Check footer for review badges
4. Add company-specific review logic

### If tests fail:
1. Run with browser visible (headless=False)
2. Add more logging
3. Save screenshots on failure
4. Check network tab for API calls

---

**Ready to implement? Start with Day 1: Price Extraction**








