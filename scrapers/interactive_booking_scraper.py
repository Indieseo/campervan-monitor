"""
Interactive Booking Form Scraper - Roadsurfer & McRent
Uses Playwright to interact with booking search forms and extract live pricing
"""

import asyncio
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# Ensure directories exist
Path("output").mkdir(exist_ok=True)
Path("data/screenshots").mkdir(parents=True, exist_ok=True)
Path("data/live_pricing").mkdir(parents=True, exist_ok=True)

# Date range
START_DATE = datetime.now()
PICKUP_DATE = START_DATE + timedelta(days=30)
RETURN_DATE = PICKUP_DATE + timedelta(days=7)

logger.info(f"Pickup: {PICKUP_DATE.strftime('%Y-%m-%d')}, Return: {RETURN_DATE.strftime('%Y-%m-%d')}")


async def handle_cookies(page):
    """Handle cookie popups"""
    try:
        await asyncio.sleep(2)

        # Try common cookie selectors
        selectors = [
            'button:has-text("Accept")',
            'button:has-text("OK")',
            'button:has-text("Agree")',
            'button:has-text("Accept All")',
            'button:has-text("I Agree")',
            'button[class*="accept"]',
            'button[id*="accept"]',
        ]

        for selector in selectors:
            try:
                button = page.locator(selector).first
                if await button.is_visible(timeout=2000):
                    await button.click(timeout=3000)
                    logger.info(f"Clicked cookie button: {selector}")
                    await asyncio.sleep(1)
                    return True
            except:
                continue

        # JavaScript fallback
        try:
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
            logger.info("Cookie handled via JavaScript")
            await asyncio.sleep(1)
            return True
        except:
            pass

        return False
    except Exception as e:
        logger.warning(f"Cookie handling: {e}")
        return False


async def extract_prices_from_page(page, currency='EUR'):
    """Extract all prices from current page"""
    try:
        content = await page.content()

        # Price patterns
        if currency == 'EUR':
            patterns = [
                r'€\s*(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)',
                r'(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*€',
                r'EUR\s*(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)',
            ]
        else:
            patterns = [
                r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*\$',
                r'USD\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            ]

        prices = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    clean_price = match.replace(',', '').replace(' ', '')
                    price = float(clean_price)

                    if currency == 'EUR' and 20 <= price <= 500:
                        prices.append(price)
                    elif currency == 'USD' and 50 <= price <= 1000:
                        prices.append(price)
                except:
                    continue

        return sorted(list(set(prices)))
    except Exception as e:
        logger.error(f"Price extraction error: {e}")
        return []


async def scrape_roadsurfer():
    """Scrape Roadsurfer using booking form interaction"""
    logger.info("\n" + "="*80)
    logger.info("ROADSURFER - INTERACTIVE BOOKING SCRAPER")
    logger.info("="*80)

    result = {
        'company': 'Roadsurfer',
        'timestamp': datetime.now().isoformat(),
        'currency': 'EUR',
        'prices': [],
        'success': False,
        'error': None
    }

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            # Navigate
            logger.info("Loading Roadsurfer homepage...")
            await page.goto('https://roadsurfer.com/', wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(5)

            # Handle cookies
            await handle_cookies(page)
            await asyncio.sleep(2)

            # Take screenshot of form
            await page.screenshot(path='data/screenshots/Roadsurfer_FORM.png', full_page=True)
            logger.info("Screenshot: Roadsurfer_FORM.png")

            # Find and fill location input
            logger.info("Looking for location input...")
            location_selectors = [
                'input[placeholder*="location" i]',
                'input[placeholder*="where" i]',
                'input[name*="location" i]',
                'input[type="text"]'
            ]

            location_filled = False
            for selector in location_selectors:
                try:
                    input_field = page.locator(selector).first
                    if await input_field.is_visible(timeout=2000):
                        await input_field.click()
                        await asyncio.sleep(1)
                        await input_field.fill('Munich')
                        await asyncio.sleep(2)

                        # Try to select from dropdown if it appears
                        try:
                            # Look for dropdown option
                            await page.locator('text=/Munich/i').first.click(timeout=3000)
                            logger.info("Selected Munich from dropdown")
                        except:
                            # Just press Enter if no dropdown
                            await input_field.press('Enter')

                        logger.info(f"Filled location with selector: {selector}")
                        location_filled = True
                        await asyncio.sleep(2)
                        break
                except Exception as e:
                    logger.debug(f"Location selector {selector} failed: {e}")
                    continue

            if not location_filled:
                logger.warning("Could not fill location field")

            # Find and interact with date picker
            logger.info("Looking for date picker...")
            date_selectors = [
                'input[placeholder*="date" i]',
                'input[type="date"]',
                'button:has-text("Date")',
                'div[class*="date"]',
                'input[name*="pickup" i]',
                'input[name*="start" i]'
            ]

            date_clicked = False
            for selector in date_selectors:
                try:
                    date_elem = page.locator(selector).first
                    if await date_elem.is_visible(timeout=2000):
                        await date_elem.click()
                        logger.info(f"Clicked date picker: {selector}")
                        date_clicked = True
                        await asyncio.sleep(3)
                        break
                except:
                    continue

            if date_clicked:
                # Try to select dates from calendar
                try:
                    # Look for available dates (typically 30 days from now)
                    target_day = PICKUP_DATE.day

                    # Try to find the date button
                    date_buttons = await page.locator(f'button:has-text("{target_day}")').all()
                    if len(date_buttons) > 0:
                        # Click first matching date (pickup)
                        await date_buttons[0].click()
                        logger.info(f"Selected pickup date: day {target_day}")
                        await asyncio.sleep(2)

                        # Select return date (7 days later)
                        return_day = RETURN_DATE.day
                        return_buttons = await page.locator(f'button:has-text("{return_day}")').all()
                        if len(return_buttons) > 0:
                            await return_buttons[0].click()
                            logger.info(f"Selected return date: day {return_day}")
                            await asyncio.sleep(2)
                except Exception as e:
                    logger.warning(f"Date selection: {e}")

            # Find and click search button
            logger.info("Looking for search button...")
            search_selectors = [
                'button:has-text("Search")',
                'button:has-text("Find")',
                'button[type="submit"]',
                'button:has-text("Show")',
                'button:has-text("Continue")',
                'a:has-text("Search")',
                'button[class*="search" i]'
            ]

            for selector in search_selectors:
                try:
                    search_btn = page.locator(selector).first
                    if await search_btn.is_visible(timeout=2000):
                        logger.info(f"Clicking search button: {selector}")
                        await search_btn.click()
                        await asyncio.sleep(10)  # Wait for results to load
                        break
                except:
                    continue

            # Take screenshot of results
            await page.screenshot(path='data/screenshots/Roadsurfer_RESULTS.png', full_page=True)
            logger.info("Screenshot: Roadsurfer_RESULTS.png")

            # Extract prices
            logger.info("Extracting prices...")
            prices = await extract_prices_from_page(page, 'EUR')

            if prices:
                result['prices'] = prices
                result['success'] = True
                logger.info(f"SUCCESS: Found {len(prices)} prices: {prices}")
            else:
                result['error'] = 'No prices found after form submission'
                logger.warning("No prices found")

            await browser.close()

        except Exception as e:
            logger.error(f"Roadsurfer error: {e}")
            result['error'] = str(e)

    return result


async def scrape_mcrent():
    """Scrape McRent using booking form interaction"""
    logger.info("\n" + "="*80)
    logger.info("MCRENT - INTERACTIVE BOOKING SCRAPER")
    logger.info("="*80)

    result = {
        'company': 'McRent',
        'timestamp': datetime.now().isoformat(),
        'currency': 'EUR',
        'prices': [],
        'success': False,
        'error': None
    }

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            # Navigate
            logger.info("Loading McRent homepage...")
            await page.goto('https://www.mcrent.de/en/', wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(5)

            # Handle cookies
            await handle_cookies(page)
            await asyncio.sleep(2)

            # Take screenshot of form
            await page.screenshot(path='data/screenshots/McRent_FORM.png', full_page=True)
            logger.info("Screenshot: McRent_FORM.png")

            # Find and fill location/station input
            logger.info("Looking for location input...")
            location_selectors = [
                'input[placeholder*="station" i]',
                'input[placeholder*="location" i]',
                'input[placeholder*="pick" i]',
                'select[name*="station" i]',
                'input[type="text"]'
            ]

            location_filled = False
            for selector in location_selectors:
                try:
                    # Check if it's a select element
                    if 'select' in selector:
                        select_elem = page.locator(selector).first
                        if await select_elem.is_visible(timeout=2000):
                            # Select Munich or first available option
                            await select_elem.select_option(index=1)
                            logger.info(f"Selected option from: {selector}")
                            location_filled = True
                            await asyncio.sleep(2)
                            break
                    else:
                        input_field = page.locator(selector).first
                        if await input_field.is_visible(timeout=2000):
                            await input_field.click()
                            await asyncio.sleep(1)
                            await input_field.fill('Munich')
                            await asyncio.sleep(2)

                            # Try to select from dropdown
                            try:
                                await page.locator('text=/Munich/i').first.click(timeout=3000)
                                logger.info("Selected Munich from dropdown")
                            except:
                                await input_field.press('Enter')

                            logger.info(f"Filled location: {selector}")
                            location_filled = True
                            await asyncio.sleep(2)
                            break
                except:
                    continue

            if not location_filled:
                logger.warning("Could not fill location field")

            # Find and interact with date picker
            logger.info("Looking for date picker...")
            date_selectors = [
                'input[placeholder*="date" i]',
                'input[type="date"]',
                'input[name*="pickup" i]',
                'input[name*="start" i]',
                'input[name*="from" i]'
            ]

            for selector in date_selectors:
                try:
                    date_input = page.locator(selector).first
                    if await date_input.is_visible(timeout=2000):
                        # Try to fill date directly
                        pickup_str = PICKUP_DATE.strftime('%Y-%m-%d')
                        await date_input.fill(pickup_str)
                        logger.info(f"Filled pickup date: {pickup_str}")
                        await asyncio.sleep(2)

                        # Find return date input
                        return_input = page.locator('input[name*="return" i], input[name*="to" i]').first
                        if await return_input.is_visible(timeout=2000):
                            return_str = RETURN_DATE.strftime('%Y-%m-%d')
                            await return_input.fill(return_str)
                            logger.info(f"Filled return date: {return_str}")
                            await asyncio.sleep(2)
                        break
                except:
                    continue

            # Find and click search button
            logger.info("Looking for search button...")
            search_selectors = [
                'button:has-text("Search")',
                'button:has-text("Find")',
                'button[type="submit"]',
                'button:has-text("Request")',
                'input[type="submit"]',
                'button[class*="search" i]',
                'button[class*="submit" i]'
            ]

            for selector in search_selectors:
                try:
                    search_btn = page.locator(selector).first
                    if await search_btn.is_visible(timeout=2000):
                        logger.info(f"Clicking search button: {selector}")
                        await search_btn.click()
                        await asyncio.sleep(10)  # Wait for results
                        break
                except:
                    continue

            # Take screenshot of results
            await page.screenshot(path='data/screenshots/McRent_RESULTS.png', full_page=True)
            logger.info("Screenshot: McRent_RESULTS.png")

            # Extract prices
            logger.info("Extracting prices...")
            prices = await extract_prices_from_page(page, 'EUR')

            if prices:
                result['prices'] = prices
                result['success'] = True
                logger.info(f"SUCCESS: Found {len(prices)} prices: {prices}")
            else:
                result['error'] = 'No prices found after form submission'
                logger.warning("No prices found")

            await browser.close()

        except Exception as e:
            logger.error(f"McRent error: {e}")
            result['error'] = str(e)

    return result


async def main():
    """Run interactive scrapers for both sites"""
    logger.info("\n" + "="*80)
    logger.info("INTERACTIVE BOOKING SCRAPER - ROADSURFER & MCRENT")
    logger.info("="*80)

    results = []

    # Scrape Roadsurfer
    roadsurfer_result = await scrape_roadsurfer()
    results.append(roadsurfer_result)

    # Small delay between sites
    await asyncio.sleep(5)

    # Scrape McRent
    mcrent_result = await scrape_mcrent()
    results.append(mcrent_result)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("INTERACTIVE SCRAPING COMPLETE")
    logger.info("="*80)

    for r in results:
        status = "SUCCESS" if r['success'] else "FAILED"
        logger.info(f"{status}: {r['company']} - {len(r['prices'])} prices")
        if r['prices']:
            logger.info(f"  Prices: {r['currency']}{min(r['prices'])}-{max(r['prices'])}")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"data/live_pricing/interactive_scraping_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"\nSaved: {output_file}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
