"""
Scrape the failing competitors using the correct URLs we discovered
"""

from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
from bs4 import BeautifulSoup
import re
import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List
from loguru import logger
import os

# Ensure output and screenshots directories exist
os.makedirs("output", exist_ok=True)
os.makedirs("data/screenshots", exist_ok=True)

# Use the correct URLs we discovered
CORRECT_URLS = [
    {
        'name': 'McRent',
        'search_url': 'https://www.mcrent.de/reservierung/',  # Top Deals page
        'currency': 'EUR',
        'country': 'Germany',
        'location_to_search': 'Munich',
    },
    {
        'name': 'Camperdays',
        'search_url': 'https://www.camperdays.com/campervans-germany/munich.html',  # Munich page
        'currency': 'EUR',
        'country': 'Netherlands',
        'location_to_search': 'Munich',
    },
    {
        'name': 'Goboony',
        'search_url': 'https://www.goboony.com/motorhome-hire/germany/munich',  # Munich page
        'currency': 'EUR',
        'country': 'Netherlands',
        'location_to_search': 'Munich',
    },
    {
        'name': 'Yescapa',
        'search_url': 'https://www.yescapa.com/motorhome-hire-germany',  # Germany page
        'currency': 'EUR',
        'country': 'France',
        'location_to_search': 'Munich',
    },
    {
        'name': 'Cruise America',
        'search_url': 'https://www.cruiseamerica.com/find-rv',  # Find RV page
        'currency': 'USD',
        'country': 'United States',
        'location_to_search': 'Los Angeles',
    }
]


def extract_prices_from_text(text: str, currency: str) -> List[float]:
    """Extract prices from text using multiple patterns"""
    prices = []
    
    # Different price patterns
    patterns = [
        rf'{currency}\s*(\d+(?:,\d{{3}})*(?:\.\d{{2}})?)',
        rf'(\d+(?:,\d{{3}})*(?:\.\d{{2}})?)\s*{currency}',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per|/)\s*(?:day|night)',
        r'from\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:day|night)',
    ]
    
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
def scrape_with_correct_url(driver: Driver, data) -> Dict:
    """Scrape using the correct URL we discovered"""
    config = data
    
    logger.info(f"🎯 SCRAPING: {config['name']}")
    logger.info(f"🌐 Correct URL: {config['search_url']}")
    
    result = {
        'company_name': config['name'],
        'search_location': config['location_to_search'],
        'search_start_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'search_end_date': (datetime.now() + timedelta(days=37)).strftime('%Y-%m-%d'),
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
        'scraping_strategy': 'correct_url_approach'
    }
    
    try:
        # Navigate to the correct URL
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
        
        # Take screenshot
        screenshot_path = f"data/screenshots/{config['name']}_CORRECT_URL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_path)
        result['screenshot_path'] = screenshot_path
        
        # Extract text content
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        logger.info(f"📄 Page text length: {len(text)} characters")
        
        # Extract prices using multiple methods
        prices = extract_prices_from_text(text, config['currency'])
        
        # Also try extracting from specific elements
        price_elements = soup.find_all(['span', 'div', 'p', 'strong'], string=re.compile(r'[€$]\s*\d+|\d+\s*[€$]'))
        for element in price_elements:
            element_text = element.get_text()
            element_prices = extract_prices_from_text(element_text, config['currency'])
            prices.extend(element_prices)
        
        # Look for data attributes
        elements_with_data = soup.find_all(attrs={'data-price': True})
        for element in elements_with_data:
            try:
                price = float(element.get('data-price'))
                if 20 <= price <= 2000:
                    prices.append(price)
            except:
                continue
        
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
            logger.warning("⚠️ No prices found")
            result['notes'] = 'No prices found on correct URL page'
            
            # Save debug HTML
            debug_file = f"output/{config['name']}_correct_url_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"🔍 Debug HTML saved: {debug_file}")
    
    except Exception as e:
        logger.error(f"❌ Error scraping {config['name']}: {e}")
        result['notes'] = f"Error: {str(e)[:200]}"
    
    return result


def scrape_all_with_correct_urls():
    """Scrape all competitors using their correct URLs"""
    print("="*80)
    print("SCRAPING WITH CORRECT URLS - FINAL ATTEMPT")
    print("="*80 + "\n")
    
    results = []
    
    for config in CORRECT_URLS:
        print(f"\n{'='*80}")
        print(f"SCRAPING: {config['name']}")
        print(f"{'='*80}\n")
        
        result = scrape_with_correct_url(data=config)
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
    print("CORRECT URL SCRAPING COMPLETE - SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r['success']]
    print(f"Success: {len(successful)}/{len(CORRECT_URLS)} competitors")
    
    if successful:
        print("\nSuccessful Scraping:")
        for r in successful:
            print(f"  ✅ {r['company_name']:15} {r['num_results']} prices | {r['currency']}{r['min_price']}-{r['max_price']}/night")
    
    failed = [r for r in results if not r['success']]
    if failed:
        print("\nStill Failing:")
        for r in failed:
            print(f"  ❌ {r['company_name']:15} {r['notes']}")
    
    # Save results
    output_path = f"output/correct_url_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[SAVED] Results: {output_path}")
    
    return results


if __name__ == "__main__":
    scrape_all_with_correct_urls()



