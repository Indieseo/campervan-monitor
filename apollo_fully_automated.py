"""
FULLY AUTOMATED Apollo booking search with clicking, typing, and form submission
No manual intervention required
"""

import asyncio
import sys
import re
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, TimeoutError

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def fully_automated_search():
    """
    Fully automated: click, type, search, extract prices
    """
    
    print("\n" + "="*80)
    print("APOLLO - FULLY AUTOMATED SEARCH (CLICKING + TYPING)")
    print("="*80 + "\n")
    
    prices = []
    
    async with async_playwright() as p:
        print("[1/15] Launching browser...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=300,  # Slow for visibility
            args=['--start-maximized', '--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        # Monitor API responses for prices
        async def handle_response(response):
            url = response.url
            if 'api' in url and response.status == 200:
                try:
                    if 'json' in response.headers.get('content-type', ''):
                        body = await response.text()
                        # Look for prices
                        found_prices = re.findall(r'"(?:price|rate|cost|total|daily)":\s*(\d+(?:\.\d{2})?)', body)
                        if found_prices:
                            print(f"       [API PRICES] {url[:50]}: {found_prices[:5]}")
                            for p in found_prices:
                                try:
                                    val = float(p)
                                    if 20 <= val <= 2000:
                                        prices.append(val)
                                except:
                                    pass
                except:
                    pass
        
        page.on('response', handle_response)
        
        print("[2/15] Loading booking.apollocamper.com...")
        
        try:
            await page.goto('https://booking.apollocamper.com/', timeout=60000)
            print("       Loaded!")
            
            print("\n[3/15] Waiting 10 seconds for React to fully initialize...")
            await asyncio.sleep(10)
            
            await page.screenshot(path='data/screenshots/apollo_auto_1_initial.png', full_page=True)
            
            print("\n[4/15] Looking for travel button...")
            
            # Try multiple selectors
            selectors = [
                'button:has-text("Where would you like to travel")',
                'button:has-text("travel")',
                '[class*="Button"]',
                'button[class*="start"]',
            ]
            
            travel_btn = None
            for selector in selectors:
                try:
                    travel_btn = await page.wait_for_selector(selector, timeout=5000)
                    if travel_btn:
                        print(f"       Found with: {selector}")
                        break
                except:
                    continue
            
            if not travel_btn:
                print("       [ERROR] Could not find travel button!")
                print("       Trying to find ANY visible button...")
                all_buttons = await page.query_selector_all('button')
                for i, btn in enumerate(all_buttons):
                    is_vis = await btn.is_visible()
                    if is_vis:
                        text = await btn.inner_text()
                        print(f"       Button {i}: '{text}'")
                        if 'travel' in text.lower():
                            travel_btn = btn
                            break
            
            if travel_btn:
                print("\n[5/15] CLICKING travel button...")
                await travel_btn.click()
                print("       Clicked!")
                
                # Wait for modal/form with multiple strategies
                print("\n[6/15] Waiting for form to appear (trying 30 seconds)...")
                
                form_appeared = False
                for i in range(30):
                    await asyncio.sleep(1)
                    
                    # Check for new inputs
                    inputs = await page.query_selector_all('input:visible')
                    selects = await page.query_selector_all('select:visible')
                    
                    if len(inputs) > 0 or len(selects) > 0:
                        print(f"       [OK] Form appeared! ({len(inputs)} inputs, {len(selects)} selects)")
                        form_appeared = True
                        break
                    
                    if i % 5 == 0:
                        print(f"       [{i}s] Still waiting...")
                
                await page.screenshot(path='data/screenshots/apollo_auto_2_clicked.png', full_page=True)
                
                if not form_appeared:
                    print("\n[7/15] Form didn't appear, trying keyboard navigation...")
                    # Press Tab to navigate
                    await page.keyboard.press('Tab')
                    await asyncio.sleep(1)
                    await page.keyboard.press('Tab')
                    await asyncio.sleep(1)
                
                print("\n[8/15] Looking for location/country input...")
                
                # Try to find any visible input to type in
                all_inputs = await page.query_selector_all('input')
                
                location_input = None
                for inp in all_inputs:
                    try:
                        is_visible = await inp.is_visible()
                        if is_visible:
                            placeholder = await inp.get_attribute('placeholder')
                            aria_label = await inp.get_attribute('aria-label')
                            name = await inp.get_attribute('name')
                            
                            print(f"       Visible input: placeholder={placeholder}, name={name}, aria={aria_label}")
                            
                            # This looks like location input
                            if placeholder or name or aria_label:
                                if any(keyword in str(placeholder).lower() + str(name).lower() + str(aria_label).lower() 
                                      for keyword in ['location', 'country', 'where', 'search', 'destination']):
                                    location_input = inp
                                    print(f"       [FOUND] Location input!")
                                    break
                    except:
                        continue
                
                if not location_input:
                    # Just use the first visible input
                    for inp in all_inputs:
                        try:
                            if await inp.is_visible():
                                location_input = inp
                                print("       [USING] First visible input")
                                break
                        except:
                            continue
                
                if location_input:
                    print("\n[9/15] TYPING location...")
                    
                    await location_input.click()
                    await asyncio.sleep(1)
                    
                    # Type USA
                    await location_input.fill('USA')
                    print("       Typed: USA")
                    await asyncio.sleep(3)
                    
                    await page.screenshot(path='data/screenshots/apollo_auto_3_typed.png', full_page=True)
                    
                    print("\n[10/15] Looking for dropdown/autocomplete options...")
                    
                    # Look for dropdown options
                    option_selectors = [
                        '[role="option"]',
                        '.option',
                        '[class*="option"]',
                        '[class*="suggestion"]',
                        '[class*="dropdown"]',
                        'li',
                    ]
                    
                    option_clicked = False
                    for selector in option_selectors:
                        try:
                            options = await page.query_selector_all(selector)
                            for opt in options:
                                is_visible = await opt.is_visible()
                                if is_visible:
                                    text = await opt.inner_text()
                                    if text and ('usa' in text.lower() or 'united states' in text.lower() or 'america' in text.lower()):
                                        print(f"       [CLICKING] Option: {text[:50]}")
                                        await opt.click()
                                        option_clicked = True
                                        await asyncio.sleep(2)
                                        break
                            if option_clicked:
                                break
                        except:
                            continue
                    
                    if not option_clicked:
                        print("       No dropdown found, pressing Enter...")
                        await page.keyboard.press('Enter')
                        await asyncio.sleep(2)
                    
                    await page.screenshot(path='data/screenshots/apollo_auto_4_selected.png', full_page=True)
                
                print("\n[11/15] Looking for date inputs...")
                
                # Look for date inputs
                date_inputs = await page.query_selector_all('input[type="date"], input[placeholder*="date"], input[name*="date"]')
                
                if date_inputs:
                    print(f"       Found {len(date_inputs)} date inputs")
                    
                    pickup = (datetime.now() + timedelta(days=30)).strftime('%m/%d/%Y')
                    dropoff = (datetime.now() + timedelta(days=37)).strftime('%m/%d/%Y')
                    
                    if len(date_inputs) >= 1:
                        await date_inputs[0].click()
                        await asyncio.sleep(0.5)
                        await date_inputs[0].fill(pickup)
                        print(f"       Pickup: {pickup}")
                    
                    if len(date_inputs) >= 2:
                        await date_inputs[1].click()
                        await asyncio.sleep(0.5)
                        await date_inputs[1].fill(dropoff)
                        print(f"       Dropoff: {dropoff}")
                    
                    await asyncio.sleep(2)
                else:
                    print("       No date inputs found, continuing...")
                
                print("\n[12/15] Looking for SEARCH button...")
                
                search_btn = None
                search_selectors = [
                    'button:has-text("Search")',
                    'button:has-text("SEARCH")',
                    'button:has-text("Find")',
                    'input[type="submit"]',
                    'button[type="submit"]',
                    '[role="button"]:has-text("Search")',
                ]
                
                for selector in search_selectors:
                    try:
                        search_btn = await page.query_selector(selector)
                        if search_btn and await search_btn.is_visible():
                            print(f"       Found search button: {selector}")
                            break
                    except:
                        continue
                
                if search_btn:
                    print("\n[13/15] CLICKING Search button...")
                    await search_btn.click()
                    print("       Clicked! Waiting for results...")
                    
                    await asyncio.sleep(10)  # Wait for search results
                    
                    await page.screenshot(path='data/screenshots/apollo_auto_5_results.png', full_page=True)
                else:
                    print("       [INFO] No search button, trying Enter key...")
                    await page.keyboard.press('Enter')
                    await asyncio.sleep(10)
                
                print("\n[14/15] Extracting prices from page...")
                
                # Get all page text
                page_text = await page.evaluate('() => document.body.innerText')
                
                # Extract visible prices
                visible_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', page_text)
                
                if visible_prices:
                    print(f"       Found {len(visible_prices)} price mentions:")
                    for p in visible_prices[:20]:
                        try:
                            val = float(p.replace(',', ''))
                            if 20 <= val <= 2000:
                                prices.append(val)
                                print(f"          ${val}")
                        except:
                            pass
                
                print("\n[15/15] RESULTS")
                print("="*80)
                
                if prices:
                    unique = sorted(set(prices))
                    print(f"\n>>> SUCCESS! FOUND {len(unique)} REAL APOLLO PRICES!\n")
                    
                    for price in unique:
                        print(f"    ${price:.2f}")
                    
                    print(f"\n>>> STATISTICS:")
                    print(f"    Lowest:  ${min(prices):.2f}")
                    print(f"    Highest: ${max(prices):.2f}")
                    print(f"    Average: ${sum(prices)/len(prices):.2f}")
                    print(f"\n>>> SOURCE: booking.apollocamper.com")
                    print(f">>> METHOD: Fully automated search")
                else:
                    print("\n>>> NO PRICES EXTRACTED")
                    print("    Form might need different interaction")
                    print("    Check screenshots to see what happened:")
                    print("      - apollo_auto_1_initial.png")
                    print("      - apollo_auto_2_clicked.png")
                    print("      - apollo_auto_3_typed.png")
                    print("      - apollo_auto_4_selected.png")
                    print("      - apollo_auto_5_results.png")
            
            print("\n" + "="*80)
            print("KEEPING BROWSER OPEN 60 SECONDS")
            print("="*80 + "\n")
            
            for i in range(60, 0, -1):
                print(f"Closing in {i:02d}s...", end='\r')
                await asyncio.sleep(1)
            
            print("\n\nClosing...")
            await browser.close()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(fully_automated_search())





