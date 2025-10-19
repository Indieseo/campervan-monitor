"""
Use Firefox to interact with booking widget on main Apollo homepage
Firefox is often better at evading Cloudflare
"""

import asyncio
import sys
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def firefox_widget_search():
    """
    Use Firefox to search via the booking widget on homepage
    """
    
    print("\n" + "="*80)
    print("APOLLO - FIREFOX + HOMEPAGE WIDGET AUTOMATION")
    print("="*80 + "\n")
    
    prices = []
    
    async with async_playwright() as p:
        print("[1/12] Launching FIREFOX (better Cloudflare evasion)...")
        
        browser = await p.firefox.launch(
            headless=False,
            slow_mo=200
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        )
        
        page = await context.new_page()
        
        # Monitor responses
        async def log_response(response):
            if 'api' in response.url and response.status == 200:
                try:
                    body = await response.text()
                    price_matches = re.findall(r'"(?:price|rate|cost)":\s*(\d+(?:\.\d{2})?)', body)
                    if price_matches:
                        print(f"       [PRICE API] {response.url[:60]}: {price_matches}")
                        for p in price_matches:
                            prices.append(float(p))
                except:
                    pass
        
        page.on('response', log_response)
        
        print("[2/12] Loading apollocamper.com (MAIN SITE)...")
        
        try:
            await page.goto('https://www.apollocamper.com/', wait_until='domcontentloaded', timeout=90000)
            print("       Page loaded")
            
            print("\n[3/12] Waiting for Cloudflare (up to 60 seconds)...")
            
            # Wait for real content
            for i in range(60):
                await asyncio.sleep(1)
                try:
                    text = await page.inner_text('body', timeout=2000)
                    if 'cloudflare' not in text.lower() and 'motorhome' in text.lower():
                        print(f"       [OK] Cloudflare cleared after {i+1} seconds!")
                        break
                except:
                    pass
                
                if i % 10 == 0 and i > 0:
                    print(f"       [{i}s] Still waiting...")
            
            await asyncio.sleep(3)
            
            await page.screenshot(path='data/screenshots/apollo_firefox_1.png', full_page=True)
            
            print("\n[4/12] Looking for booking widget on homepage...")
            
            # The homepage has an embedded booking widget - find it
            # Look for common widget selectors
            widget_selectors = [
                '#booking-widget',
                '[class*="booking"]',
                '[class*="search"]',
                '[id*="search"]',
                'iframe[src*="booking"]',
            ]
            
            widget_found = False
            for selector in widget_selectors:
                try:
                    widget = await page.query_selector(selector)
                    if widget:
                        print(f"       [FOUND] Widget: {selector}")
                        widget_found = True
                        break
                except:
                    continue
            
            print("\n[5/12] Looking for pickup location dropdown...")
            
            # On Apollo homepage, look for "Pick up from" select
            pickup_select = await page.query_selector('select, input[placeholder*="Pick"], input[placeholder*="location"]')
            
            if pickup_select:
                print("       [FOUND] Pickup selector!")
                print("       [ACTION] Clicking...")
                
                await pickup_select.click()
                await asyncio.sleep(2)
                
                # Type or select USA location
                tag = await pickup_select.evaluate('el => el.tagName')
                
                if tag == 'SELECT':
                    print("       [SELECT] Using dropdown...")
                    # Get all options
                    options = await pickup_select.query_selector_all('option')
                    for opt in options[:20]:
                        text = await opt.inner_text()
                        value = await opt.get_attribute('value')
                        print(f"          Option: {text} = {value}")
                        
                        if any(keyword in text.lower() for keyword in ['los angeles', 'usa', 'california', 'lax']):
                            print(f"       [SELECTING] {text}")
                            await pickup_select.select_option(value=value)
                            await asyncio.sleep(2)
                            break
                else:
                    print("       [INPUT] Typing...")
                    await pickup_select.fill('Los Angeles')
                    await asyncio.sleep(3)
                    
                    # Look for autocomplete
                    suggestions = await page.query_selector_all('[role="option"], .autocomplete-item, .suggestion')
                    if suggestions:
                        print(f"       Found {len(suggestions)} suggestions, clicking first...")
                        await suggestions[0].click()
                        await asyncio.sleep(2)
            
            print("\n[6/12] Looking for dropoff location...")
            
            dropoff_select = await page.query_selector('select:not([name*="pickup"]), input[placeholder*="Drop"]')
            if dropoff_select:
                print("       [FOUND] Dropoff selector!")
                # Usually "Same as pickup" is default
                print("       Using same as pickup")
            
            print("\n[7/12] Looking for date pickers...")
            
            # Look for travel dates
            date_inputs = await page.query_selector_all('input[type="text"][placeholder*="date"], input[type="date"], input[placeholder*="Date"]')
            
            if date_inputs:
                print(f"       [FOUND] {len(date_inputs)} date inputs!")
                
                pickup_date = (datetime.now() + timedelta(days=30)).strftime('%m/%d/%Y')
                dropoff_date = (datetime.now() + timedelta(days=37)).strftime('%m/%d/%Y')
                
                if len(date_inputs) >= 1:
                    print(f"       [ACTION] Filling pickup date: {pickup_date}")
                    await date_inputs[0].click()
                    await asyncio.sleep(0.5)
                    await date_inputs[0].fill(pickup_date)
                    await asyncio.sleep(1)
                
                if len(date_inputs) >= 2:
                    print(f"       [ACTION] Filling dropoff date: {dropoff_date}")
                    await date_inputs[1].click()
                    await asyncio.sleep(0.5)
                    await date_inputs[1].fill(dropoff_date)
                    await asyncio.sleep(1)
                
                await page.screenshot(path='data/screenshots/apollo_firefox_2_filled.png', full_page=True)
            
            print("\n[8/12] Looking for passenger/driver fields...")
            
            # Passengers
            passenger_select = await page.query_selector('select[name*="passenger"], input[placeholder*="Passenger"]')
            if passenger_select:
                print("       [FOUND] Passenger selector!")
                tag = await passenger_select.evaluate('el => el.tagName')
                if tag == 'SELECT':
                    await passenger_select.select_option(value='2')
                    print("       Selected: 2 passengers")
                    await asyncio.sleep(1)
            
            # License/age
            license_select = await page.query_selector('select[name*="license"], select[name*="age"], input[placeholder*="Licence"]')
            if license_select:
                print("       [FOUND] License/age selector!")
                tag = await license_select.evaluate('el => el.tagName')
                if tag == 'SELECT':
                    # Select first option
                    await license_select.select_option(index=0)
                    print("       Selected license option")
                    await asyncio.sleep(1)
            
            print("\n[9/12] Looking for SEARCH button...")
            
            # Find search button on the widget
            search_btn_selectors = [
                'button:has-text("Search")',
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Find")',
                'button:has-text("Check")',
                'button.search-button',
                '.search-btn',
            ]
            
            search_btn = None
            for selector in search_btn_selectors:
                try:
                    search_btn = await page.query_selector(selector)
                    if search_btn and await search_btn.is_visible():
                        print(f"       [FOUND] Search button: {selector}")
                        break
                except:
                    continue
            
            if search_btn:
                print("\n[10/12] CLICKING SEARCH BUTTON...")
                await search_btn.click()
                print("       Clicked! Waiting for results...")
                
                await asyncio.sleep(10)  # Wait for search results
                
                await page.screenshot(path='data/screenshots/apollo_firefox_3_results.png', full_page=True)
                
                print("\n[11/12] Checking results page...")
                
                current_url = page.url
                page_text = await page.inner_text('body')
                
                print(f"       URL: {current_url}")
                print(f"       Text length: {len(page_text)} chars")
                
                # Extract prices
                found_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', page_text)
                
                if found_prices:
                    print(f"\n       [PRICES FOUND] {len(found_prices)} mentions:")
                    for p in found_prices:
                        try:
                            val = float(p.replace(',', ''))
                            if 20 <= val <= 2000:
                                prices.append(val)
                                print(f"          ${val}")
                        except:
                            pass
                
                # Look for vehicle cards
                print("\n[12/12] Looking for vehicle listings...")
                
                vehicle_elements = await page.query_selector_all('[class*="vehicle"], [class*="result"], [class*="card"], article')
                print(f"       Found {len(vehicle_elements)} potential vehicle cards")
                
                for i, card in enumerate(vehicle_elements[:10]):
                    try:
                        card_text = await card.inner_text()
                        card_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', card_text)
                        if card_prices:
                            print(f"       Card {i}: {card_prices}")
                    except:
                        pass
            
            else:
                print("       [WARNING] No search button found")
                print("       Trying to press Enter on the form...")
                await page.keyboard.press('Enter')
                await asyncio.sleep(10)
            
            # FINAL RESULTS
            print("\n" + "="*80)
            print("FINAL RESULTS")
            print("="*80)
            
            if prices:
                unique = sorted(set(prices))
                print(f"\n>>> SUCCESS! EXTRACTED {len(unique)} REAL APOLLO PRICES!\n")
                
                for price in unique:
                    print(f"    ${price:.2f}")
                
                print(f"\n>>> STATISTICS:")
                print(f"    Lowest:  ${min(prices):.2f}")
                print(f"    Highest: ${max(prices):.2f}")
                print(f"    Average: ${sum(prices)/len(prices):.2f}")
            else:
                print("\n>>> NO AUTOMATED EXTRACTION")
                print("    Check screenshots:")
                print("      - apollo_firefox_1.png")
                print("      - apollo_firefox_2_filled.png")
                print("      - apollo_firefox_3_results.png")
            
            print("\n" + "="*80)
            print("BROWSER OPEN 60 SECONDS")
            print("="*80 + "\n")
            
            for i in range(60, 0, -1):
                print(f"{i}s...", end='\r')
                await asyncio.sleep(1)
            
            await browser.close()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(firefox_widget_search())





