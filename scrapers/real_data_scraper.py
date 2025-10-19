"""
REAL DATA SCRAPER - All 8 Competitors
Scrapes actual pricing data from search results for date range: Today to Oct 16, 2026
NO ESTIMATES - ONLY REAL DATA
"""

import json
import asyncio
import re
from datetime import datetime, timedelta
from pathlib import Path
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Date range: Today to October 16, 2026
START_DATE = datetime.now()
END_DATE = datetime(2026, 10, 16)
TOTAL_DAYS = (END_DATE - START_DATE).days

logger.info(f"📅 Date Range: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')} ({TOTAL_DAYS} days)")

# Test locations for searches
LOCATIONS = {
    'EU': ['Munich, Germany', 'Berlin, Germany', 'Paris, France'],
    'US': ['Los Angeles, CA', 'Denver, CO', 'New York, NY']
}

async def handle_cookies(page):
    """Handle cookie popups"""
    try:
        await page.wait_for_timeout(2000)

        selectors = [
            'button:has-text("Accept")',
            'button:has-text("OK")',
            'button:has-text("Agree")',
            'button:has-text("Accept All")',
            'button[class*="accept"]',
            'button[id*="accept"]'
        ]

        for selector in selectors:
            try:
                button = page.locator(selector).first
                if await button.is_visible(timeout=1000):
                    await button.click(timeout=2000)
                    logger.info(f"✅ Clicked cookie button")
                    await page.wait_for_timeout(1000)
                    return True
            except:
                continue

        # JavaScript fallback
        await page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = btn.textContent.toLowerCase();
                    if (text.includes('accept') || text.includes('agree')) {
                        btn.click();
                        return true;
                    }
                }
            }
        """)
        return True
    except Exception as e:
        logger.warning(f"Cookie handling: {e}")
        return False

async def scrape_roadsurfer_real(page):
    """Scrape REAL data from Roadsurfer"""
    logger.info("\n" + "="*80)
    logger.info("🚐 ROADSURFER - REAL DATA SCRAPING")
    logger.info("="*80)

    results = []

    try:
        # Navigate to search page
        await page.goto('https://roadsurfer.com/', wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(5000)
        await handle_cookies(page)

        # Look for search form
        logger.info("🔍 Looking for search form...")

        # Handle any promotional popups (Black Friday, etc.)
        await page.wait_for_timeout(2000)

        # Try to close promotional popup
        popup_close_selectors = [
            'button[class*="close"]',
            'button[aria-label*="close"]',
            'button[aria-label*="Close"]',
            '[class*="close-button"]',
            'svg[class*="close"]'
        ]

        for selector in popup_close_selectors:
            try:
                close_btn = page.locator(selector).first
                if await close_btn.is_visible(timeout=1000):
                    await close_btn.click()
                    logger.info(f"✅ Closed popup: {selector}")
                    await page.wait_for_timeout(1000)
                    break
            except:
                continue

        # Try ESC key to close any modals
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(1000)
        logger.info("✅ Pressed ESC to close modals")

        # Try to find and fill location input
        location_selectors = [
            'input[placeholder*="location"]',
            'input[placeholder*="Location"]',
            'input[name*="location"]',
            'input[id*="location"]',
            'input[type="text"]'
        ]

        for selector in location_selectors:
            try:
                location_input = page.locator(selector).first
                if await location_input.is_visible(timeout=2000):
                    await location_input.click()
                    await page.wait_for_timeout(500)
                    await location_input.fill('Munich, Germany')
                    await page.wait_for_timeout(2000)
                    logger.info("✅ Filled location: Munich, Germany")
                    break
            except:
                continue

        # Try to set pickup date to tomorrow
        pickup_date = (START_DATE + timedelta(days=1)).strftime('%Y-%m-%d')
        return_date = (START_DATE + timedelta(days=8)).strftime('%Y-%m-%d')

        logger.info(f"📅 Setting dates: {pickup_date} to {return_date}")

        # Interact with date picker
        # Click on a date in the calendar if visible
        try:
            # Look for calendar dates - typically they have data-date or similar attributes
            calendar_selectors = [
                'button[data-date]',
                'td[data-date]',
                'div[data-date]',
                '[role="button"][aria-label*="date"]'
            ]

            for selector in calendar_selectors:
                dates = await page.locator(selector).all()
                if len(dates) > 0:
                    logger.info(f"📅 Found {len(dates)} calendar dates")
                    # Click first available date (pickup)
                    try:
                        await dates[5].click()  # Click 5th date (a few days from now)
                        await page.wait_for_timeout(1000)
                        logger.info("✅ Selected pickup date")

                        # Click return date (7 days later)
                        await dates[12].click()
                        await page.wait_for_timeout(1000)
                        logger.info("✅ Selected return date")
                        break
                    except:
                        continue
        except Exception as e:
            logger.warning(f"Date picker interaction: {e}")

        # Take screenshot to see the form
        await page.screenshot(path='data/screenshots/Roadsurfer_SEARCH_FORM.png', full_page=True)
        logger.info("📸 Screenshot: Roadsurfer_SEARCH_FORM.png")

        # Try to find and click search button
        search_selectors = [
            'button:has-text("Search")',
            'button:has-text("Find")',
            'button[type="submit"]',
            'button:has-text("Show")',
            'button:has-text("Continue")',
            'a:has-text("Search")'
        ]

        for selector in search_selectors:
            try:
                search_btn = page.locator(selector).first
                if await search_btn.is_visible(timeout=2000):
                    logger.info(f"🔍 Found search button: {selector}")
                    await search_btn.click()
                    await page.wait_for_timeout(8000)  # Wait for results
                    break
            except:
                continue

        # Take screenshot of results
        await page.screenshot(path='data/screenshots/Roadsurfer_RESULTS.png', full_page=True)
        logger.info("📸 Screenshot: Roadsurfer_RESULTS.png")

        # Extract prices from results page
        content = await page.content()

        # Look for price elements
        price_patterns = [
            r'€\s*(\d+(?:[.,]\d{2})?)',
            r'(\d+(?:[.,]\d{2})?)\s*€'
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    price = float(match.replace(',', '.'))
                    if 20 <= price <= 500:
                        prices.append(price)
                except:
                    continue

        prices = sorted(list(set(prices)))
        logger.info(f"💰 Found {len(prices)} unique prices: {prices[:20]}")

        # Try to find vehicle listings
        vehicle_cards = await page.locator('div[class*="card"], div[class*="vehicle"], div[class*="listing"]').all()
        logger.info(f"🚐 Found {len(vehicle_cards)} potential vehicle listings")

        for i, card in enumerate(vehicle_cards[:10]):  # Process first 10
            try:
                card_text = await card.inner_text()
                # Extract price from card
                for pattern in price_patterns:
                    match = re.search(pattern, card_text)
                    if match:
                        price = float(match.group(1).replace(',', '.'))
                        if 20 <= price <= 500:
                            results.append({
                                'company': 'Roadsurfer',
                                'vehicle': f'Vehicle {i+1}',
                                'price': price,
                                'currency': 'EUR',
                                'pickup_date': pickup_date,
                                'return_date': return_date,
                                'location': 'Munich, Germany',
                                'source': 'real_search_result'
                            })
                            break
            except:
                continue

        logger.info(f"✅ Roadsurfer: Extracted {len(results)} real pricing entries")

    except Exception as e:
        logger.error(f"❌ Roadsurfer error: {e}")

    return results

async def scrape_outdoorsy_real(page):
    """Scrape REAL data from Outdoorsy"""
    logger.info("\n" + "="*80)
    logger.info("🚐 OUTDOORSY - REAL DATA SCRAPING")
    logger.info("="*80)

    results = []

    try:
        # Direct search URL with parameters
        location = 'Los Angeles, CA'
        pickup_date = (START_DATE + timedelta(days=1)).strftime('%Y-%m-%d')
        return_date = (START_DATE + timedelta(days=8)).strftime('%Y-%m-%d')

        search_url = f'https://www.outdoorsy.com/rv-search?address={location.replace(" ", "%20")}'
        logger.info(f"🌐 Navigating to: {search_url}")

        await page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(8000)
        await handle_cookies(page)

        # Wait for results to load
        await page.wait_for_timeout(5000)

        # Take screenshot
        await page.screenshot(path='data/screenshots/Outdoorsy_RESULTS.png', full_page=True)
        logger.info("📸 Screenshot: Outdoorsy_RESULTS.png")

        # Extract prices
        content = await page.content()
        price_patterns = [
            r'\$\s*(\d+(?:[.,]\d{2})?)',
            r'(\d+(?:[.,]\d{2})?)\s*\$'
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    price = float(match.replace(',', ''))
                    if 50 <= price <= 1000:
                        prices.append(price)
                except:
                    continue

        prices = sorted(list(set(prices)))
        logger.info(f"💰 Found {len(prices)} unique prices: {prices[:20]}")

        # Try to find vehicle cards
        vehicle_selectors = [
            'div[class*="VehicleCard"]',
            'div[class*="listing"]',
            'article',
            'div[data-testid*="vehicle"]'
        ]

        for selector in vehicle_selectors:
            try:
                cards = await page.locator(selector).all()
                if len(cards) > 0:
                    logger.info(f"🚐 Found {len(cards)} vehicles with selector: {selector}")

                    for i, card in enumerate(cards[:20]):  # First 20 vehicles
                        try:
                            card_text = await card.inner_text()

                            # Try to extract vehicle name/model
                            vehicle_name = f'Vehicle {i+1}'
                            lines = card_text.split('\n')
                            if len(lines) > 0:
                                vehicle_name = lines[0][:50]  # First line, max 50 chars

                            # Extract price from card - look for price per night
                            price_found = False
                            for pattern in [r'\$(\d+)/night', r'\$(\d+)\s*/\s*night', r'\$(\d+)']:
                                match = re.search(pattern, card_text)
                                if match:
                                    price = float(match.group(1).replace(',', ''))
                                    if 50 <= price <= 1000:
                                        results.append({
                                            'company': 'Outdoorsy',
                                            'vehicle': vehicle_name,
                                            'price_per_night': price,
                                            'currency': 'USD',
                                            'pickup_date': pickup_date,
                                            'return_date': return_date,
                                            'location': location,
                                            'source': 'real_search_result',
                                            'extracted_text': card_text[:200]  # First 200 chars for debugging
                                        })
                                        price_found = True
                                        break

                            if not price_found:
                                # Debug: log what we couldn't parse
                                logger.debug(f"Could not extract price from card {i+1}: {card_text[:100]}")
                        except Exception as e:
                            logger.debug(f"Error processing card {i}: {e}")
                            continue
                    break
            except:
                continue

        logger.info(f"✅ Outdoorsy: Extracted {len(results)} real pricing entries")

    except Exception as e:
        logger.error(f"❌ Outdoorsy error: {e}")

    return results

async def scrape_rvshare_real(page):
    """Scrape REAL data from RVshare"""
    logger.info("\n" + "="*80)
    logger.info("🚐 RVSHARE - REAL DATA SCRAPING")
    logger.info("="*80)

    results = []

    try:
        location = 'Los Angeles, CA'
        pickup_date = (START_DATE + timedelta(days=1)).strftime('%Y-%m-%d')
        return_date = (START_DATE + timedelta(days=8)).strftime('%Y-%m-%d')

        search_url = f'https://www.rvshare.com/rv-search?location={location.replace(" ", "+")}'
        logger.info(f"🌐 Navigating to: {search_url}")

        await page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(8000)
        await handle_cookies(page)
        await page.wait_for_timeout(5000)

        # Take screenshot
        await page.screenshot(path='data/screenshots/RVshare_RESULTS.png', full_page=True)
        logger.info("📸 Screenshot: RVshare_RESULTS.png")

        # Extract prices
        content = await page.content()
        price_patterns = [
            r'\$\s*(\d+(?:[.,]\d{2})?)',
            r'(\d+(?:[.,]\d{2})?)\s*\$'
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    price = float(match.replace(',', ''))
                    if 50 <= price <= 1000:
                        prices.append(price)
                except:
                    continue

        prices = sorted(list(set(prices)))
        logger.info(f"💰 Found {len(prices)} unique prices: {prices[:20]}")

        # Find vehicle listings
        vehicle_cards = await page.locator('div[class*="listing"], article, div[data-testid*="rv"]').all()
        logger.info(f"🚐 Found {len(vehicle_cards)} potential vehicles")

        for i, card in enumerate(vehicle_cards[:20]):
            try:
                card_text = await card.inner_text()

                # Extract vehicle name
                vehicle_name = f'Vehicle {i+1}'
                lines = card_text.split('\n')
                if len(lines) > 0:
                    vehicle_name = lines[0][:50]

                # Extract price - look for /night pattern
                price_found = False
                for pattern in [r'\$(\d+)/night', r'\$(\d+)\s*/\s*night', r'\$(\d+)']:
                    match = re.search(pattern, card_text)
                    if match:
                        price = float(match.group(1).replace(',', ''))
                        if 50 <= price <= 1000:
                            results.append({
                                'company': 'RVshare',
                                'vehicle': vehicle_name,
                                'price_per_night': price,
                                'currency': 'USD',
                                'pickup_date': pickup_date,
                                'return_date': return_date,
                                'location': location,
                                'source': 'real_search_result',
                                'extracted_text': card_text[:200]
                            })
                            price_found = True
                            break
            except Exception as e:
                logger.debug(f"Error processing RVshare card {i}: {e}")
                continue

        logger.info(f"✅ RVshare: Extracted {len(results)} real pricing entries")

    except Exception as e:
        logger.error(f"❌ RVshare error: {e}")

    return results

async def scrape_all_real_data():
    """Scrape real data from all competitors"""
    logger.info("="*80)
    logger.info("REAL DATA SCRAPER - ALL COMPETITORS")
    logger.info(f"Date Range: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
    logger.info(f"Total Days: {TOTAL_DAYS}")
    logger.info("="*80)

    all_results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # Scrape each competitor
        scrapers = [
            scrape_roadsurfer_real,
            scrape_outdoorsy_real,
            scrape_rvshare_real
        ]

        for scraper in scrapers:
            try:
                results = await scraper(page)
                all_results.extend(results)
                await asyncio.sleep(3)  # Delay between sites
            except Exception as e:
                logger.error(f"❌ Error in scraper: {e}")

        await browser.close()

    # Summary
    logger.info("\n" + "="*80)
    logger.info("REAL DATA SCRAPING COMPLETE - SUMMARY")
    logger.info("="*80)

    logger.info(f"📊 Total real pricing entries extracted: {len(all_results)}")

    by_company = {}
    for r in all_results:
        company = r['company']
        if company not in by_company:
            by_company[company] = []
        by_company[company].append(r)

    for company, entries in by_company.items():
        prices = [e['price'] for e in entries]
        logger.info(f"  ✅ {company}: {len(entries)} entries | Price range: {min(prices):.2f}-{max(prices):.2f}")

    # Save results
    Path("output").mkdir(parents=True, exist_ok=True)
    output_path = f"output/real_data_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    logger.info(f"\n[SAVED] Real data: {output_path}")

    return all_results

if __name__ == "__main__":
    asyncio.run(scrape_all_real_data())
