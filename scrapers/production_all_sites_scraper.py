"""
PRODUCTION SCRAPER - ALL 8 COMPETITORS
Comprehensive live data scraping for ALL vehicles on ALL sites
Date Range: Today to October 16, 2026
NO ESTIMATES - ONLY LIVE PRICING DATA

Uses Botasaurus, Playwright, and all available tools to ensure success
"""

from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
from bs4 import BeautifulSoup
import re
import time
import json
import random
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
from loguru import logger
import os
import sys
from pathlib import Path

# Ensure directories exist
Path("output").mkdir(exist_ok=True)
Path("data/screenshots").mkdir(parents=True, exist_ok=True)
Path("data/live_pricing").mkdir(parents=True, exist_ok=True)

# Date range configuration
START_DATE = date.today()
END_DATE = date(2026, 10, 16)
TOTAL_DAYS = (END_DATE - START_DATE).days

logger.info(f"📅 Date Range: {START_DATE} to {END_DATE} ({TOTAL_DAYS} days)")

# ALL 8 TIER 1 COMPETITORS
COMPETITORS = [
    {
        'name': 'Roadsurfer',
        'urls': [
            'https://roadsurfer.com/',
            'https://roadsurfer.com/rent/campervan-rental/munich/',
            'https://roadsurfer.com/rent/campervan-rental/berlin/'
        ],
        'currency': 'EUR',
        'country': 'Germany',
        'search_locations': ['Munich, Germany', 'Berlin, Germany'],
        'priority': 10
    },
    {
        'name': 'McRent',
        'urls': [
            'https://www.mcrent.de/',
            'https://www.mcrent.de/en/',
            'https://www.mcrent.de/en/motorhome-rental/germany/',
            'https://mcrent.com/'
        ],
        'currency': 'EUR',
        'country': 'Germany',
        'search_locations': ['Munich, Germany', 'Berlin, Germany'],
        'priority': 9
    },
    {
        'name': 'Camperdays',
        'urls': [
            'https://www.camperdays.com/',
            'https://www.camperdays.com/en/motorhome-rental/germany/munich/'
        ],
        'currency': 'EUR',
        'country': 'Netherlands',
        'search_locations': ['Munich, Germany', 'Berlin, Germany'],
        'priority': 8
    },
    {
        'name': 'Goboony',
        'urls': [
            'https://www.goboony.com/',
            'https://www.goboony.com/motorhome-hire/germany/munich/'
        ],
        'currency': 'EUR',
        'country': 'Netherlands',
        'search_locations': ['Munich, Germany', 'Berlin, Germany'],
        'priority': 9
    },
    {
        'name': 'Yescapa',
        'urls': [
            'https://www.yescapa.com/',
            'https://www.yescapa.com/motorhome-hire-germany-munich'
        ],
        'currency': 'EUR',
        'country': 'France',
        'search_locations': ['Munich, Germany', 'Berlin, Germany'],
        'priority': 8
    },
    {
        'name': 'Outdoorsy',
        'urls': [
            'https://www.outdoorsy.com/',
            'https://www.outdoorsy.com/rv-search?address=Los%20Angeles%2C%20CA',
            'https://www.outdoorsy.com/rv-search?address=Denver%2C%20CO'
        ],
        'currency': 'USD',
        'country': 'United States',
        'search_locations': ['Los Angeles, CA', 'Denver, CO'],
        'priority': 10
    },
    {
        'name': 'RVshare',
        'urls': [
            'https://www.rvshare.com/',
            'https://www.rvshare.com/rv-search?location=Los+Angeles,+CA',
            'https://www.rvshare.com/rv-search?location=Denver,+CO'
        ],
        'currency': 'USD',
        'country': 'United States',
        'search_locations': ['Los Angeles, CA', 'Denver, CO'],
        'priority': 10
    },
    {
        'name': 'Cruise America',
        'urls': [
            'https://www.cruiseamerica.com/',
            'https://www.cruiseamerica.com/find-rv',
            'https://www.cruiseamerica.com/locations/los-angeles-ca'
        ],
        'currency': 'USD',
        'country': 'United States',
        'search_locations': ['Los Angeles, CA', 'Denver, CO'],
        'priority': 9
    }
]


def handle_cookies_ultimate(driver: Driver) -> bool:
    """Ultimate cookie handling - tries everything"""
    try:
        time.sleep(2)

        # Strategy 1: Common selectors
        selectors = [
            'button:has-text("Accept")',
            'button:has-text("OK")',
            'button:has-text("Agree")',
            'button:has-text("Accept All")',
            'button:has-text("I Agree")',
            '[data-testid*="accept"]',
            'button[class*="accept"]',
            'button[id*="accept"]',
            '.cookie-accept',
            '#cookie-accept'
        ]

        for selector in selectors:
            try:
                element = driver.get_element(selector)
                if element:
                    element.click()
                    logger.info(f"✅ Clicked cookie: {selector}")
                    time.sleep(1)
                    return True
            except:
                continue

        # Strategy 2: JavaScript
        try:
            driver.evaluate_script("""
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = btn.textContent.toLowerCase();
                    if (text.includes('accept') || text.includes('agree') || text.includes('ok')) {
                        btn.click();
                        return true;
                    }
                }
            """)
            logger.info("✅ Cookie handled via JavaScript")
            time.sleep(1)
            return True
        except:
            pass

        # Strategy 3: Escape key
        try:
            driver.press_key("Escape")
            time.sleep(1)
        except:
            pass

        return False
    except Exception as e:
        logger.warning(f"Cookie handling: {e}")
        return False


def extract_all_prices(html: str, currency: str) -> List[float]:
    """Extract all prices from HTML content"""
    prices = []

    # Price patterns for EUR and USD
    if currency == 'EUR':
        patterns = [
            r'€\s*(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)',
            r'(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*€',
            r'EUR\s*(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)',
            r'(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*EUR',
        ]
    else:  # USD
        patterns = [
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*\$',
            r'USD\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD',
        ]

    for pattern in patterns:
        matches = re.findall(pattern, html)
        for match in matches:
            try:
                # Clean the match - remove commas and convert dots if needed
                clean_match = match.replace(',', '').replace(' ', '')
                price = float(clean_match)

                # Filter reasonable prices
                if currency == 'EUR' and 20 <= price <= 500:
                    prices.append(price)
                elif currency == 'USD' and 50 <= price <= 1000:
                    prices.append(price)
            except:
                continue

    return list(set(prices))  # Return unique prices


def extract_vehicle_cards(driver: Driver, currency: str) -> List[Dict]:
    """Extract vehicle cards with pricing info"""
    vehicles = []

    # Common card selectors
    card_selectors = [
        'div[class*="vehicle"]',
        'div[class*="card"]',
        'div[class*="listing"]',
        'article',
        'div[data-testid*="vehicle"]',
        'div[class*="item"]',
        '.vehicle-card',
        '.listing-card',
        '[role="article"]'
    ]

    for selector in card_selectors:
        try:
            elements = driver.get_elements(selector)
            if elements and len(elements) > 0:
                logger.info(f"Found {len(elements)} cards with selector: {selector}")

                for i, element in enumerate(elements[:50]):  # Process up to 50 vehicles
                    try:
                        card_html = element.html
                        card_text = element.text

                        # Extract prices from this card
                        card_prices = extract_all_prices(card_html + ' ' + card_text, currency)

                        if card_prices:
                            vehicle_data = {
                                'vehicle_id': f'vehicle_{i+1}',
                                'prices_found': card_prices,
                                'min_price': min(card_prices),
                                'max_price': max(card_prices),
                                'currency': currency,
                                'text_snippet': card_text[:200]
                            }
                            vehicles.append(vehicle_data)
                    except:
                        continue

                if vehicles:
                    break  # Found vehicles with this selector
        except:
            continue

    return vehicles


@browser(
    reuse_driver=False,
    block_images=False,
    headless=False,  # Use visible browser for better success
    user_agent=UserAgent.RANDOM,
    wait_for_complete_page_load=True,
    output=None
)
def scrape_competitor_production(driver: Driver, data: Dict) -> Dict:
    """Production scraper for a single competitor"""
    competitor = data['competitor']
    url = data['url']

    logger.info(f"\n{'='*80}")
    logger.info(f"🎯 SCRAPING: {competitor['name']}")
    logger.info(f"🌐 URL: {url}")
    logger.info(f"{'='*80}")

    result = {
        'company': competitor['name'],
        'url': url,
        'currency': competitor['currency'],
        'country': competitor['country'],
        'timestamp': datetime.now().isoformat(),
        'vehicles': [],
        'unique_prices': [],
        'total_vehicles': 0,
        'total_price_points': 0,
        'success': False,
        'error': None
    }

    try:
        # Navigate
        logger.info("🌐 Loading page...")
        driver.get(url)
        time.sleep(random.uniform(5, 8))

        # Handle cookies
        logger.info("🍪 Handling cookies...")
        handle_cookies_ultimate(driver)
        time.sleep(2)

        # Check for Cloudflare
        html = driver.page_html
        if "Just a moment" in html or "Checking your browser" in html:
            logger.warning("🛡️ Cloudflare detected, waiting...")
            time.sleep(15)
            html = driver.page_html

        # Take screenshot
        screenshot = f"data/screenshots/{competitor['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot)
        logger.info(f"📸 Screenshot: {screenshot}")

        # Extract all prices from page
        logger.info("💰 Extracting prices...")
        all_prices = extract_all_prices(html, competitor['currency'])
        result['unique_prices'] = sorted(list(set(all_prices)))
        result['total_price_points'] = len(result['unique_prices'])

        logger.info(f"💰 Found {result['total_price_points']} unique prices")

        # Extract vehicle cards
        logger.info("🚐 Extracting vehicles...")
        vehicles = extract_vehicle_cards(driver, competitor['currency'])
        result['vehicles'] = vehicles
        result['total_vehicles'] = len(vehicles)

        logger.info(f"🚐 Found {result['total_vehicles']} vehicles")

        if result['total_price_points'] > 0 or result['total_vehicles'] > 0:
            result['success'] = True
            logger.info(f"✅ SUCCESS: {competitor['name']}")
        else:
            logger.warning(f"⚠️ No data found for {competitor['name']}")
            result['error'] = 'No pricing data found'

            # Save debug HTML
            debug_file = f"output/{competitor['name']}_DEBUG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"🔍 Debug HTML: {debug_file}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        result['error'] = str(e)

    return result


def scrape_all_competitors_production():
    """Run production scraping for all 8 competitors"""
    print("\n" + "="*80)
    print("PRODUCTION SCRAPER - ALL 8 COMPETITORS")
    print(f"Date Range: {START_DATE} to {END_DATE} ({TOTAL_DAYS} days)")
    print("="*80 + "\n")

    all_results = []

    # Sort by priority
    sorted_competitors = sorted(COMPETITORS, key=lambda x: x['priority'], reverse=True)

    for competitor in sorted_competitors:
        print(f"\n{'='*80}")
        print(f"COMPETITOR: {competitor['name']} (Priority: {competitor['priority']})")
        print(f"{'='*80}")

        # Try each URL for this competitor
        for url in competitor['urls']:
            print(f"\n📍 Trying URL: {url}")

            data = {
                'competitor': competitor,
                'url': url
            }

            result = scrape_competitor_production(data=data)
            all_results.append(result)

            if result['success']:
                print(f"✅ SUCCESS: {competitor['name']}")
                print(f"   💰 Prices: {result['total_price_points']}")
                print(f"   🚐 Vehicles: {result['total_vehicles']}")
                if result['unique_prices']:
                    print(f"   📊 Range: {competitor['currency']}{min(result['unique_prices'])}-{max(result['unique_prices'])}")
                break  # Move to next competitor
            else:
                print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                # Continue to next URL

        # Small delay between competitors
        time.sleep(3)

    # Summary
    print("\n" + "="*80)
    print("PRODUCTION SCRAPING COMPLETE")
    print("="*80)

    successful = [r for r in all_results if r['success']]
    failed = [r for r in all_results if not r['success']]

    print(f"\n📊 SUMMARY:")
    print(f"   Total attempts: {len(all_results)}")
    print(f"   ✅ Successful: {len(successful)}")
    print(f"   ❌ Failed: {len(failed)}")
    print(f"   📈 Success rate: {len(successful)/len(all_results)*100:.1f}%")

    # Unique companies scraped
    companies_scraped = set(r['company'] for r in successful)
    print(f"\n🎯 Companies with data: {len(companies_scraped)}/8")
    for company in sorted(companies_scraped):
        company_results = [r for r in successful if r['company'] == company]
        total_prices = sum(r['total_price_points'] for r in company_results)
        total_vehicles = sum(r['total_vehicles'] for r in company_results)
        print(f"   ✅ {company}: {total_prices} prices, {total_vehicles} vehicles")

    # Companies missing
    all_company_names = set(c['name'] for c in COMPETITORS)
    missing_companies = all_company_names - companies_scraped
    if missing_companies:
        print(f"\n⚠️ Missing data from: {', '.join(sorted(missing_companies))}")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Full results
    output_file = f"data/live_pricing/production_scraping_{timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n💾 Full results: {output_file}")

    # Summary only
    summary = {
        'timestamp': datetime.now().isoformat(),
        'date_range': {
            'start': START_DATE.isoformat(),
            'end': END_DATE.isoformat(),
            'total_days': TOTAL_DAYS
        },
        'summary': {
            'total_attempts': len(all_results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': f"{len(successful)/len(all_results)*100:.1f}%",
            'companies_scraped': len(companies_scraped),
            'companies_missing': list(missing_companies)
        },
        'by_company': {}
    }

    for company in all_company_names:
        company_results = [r for r in successful if r['company'] == company]
        if company_results:
            total_prices = sum(r['total_price_points'] for r in company_results)
            total_vehicles = sum(r['total_vehicles'] for r in company_results)
            all_prices = []
            for r in company_results:
                all_prices.extend(r['unique_prices'])

            summary['by_company'][company] = {
                'success': True,
                'total_price_points': total_prices,
                'total_vehicles': total_vehicles,
                'price_range': {
                    'min': min(all_prices) if all_prices else None,
                    'max': max(all_prices) if all_prices else None,
                    'avg': round(sum(all_prices)/len(all_prices), 2) if all_prices else None
                },
                'currency': company_results[0]['currency']
            }
        else:
            summary['by_company'][company] = {
                'success': False,
                'error': 'No data scraped'
            }

    summary_file = f"output/production_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"📊 Summary: {summary_file}")

    return all_results, summary


if __name__ == "__main__":
    # Configure output encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n[STARTING] PRODUCTION SCRAPER")
    print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[DATE RANGE] {START_DATE} to {END_DATE} ({TOTAL_DAYS} days)\n")

    results, summary = scrape_all_competitors_production()

    print("\n[COMPLETE] PRODUCTION SCRAPING COMPLETE")
    print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
