# Quick Wins - Immediate Scraping Improvements

## 🎯 Top 3 Improvements to Implement Today

These changes will dramatically improve data quality with minimal effort.

---

## 1. API Interception (30 minutes) - HIGHEST IMPACT

### Why This Matters
- **10x cleaner data** - JSON instead of HTML parsing
- **More complete** - Gets all data before filtering
- **Less fragile** - No CSS selector maintenance

### Implementation

Add this to `scrapers/base_scraper.py`:

```python
async def monitor_api_calls(self, page):
    """Capture API calls for structured data"""
    self.api_responses = []
    
    async def handle_response(response):
        # Target common rental site APIs
        api_patterns = [
            '/api/search',
            '/api/listings',
            '/api/vehicles',
            '/api/pricing',
            '/api/availability',
            '/graphql',
            'search.json',
            'prices.json'
        ]
        
        if any(pattern in response.url for pattern in api_patterns):
            try:
                if response.status == 200:
                    data = await response.json()
                    self.api_responses.append({
                        'url': response.url,
                        'data': data,
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.info(f"🔍 Captured API: {response.url[:100]}")
            except Exception as e:
                logger.debug(f"API capture failed: {e}")
    
    page.on('response', handle_response)
    logger.info("👂 API monitoring active")
```

Then in `scrape()` method, add before navigation:

```python
# Start monitoring API calls
await self.monitor_api_calls(page)
```

And after scraping, extract from APIs:

```python
# Try to extract from captured APIs first
await self._extract_from_api_responses()
```

Add extraction method:

```python
async def _extract_from_api_responses(self):
    """Extract data from captured API calls"""
    for response in self.api_responses:
        data = response['data']
        
        # Handle different API formats
        if isinstance(data, dict):
            # Look for pricing data
            if 'price' in data or 'pricing' in data:
                self._extract_price_from_api(data)
            
            # Look for listing data
            if 'results' in data or 'listings' in data:
                self._extract_listings_from_api(data)
            
            # Look for vehicle data
            if 'vehicles' in data or 'fleet' in data:
                self._extract_fleet_from_api(data)
```

### Testing
```bash
# Run Goboony scraper and look for "Captured API" messages
python -c "import asyncio; from scrapers.tier1_scrapers import GoboonyScraper; asyncio.run(GoboonyScraper().scrape())"
```

---

## 2. Smart Content Loading (15 minutes) - HIGH IMPACT

### Why This Matters
- **Captures lazy-loaded content** - No more missing listings
- **Handles infinite scroll** - Modern UI patterns
- **More reliable** - Waits for actual content, not arbitrary timeouts

### Implementation

Replace this pattern:
```python
await asyncio.sleep(5)  # ❌ Blind waiting
```

With this:
```python
await self.wait_for_content_loaded(page)  # ✅ Smart waiting
```

Add to `base_scraper.py`:

```python
async def wait_for_content_loaded(self, page, timeout=30000):
    """Smart waiting for dynamic content"""
    try:
        # Strategy 1: Wait for common rental site elements
        selectors = [
            '[class*="price"]',
            '[data-testid*="price"]',
            '[class*="listing"]',
            'article',
            '[class*="vehicle"]'
        ]
        
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000, state='visible')
                logger.info(f"✅ Content loaded: {selector}")
                break
            except:
                continue
        
        # Strategy 2: Ensure network is idle
        await page.wait_for_load_state('networkidle', timeout=timeout)
        
        # Strategy 3: Scroll to trigger lazy loading
        await self.scroll_to_load_all(page)
        
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Content loading timeout: {e}")
        return False

async def scroll_to_load_all(self, page, max_scrolls=5):
    """Scroll page to trigger lazy-loaded content"""
    for i in range(max_scrolls):
        # Scroll to bottom
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(1)
        
        # Check if new content appeared
        current_height = await page.evaluate('document.body.scrollHeight')
        await asyncio.sleep(1)
        new_height = await page.evaluate('document.body.scrollHeight')
        
        if current_height == new_height:
            logger.info(f"✅ All content loaded after {i+1} scrolls")
            break
```

### Apply to Your Scrapers

In `tier1_scrapers.py`, update all scrapers:

```python
# In GoboonyScraper.scrape_deep_data():
# Replace:
await asyncio.sleep(3)

# With:
await self.wait_for_content_loaded(page)
```

---

## 3. Data Validation (20 minutes) - QUALITY IMPACT

### Why This Matters
- **Catches errors early** - No bad data in database
- **Quality metrics** - Know when scraping degrades
- **Debugging** - Identifies problematic sites

### Implementation

Add to `base_scraper.py`:

```python
def validate_scraped_data(self) -> Dict[str, bool]:
    """Validate data quality with detailed checks"""
    validation_results = {
        'price_valid': self._validate_price(),
        'reviews_valid': self._validate_reviews(),
        'completeness_ok': self._validate_completeness(),
        'sanity_check': self._validate_sanity()
    }
    
    # Log validation results
    passed = sum(validation_results.values())
    total = len(validation_results)
    
    if passed == total:
        logger.info(f"✅ Data validation: {passed}/{total} checks passed")
    else:
        failed = [k for k, v in validation_results.items() if not v]
        logger.warning(f"⚠️ Data validation: {passed}/{total} passed. Failed: {failed}")
    
    return validation_results

def _validate_price(self) -> bool:
    """Check if price is realistic"""
    price = self.data.get('base_nightly_rate')
    
    if price is None:
        logger.warning(f"⚠️ {self.company_name}: No price extracted")
        return False
    
    # Campervan rentals: €30-500/night is reasonable
    if not (30 <= price <= 500):
        logger.error(f"❌ {self.company_name}: Unrealistic price €{price}")
        return False
    
    return True

def _validate_reviews(self) -> bool:
    """Check if review data makes sense"""
    rating = self.data.get('customer_review_avg')
    count = self.data.get('review_count')
    
    # Rating out of range
    if rating and not (1.0 <= rating <= 5.0):
        logger.error(f"❌ {self.company_name}: Invalid rating {rating}")
        return False
    
    # Negative review count
    if count and count < 0:
        logger.error(f"❌ {self.company_name}: Invalid review count {count}")
        return False
    
    # Suspicious: Perfect rating with few reviews
    if rating == 5.0 and 0 < count < 5:
        logger.warning(f"⚠️ {self.company_name}: Suspicious - 5.0★ with only {count} reviews")
        # Not a failure, just suspicious
    
    return True

def _validate_completeness(self) -> bool:
    """Check if minimum data was extracted"""
    completeness = self.data.get('data_completeness_pct', 0)
    
    if completeness < 25:
        logger.error(f"❌ {self.company_name}: Very low completeness {completeness:.1f}%")
        return False
    
    if completeness < 40:
        logger.warning(f"⚠️ {self.company_name}: Low completeness {completeness:.1f}%")
    
    return True

def _validate_sanity(self) -> bool:
    """Cross-field sanity checks"""
    issues = []
    
    # Check: Insurance shouldn't exceed base price
    if (self.data.get('insurance_cost_per_day', 0) > 
        self.data.get('base_nightly_rate', 999)):
        issues.append("Insurance > base price")
    
    # Check: Cleaning fee shouldn't be extreme
    if (self.data.get('cleaning_fee', 0) > 
        self.data.get('base_nightly_rate', 999) * 3):
        issues.append("Cleaning fee > 3x base price")
    
    # Check: Monthly discount should be > weekly
    weekly = self.data.get('weekly_discount_pct', 0)
    monthly = self.data.get('monthly_discount_pct', 0)
    if monthly > 0 and weekly > monthly:
        issues.append("Weekly discount > monthly discount")
    
    if issues:
        logger.warning(f"⚠️ {self.company_name}: Sanity checks failed: {', '.join(issues)}")
        return False
    
    return True
```

Then in `scrape()` method, add before saving:

```python
# Validate data before saving
validation = self.validate_scraped_data()
self.data['validation_passed'] = all(validation.values())
self.data['validation_issues'] = [k for k, v in validation.items() if not v]
```

---

## 🚀 Implementation Checklist

### Step 1: Add API Monitoring (30 min)
- [ ] Add `monitor_api_calls()` to base_scraper.py
- [ ] Add `_extract_from_api_responses()` to base_scraper.py
- [ ] Test with Goboony (React app, definitely has APIs)
- [ ] Check logs for "🔍 Captured API" messages

### Step 2: Smart Content Loading (15 min)
- [ ] Add `wait_for_content_loaded()` to base_scraper.py
- [ ] Add `scroll_to_load_all()` to base_scraper.py
- [ ] Replace `asyncio.sleep()` in GoboonyScraper
- [ ] Replace `asyncio.sleep()` in YescapaScraper
- [ ] Test and verify more content loads

### Step 3: Data Validation (20 min)
- [ ] Add `validate_scraped_data()` to base_scraper.py
- [ ] Add all validation helper methods
- [ ] Add validation call in `scrape()` method
- [ ] Run full scrape and check validation logs

### Step 4: Test Everything (15 min)
- [ ] Run: `python run_intelligence.py`
- [ ] Check logs for new validation messages
- [ ] Verify completeness hasn't dropped
- [ ] Check for "Captured API" messages

**Total Time: ~1.5 hours**
**Expected Impact: +5-10% completeness, much cleaner data**

---

## 📊 Expected Results

### Before
```
Goboony: 61.9% complete
- Prices from HTML parsing
- Some lazy-loaded content missed
- No data validation
```

### After
```
Goboony: 70%+ complete
- Prices from API + HTML (redundancy)
- All lazy-loaded content captured
- Validated, high-quality data
- Detailed quality metrics
```

---

## 🔍 Debugging Tips

### If API Capture Shows Nothing
```python
# Add more logging
logger.info(f"All response URLs seen: {[r.url for r in page.responses]}")
```

### If Validation Fails Everything
```python
# Adjust thresholds
if not (20 <= price <= 600):  # More lenient
```

### If Content Loading Hangs
```python
# Reduce timeout
await page.wait_for_selector(selector, timeout=3000)  # 3s instead of 30s
```

---

## 📈 Measuring Success

Run this before and after:
```bash
python generate_insights.py | grep "Average Data Completeness"
```

**Target**: +5 percentage points
**Expected**: 64% → 69%+

---

## 🎯 Next Steps After Quick Wins

1. **Implement for All Scrapers** - Roll out to all 8 competitors
2. **Add More API Patterns** - Learn each site's specific APIs
3. **Create Validation Dashboard** - Track quality over time
4. **Set Up Alerts** - Notify when validation fails

---

**Ready to Implement?** Start with API monitoring - it has the biggest impact!


