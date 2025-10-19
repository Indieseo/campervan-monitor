# 🎯 **CLAUDE CODE COMPREHENSIVE SCRAPING PROMPT**

## **MISSION:** Get Real Data from ALL 8 Competitors

### **Current Status:**
- ✅ **5/8 companies working** (Roadsurfer, Camperdays, Goboony, Outdoorsy, RVshare)
- ❌ **3/8 companies failing** (McRent, Yescapa, Cruise America)
- **Target:** 100% success rate with real pricing data

---

## 🚨 **CRITICAL FAILURES TO FIX:**

### **1. McRent (Error Pages)**
- **Issue:** All URLs returning error pages
- **Attempted:** 8 different strategies
- **URLs tried:** 
  - https://www.mcrent.de/
  - https://www.mcrent.de/en/
  - https://www.mcrent.de/en/motorhome-rental/
  - https://www.mcrent.de/en/motorhome-rental/germany/

### **2. Yescapa (Cookie Popups Blocking)**
- **Issue:** Cookie consent popups preventing access
- **Attempted:** 6 different strategies
- **URLs tried:**
  - https://www.yescapa.com/
  - https://www.yescapa.com/motorhome-hire-germany
  - https://www.yescapa.com/motorhome-hire-germany-munich

### **3. Cruise America (Error Pages)**
- **Issue:** All URLs returning error pages
- **Attempted:** 8 different strategies
- **URLs tried:**
  - https://www.cruiseamerica.com/
  - https://www.cruiseamerica.com/find-rv
  - https://www.cruiseamerica.com/locations
  - https://www.cruiseamerica.com/locations/los-angeles-ca

---

## 🛠️ **COMPREHENSIVE SOLUTION STRATEGY:**

### **Phase 1: Advanced Cookie Handling**
```python
# Implement multiple cookie bypass strategies
def handle_cookie_popup_advanced(driver):
    strategies = [
        # Strategy 1: Common cookie button selectors
        ['button[id*="accept"]', 'button[class*="accept"]', 'button[class*="cookie"]'],
        # Strategy 2: Text-based detection
        ['button:contains("Accept")', 'button:contains("OK")', 'button:contains("I agree")'],
        # Strategy 3: Modal/overlay detection
        ['div[class*="cookie"] button', 'div[id*="cookie"] button'],
        # Strategy 4: JavaScript execution
        ['document.querySelectorAll("button")[0].click()'],
        # Strategy 5: ESC key press
        ['driver.press_key("Escape")']
    ]
```

### **Phase 2: Multiple Browser Engines**
```python
# Test with different browser engines
browser_engines = [
    'chrome',      # Current
    'firefox',     # Alternative
    'edge',        # Windows native
    'safari'       # If available
]
```

### **Phase 3: Advanced Anti-Detection**
```python
# Enhanced stealth configuration
stealth_config = {
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'viewport': {'width': 1920, 'height': 1080},
    'headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    },
    'disable_images': False,
    'disable_css': False,
    'disable_javascript': False
}
```

### **Phase 4: Alternative URL Discovery**
```python
# Research and test alternative URLs
alternative_urls = {
    'McRent': [
        'https://mcrent.com/',  # Alternative domain
        'https://www.mcrent.com/en/',  # Different TLD
        'https://mcrent.de/en/motorhome-rental/',  # Direct path
        'https://www.mcrent.de/de/',  # German version
        'https://mcrent.de/en/rental/',  # Alternative path
    ],
    'Yescapa': [
        'https://yescapa.fr/',  # French version
        'https://www.yescapa.com/en/',  # English version
        'https://yescapa.com/motorhome-rental/',  # Alternative path
        'https://www.yescapa.com/rent/',  # Short path
    ],
    'Cruise America': [
        'https://cruiseamerica.com/',  # Without www
        'https://www.cruiseamerica.com/rent/',  # Alternative path
        'https://cruiseamerica.com/locations/',  # Direct locations
        'https://www.cruiseamerica.com/rv-rental/',  # Alternative path
    ]
}
```

### **Phase 5: Proxy and VPN Rotation**
```python
# Implement proxy rotation for blocked IPs
proxy_list = [
    'http://proxy1:port',
    'http://proxy2:port',
    'http://proxy3:port'
]

def rotate_proxy():
    # Rotate through proxy list
    # Test each proxy with target sites
    pass
```

### **Phase 6: Mobile User Agent Testing**
```python
# Test with mobile user agents
mobile_user_agents = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)',
    'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
    'Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X)'
]
```

---

## 🎯 **SPECIFIC TASKS FOR CLAUDE CODE:**

### **Task 1: McRent Deep Analysis**
```python
# 1. Test all alternative URLs
# 2. Check if site is down or blocking
# 3. Try different user agents
# 4. Test with and without JavaScript
# 5. Check for redirects or CAPTCHAs
# 6. Test mobile version
# 7. Check if site requires specific headers
```

### **Task 2: Yescapa Cookie Bypass**
```python
# 1. Implement advanced cookie detection
# 2. Try multiple cookie button selectors
# 3. Use JavaScript to bypass cookies
# 4. Test with different browsers
# 5. Try incognito/private mode
# 6. Test with disabled cookies
# 7. Use browser automation to click cookies
```

### **Task 3: Cruise America Error Resolution**
```python
# 1. Test all alternative URLs
# 2. Check for maintenance mode
# 3. Test with different regions
# 4. Try mobile version
# 5. Check for IP blocking
# 6. Test with VPN/proxy
# 7. Verify site is actually accessible
```

---

## 🔧 **IMPLEMENTATION PLAN:**

### **Step 1: Create Enhanced Scraper**
```python
# File: scrapers/ultimate_competitor_scraper.py
class UltimateCompetitorScraper:
    def __init__(self):
        self.browser_engines = ['chrome', 'firefox', 'edge']
        self.proxy_list = self.load_proxies()
        self.user_agents = self.load_user_agents()
    
    def scrape_with_fallback(self, company, urls):
        # Try multiple strategies in sequence
        for engine in self.browser_engines:
            for url in urls:
                for user_agent in self.user_agents:
                    result = self.attempt_scrape(engine, url, user_agent)
                    if result['success']:
                        return result
        return {'success': False, 'error': 'All strategies failed'}
```

### **Step 2: Advanced Cookie Handler**
```python
# File: scrapers/advanced_cookie_handler.py
class AdvancedCookieHandler:
    def handle_cookies(self, driver):
        strategies = [
            self.click_cookie_buttons,
            self.javascript_cookie_bypass,
            self.keyboard_cookie_bypass,
            self.wait_and_retry,
            self.force_navigation
        ]
        
        for strategy in strategies:
            if strategy(driver):
                return True
        return False
```

### **Step 3: URL Discovery System**
```python
# File: scrapers/url_discovery.py
class URLDiscovery:
    def discover_working_urls(self, company):
        # 1. Test common URL patterns
        # 2. Check for redirects
        # 3. Test mobile versions
        # 4. Check for alternative domains
        # 5. Test with different paths
        pass
```

---

## 📊 **SUCCESS METRICS:**

### **Target Results:**
- **McRent:** Get 7-day pricing data (EUR)
- **Yescapa:** Get 7-day pricing data (EUR)
- **Cruise America:** Get 7-day pricing data (USD)

### **Data Requirements:**
```json
{
    "company_name": "McRent",
    "daily_prices": [
        {"date": "2025-10-18", "price": 85.50, "currency": "EUR"},
        {"date": "2025-10-19", "price": 92.30, "currency": "EUR"},
        // ... 7 days total
    ],
    "total_results": 7,
    "min_price": 85.50,
    "max_price": 125.80,
    "avg_price": 105.65,
    "success": true
}
```

---

## 🚀 **EXECUTION COMMANDS:**

### **1. Run Enhanced Scraper**
```bash
python scrapers/ultimate_competitor_scraper.py
```

### **2. Test Individual Companies**
```bash
python scrapers/test_mcrent_advanced.py
python scrapers/test_yescapa_advanced.py
python scrapers/test_cruise_america_advanced.py
```

### **3. Update Dashboard**
```bash
python -m streamlit run dashboard/comprehensive_calendar_display.py --server.port 8505
```

---

## 🎯 **FINAL GOAL:**

**Achieve 100% success rate with ALL 8 competitors showing real pricing data in the calendar dashboard.**

**Current:** 5/8 working (62.5%)
**Target:** 8/8 working (100%)

**This is the final push to get complete market coverage!** 🚀

---

## 📝 **DELIVERABLES:**

1. **Working scrapers** for McRent, Yescapa, Cruise America
2. **Real pricing data** for all 3 companies
3. **Updated dashboard** showing all 8 competitors
4. **Success report** with final metrics
5. **Screenshots** proving successful scraping

**Let's get this done!** 💪



