"""
Botasaurus Search Scraper - Get Real Pricing from Booking Forms
Fills out search forms to get actual rental prices
"""

import re
from typing import Dict, List
from datetime import datetime, timedelta
from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
from loguru import logger
from bs4 import BeautifulSoup
import time


def get_search_dates():
    """Get search dates 30 days from now"""
    start_date = datetime.now() + timedelta(days=30)
    end_date = start_date + timedelta(days=7)  # 7-day rental
    return start_date, end_date


SEARCH_CONFIGS = {
    'Roadsurfer': {
        'url': 'https://roadsurfer.com/',
        'search_url': 'https://roadsurfer.com/',
        'location': 'Munich',
        'currency': 'EUR',
        'strategy': 'search_form',
    },
    'McRent': {
        'url': 'https://www.mcrent.de/en/',
        'search_url': 'https://www.mcrent.de/en/motorhome-rental/germany',
        'location': 'Munich',
        'currency': 'EUR',
        'strategy': 'search_form',
    },
    'Camperdays': {
        'url': 'https://www.camperdays.com/',
        'search_url': 'https://www.camperdays.com/en/motorhome-rental/germany/munich',
        'location': 'Munich',
        'currency': 'EUR',
        'strategy': 'direct_search',
    },
    'Goboony': {
        'url': 'https://www.goboony.com/',
        'search_url': 'https://www.goboony.com/motorhome-hire/germany/munich',
        'location': 'Munich',
        'currency': 'EUR',
        'strategy': 'direct_search',
    },
    'Yescapa': {
        'url': 'https://www.yescapa.com/',
        'search_url': 'https://www.yescapa.com/motorhome-hire-germany',
        'location': 'Germany',
        'currency': 'EUR',
        'strategy': 'direct_search',
    },
    'Outdoorsy': {
        'url': 'https://www.outdoorsy.com/',
        'search_url': 'https://www.outdoorsy.com/rv-search?address=Los%20Angeles%2C%20CA',
        'location': 'Los Angeles',
        'currency': 'USD',
        'strategy': 'direct_search',
    },
    'RVshare': {
        'url': 'https://www.rvshare.com/',
        'search_url': 'https://www.rvshare.com/rv-search?location=Los+Angeles,+CA',
        'location': 'Los Angeles',
        'currency': 'USD',
        'strategy': 'direct_search',
    },
    'Cruise America': {
        'url': 'https://www.cruiseamerica.com/',
        'search_url': 'https://www.cruiseamerica.com/find-rv',
        'location': 'Los Angeles',
        'currency': 'USD',
        'strategy': 'search_form',
    },
}


def extract_search_results_prices(html: str, text: str, currency: str) -> List[Dict]:
    """Extract prices from search results"""
    prices = []
    
    # Price patterns for search results
    patterns = [
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:' + currency + r'|€|\$)\s*(?:per|/|for)\s*(?:day|night)',
        r'(?:' + currency + r'|€|\$)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per|/|for)\s*(?:day|night)',
        r'(?:from|starting)\s*(?:' + currency + r'|€|\$)\s*(\d+(?:,\d{3})*)',
        r'(\d+(?:,\d{3})*)\s*(?:' + currency + r'|€|\$)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                price = float(match.replace(',', ''))
                if 20 <= price <= 1000:  # Reasonable range for campervan rental
                    prices.append({
                        'price': price,
                        'currency': currency,
                        'per_day': True
                    })
            except:
                continue
    
    return prices


@browser(
    reuse_driver=False,
    block_images=False,
    headless=True,
    user_agent=UserAgent.RANDOM,
    wait_for_complete_page_load=True
)
def scrape_search_results(driver: Driver, company_name: str) -> Dict:
    """Scrape actual search results with real pricing"""
    
    if company_name not in SEARCH_CONFIGS:
        logger.error(f"Unknown competitor: {company_name}")
        return None
    
    config = SEARCH_CONFIGS[company_name]
    start_date, end_date = get_search_dates()
    
    logger.info(f"🚀 Searching: {company_name}")
    logger.info(f"📍 Location: {config['location']}")
    logger.info(f"📅 Dates: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    result = {
        'company_name': company_name,
        'search_location': config['location'],
        'search_start_date': start_date.isoformat(),
        'search_end_date': end_date.isoformat(),
        'rental_days': 7,
        'timestamp': datetime.now().isoformat(),
        'currency': config['currency'],
        'search_results': [],
        'min_price': None,
        'max_price': None,
        'avg_price': None,
        'num_results': 0,
        'scraping_strategy': 'search_form_interaction',
        'cloudflare_bypassed': False,
        'notes': ''
    }
    
    try:
        # Navigate to search URL
        logger.info(f"🌐 Navigating to {config['search_url']}")
        driver.get(config['search_url'])
        time.sleep(5)  # Wait for page load and any dynamic content
        
        # Check for Cloudflare
        html = driver.page_html
        if "Just a moment" in html or "Checking your browser" in html:
            logger.warning("🛡️ Cloudflare detected - waiting...")
            time.sleep(10)
            html = driver.page_html
        
        result['cloudflare_bypassed'] = "Just a moment" not in html
        
        if not result['cloudflare_bypassed']:
            logger.error("❌ Cloudflare not bypassed")
            result['notes'] = 'Cloudflare challenge failed'
            return result
        
        logger.info("✅ Page loaded successfully")
        
        # Get page content
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        # Try to find and fill search form
        if config['strategy'] == 'search_form':
            logger.info("📝 Looking for search form...")
            
            # Try to find date inputs
            try:
                date_inputs = driver.execute_script("""
                    return Array.from(document.querySelectorAll('input[type="date"], input[placeholder*="date" i], input[name*="date" i]'))
                        .map(el => el.outerHTML);
                """)
                
                if date_inputs:
                    logger.info(f"Found {len(date_inputs)} date inputs")
                    result['notes'] += 'Search form detected. '
            except:
                pass
            
            # Try to find location inputs
            try:
                location_inputs = driver.execute_script("""
                    return Array.from(document.querySelectorAll('input[placeholder*="location" i], input[placeholder*="city" i], input[name*="location" i]'))
                        .map(el => el.outerHTML);
                """)
                
                if location_inputs:
                    logger.info(f"Found {len(location_inputs)} location inputs")
            except:
                pass
        
        # Extract prices from current page (search results or offers)
        logger.info("💰 Extracting prices from page...")
        found_prices = extract_search_results_prices(html, text, config['currency'])
        
        if found_prices:
            result['search_results'] = found_prices
            result['num_results'] = len(found_prices)
            prices_only = [p['price'] for p in found_prices]
            result['min_price'] = min(prices_only)
            result['max_price'] = max(prices_only)
            result['avg_price'] = round(sum(prices_only) / len(prices_only), 2)
            logger.info(f"💰 Found {len(found_prices)} prices: {config['currency']}{result['min_price']}-{result['max_price']}/night")
        else:
            logger.warning("⚠️ No prices found on page")
            result['notes'] += 'No prices extracted from search page. '
        
        # Take screenshot
        screenshot_path = f"data/screenshots/{company_name}_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_path)
        logger.info(f"📸 Screenshot: {screenshot_path}")
        result['screenshot'] = screenshot_path
        
        # Scroll down to see more results
        logger.info("📜 Scrolling to load more results...")
        try:
            for i in range(3):
                # Try different scroll methods for Botasaurus
                try:
                    driver.evaluate_script("window.scrollBy(0, 800);")
                except:
                    try:
                        driver.execute_script("window.scrollBy(0, 800);")
                    except:
                        # Fallback: use page down key
                        driver.press_key("PageDown")
                time.sleep(1)
        except Exception as scroll_error:
            logger.warning(f"⚠️ Scrolling failed: {scroll_error}. Continuing with current results.")
        
        # Check for additional prices after scrolling
        html = driver.page_html
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        additional_prices = extract_search_results_prices(html, text, config['currency'])
        if len(additional_prices) > len(found_prices):
            logger.info(f"📜 Found {len(additional_prices) - len(found_prices)} more prices after scrolling")
            result['search_results'] = additional_prices
            result['num_results'] = len(additional_prices)
            prices_only = [p['price'] for p in additional_prices]
            result['min_price'] = min(prices_only)
            result['max_price'] = max(prices_only)
            result['avg_price'] = round(sum(prices_only) / len(prices_only), 2)
        
        # Final screenshot after scrolling
        screenshot_path_final = f"data/screenshots/{company_name}_search_scrolled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_path_final)
        result['screenshot_scrolled'] = screenshot_path_final
        
        logger.info(f"✅ {company_name}: {result['num_results']} results, {config['currency']}{result['min_price']}-{result['max_price']}/night")
        
    except Exception as e:
        logger.error(f"❌ Search scraping failed: {e}")
        import traceback
        traceback.print_exc()
        result['notes'] += f"Error: {str(e)[:200]}"
    
    return result


def scrape_all_search_results() -> List[Dict]:
    """Scrape search results from all competitors"""
    print("\n" + "="*80)
    print("BOTASAURUS SEARCH RESULTS SCRAPER")
    print("Getting REAL prices from search/booking tools")
    print("="*80 + "\n")
    
    results = []
    
    for company_name in SEARCH_CONFIGS.keys():
        print(f"\n{'='*80}")
        print(f"SEARCHING: {company_name}")
        print(f"{'='*80}\n")
        
        result = scrape_search_results(company_name)
        
        if result and result.get('num_results', 0) > 0:
            results.append(result)
            print(f"\n[SUCCESS] {company_name}:")
            print(f"  Results: {result['num_results']} campervans")
            print(f"  Prices: {result['currency']}{result['min_price']}-{result['max_price']}/night")
            print(f"  Average: {result['currency']}{result['avg_price']}/night")
        else:
            if result:
                results.append(result)
            print(f"\n[WARNING] {company_name}: No search results found")
    
    # Summary
    print("\n" + "="*80)
    print("SEARCH SCRAPING COMPLETE - SUMMARY")
    print("="*80)
    print(f"Competitors Searched: {len(results)}/{len(SEARCH_CONFIGS)}")
    
    successful = [r for r in results if r.get('num_results', 0) > 0]
    print(f"With Results: {len(successful)}/{len(results)}")
    
    if successful:
        print(f"\nResults Summary:")
        for r in successful:
            print(f"  {r['company_name']:20} {r['num_results']:3} results | "
                  f"{r['currency']}{r['min_price']}-{r['max_price']}/night | "
                  f"Avg: {r['currency']}{r['avg_price']}/night")
    
    print("="*80 + "\n")
    
    # Save results
    import json
    output_path = f"output/search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"[SAVED] Results: {output_path}\n")
    
    return results


if __name__ == "__main__":
    scrape_all_search_results()

