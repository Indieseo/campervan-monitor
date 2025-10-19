"""
Fix the 5 competitors that are currently failing to extract real pricing data
McRent, Camperdays, Goboony, Yescapa, Cruise America
"""

from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
from bs4 import BeautifulSoup
import re
import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
import os

# Ensure output and screenshots directories exist
os.makedirs("output", exist_ok=True)
os.makedirs("data/screenshots", exist_ok=True)

# Define search parameters
SEARCH_LOCATION_EUROPE = "Munich"
SEARCH_LOCATION_US = "Los Angeles"
SEARCH_START_DATE = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
SEARCH_END_DATE = (datetime.now() + timedelta(days=37)).strftime('%Y-%m-%d')

# Focus on the 5 failing competitors with better search URLs
FAILING_COMPETITORS = [
    {
        'name': 'McRent',
        'homepage_url': 'https://www.mcrent.de/',
        'search_url': 'https://www.mcrent.de/en/motorhome-rental/germany/munich',
        'currency': 'EUR',
        'country': 'Germany',
        'location_to_search': SEARCH_LOCATION_EUROPE,
        'price_patterns': [r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*€', r'€\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'],
    },
    {
        'name': 'Camperdays',
        'homepage_url': 'https://www.camperdays.com/',
        'search_url': 'https://www.camperdays.com/en/motorhome-rental/germany/munich',
        'currency': 'EUR',
        'country': 'Netherlands',
        'location_to_search': SEARCH_LOCATION_EUROPE,
        'price_patterns': [r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*€', r'€\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'],
    },
    {
        'name': 'Goboony',
        'homepage_url': 'https://www.goboony.com/',
        'search_url': 'https://www.goboony.com/motorhome-hire/germany/munich',
        'currency': 'EUR',
        'country': 'Netherlands',
        'location_to_search': SEARCH_LOCATION_EUROPE,
        'price_patterns': [r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*€', r'€\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'],
    },
    {
        'name': 'Yescapa',
        'homepage_url': 'https://www.yescapa.com/',
        'search_url': 'https://www.yescapa.com/motorhome-hire-germany',
        'currency': 'EUR',
        'country': 'France',
        'location_to_search': SEARCH_LOCATION_EUROPE,
        'price_patterns': [r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*€', r'€\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'],
    },
    {
        'name': 'Cruise America',
        'homepage_url': 'https://www.cruiseamerica.com/',
        'search_url': 'https://www.cruiseamerica.com/find-rv',
        'currency': 'USD',
        'country': 'United States',
        'location_to_search': SEARCH_LOCATION_US,
        'price_patterns': [r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*\$'],
    }
]


def extract_prices_advanced(text: str, currency: str, patterns: List[str]) -> List[float]:
    """Advanced price extraction with multiple patterns"""
    prices = []
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                price = float(match.replace(',', ''))
                if 20 <= price <= 2000:  # Reasonable rental price range
                    prices.append(price)
            except ValueError:
                continue
    
    return sorted(list(set(prices)))  # Remove duplicates and sort


@browser(
    reuse_driver=False,
    block_images=False,
    headless=True,
    user_agent=UserAgent.RANDOM,
    wait_for_complete_page_load=True
)
def scrape_failing_competitor(driver: Driver, data) -> Dict:
    """Scrape a failing competitor with enhanced methods"""
    config = data
    
    logger.info(f"🔧 FIXING: {config['name']}")
    logger.info(f"🌐 URL: {config['search_url']}")
    
    result = {
        'company_name': config['name'],
        'search_location': config['location_to_search'],
        'search_start_date': SEARCH_START_DATE,
        'search_end_date': SEARCH_END_DATE,
        'timestamp': datetime.now().isoformat(),
        'currency': config['currency'],
        'url': config['search_url'],
        'num_results': 0,
        'min_price': None,
        'max_price': None,
        'avg_price': None,
        'prices_found': [],
        'notes': '',
        'screenshot_path': None,
        'success': False,
        'scraping_strategy': 'enhanced_fix_attempt'
    }
    
    try:
        # Navigate to search URL
        logger.info(f"🌐 Navigating to {config['search_url']}")
        driver.get(config['search_url'])
        
        # Wait for page load and Cloudflare
        time.sleep(random.uniform(5, 8))
        
        html = driver.page_html
        title = driver.title
        
        # Check for Cloudflare
        if "Just a moment" in html or "Checking your browser" in html:
            logger.warning("🛡️ Cloudflare detected, waiting...")
            time.sleep(random.uniform(10, 15))
            html = driver.page_html
            if "Just a moment" in html or "Checking your browser" in html:
                logger.error("❌ Cloudflare not cleared")
                result['notes'] = 'Cloudflare challenge not cleared'
                return result
        
        logger.info(f"✅ Page loaded: {title}")
        
        # Take initial screenshot
        screenshot_path = f"data/screenshots/{config['name']}_FIXED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_path)
        result['screenshot_path'] = screenshot_path
        
        # Extract text content
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        logger.info(f"📄 Page text length: {len(text)} characters")
        
        # Try multiple extraction methods
        prices = []
        
        # Method 1: Direct price pattern matching
        logger.info("🔍 Method 1: Direct price pattern matching")
        prices.extend(extract_prices_advanced(text, config['currency'], config['price_patterns']))
        
        # Method 2: Look for specific price elements
        logger.info("🔍 Method 2: Price element extraction")
        price_elements = soup.find_all(['span', 'div', 'p'], string=re.compile(r'[€$]\s*\d+|\d+\s*[€$]'))
        for element in price_elements:
            element_text = element.get_text()
            element_prices = extract_prices_advanced(element_text, config['currency'], config['price_patterns'])
            prices.extend(element_prices)
        
        # Method 3: Look for data attributes
        logger.info("🔍 Method 3: Data attribute extraction")
        elements_with_data = soup.find_all(attrs={'data-price': True})
        for element in elements_with_data:
            try:
                price = float(element.get('data-price'))
                if 20 <= price <= 2000:
                    prices.append(price)
            except:
                continue
        
        # Method 4: Look for class names containing 'price'
        logger.info("🔍 Method 4: Price class extraction")
        price_classes = soup.find_all(class_=re.compile(r'price|cost|rate', re.I))
        for element in price_classes:
            element_text = element.get_text()
            element_prices = extract_prices_advanced(element_text, config['currency'], config['price_patterns'])
            prices.extend(element_prices)
        
        # Remove duplicates and filter
        prices = sorted(list(set(prices)))
        prices = [p for p in prices if 20 <= p <= 2000]  # Final filter
        
        if prices:
            result['prices_found'] = prices
            result['num_results'] = len(prices)
            result['min_price'] = min(prices)
            result['max_price'] = max(prices)
            result['avg_price'] = round(sum(prices) / len(prices), 2)
            result['success'] = True
            logger.info(f"✅ SUCCESS: Found {len(prices)} prices: {config['currency']}{result['min_price']}-{result['max_price']}/night")
        else:
            logger.warning("⚠️ No prices found with any method")
            result['notes'] = 'No prices found with enhanced extraction methods'
            
            # Debug: Save page content for analysis
            debug_file = f"output/{config['name']}_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"🔍 Debug HTML saved: {debug_file}")
    
    except Exception as e:
        logger.error(f"❌ Error scraping {config['name']}: {e}")
        result['notes'] = f"Error: {str(e)[:200]}"
    
    return result


def fix_all_failing_competitors():
    """Fix all 5 failing competitors"""
    print("="*80)
    print("FIXING FAILING COMPETITORS - ENHANCED EXTRACTION")
    print("="*80 + "\n")
    
    results = []
    
    for config in FAILING_COMPETITORS:
        print(f"\n{'='*80}")
        print(f"FIXING: {config['name']}")
        print(f"{'='*80}\n")
        
        result = scrape_failing_competitor(data=config)
        results.append(result)
        
        if result['success']:
            print(f"\n[SUCCESS] {config['name']}:")
            print(f"  Results: {result['num_results']} prices found")
            print(f"  Range: {config['currency']}{result['min_price']}-{result['max_price']}/night")
            print(f"  Average: {config['currency']}{result['avg_price']}/night")
        else:
            print(f"\n[FAILED] {config['name']}: {result['notes']}")
    
    # Summary
    print("\n" + "="*80)
    print("FIXING COMPLETE - SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r['success']]
    print(f"Fixed: {len(successful)}/{len(FAILING_COMPETITORS)} competitors")
    
    if successful:
        print("\nFixed Competitors:")
        for r in successful:
            print(f"  ✅ {r['company_name']:15} {r['num_results']} prices | {r['currency']}{r['min_price']}-{r['max_price']}/night")
    
    failed = [r for r in results if not r['success']]
    if failed:
        print("\nStill Failing:")
        for r in failed:
            print(f"  ❌ {r['company_name']:15} {r['notes']}")
    
    # Save results
    output_path = f"output/fixed_competitors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[SAVED] Results: {output_path}")
    
    return results


if __name__ == "__main__":
    fix_all_failing_competitors()



