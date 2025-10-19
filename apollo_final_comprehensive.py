"""
FINAL COMPREHENSIVE Apollo automation
Combining ALL techniques with extensive logging and fallback strategies
"""

import asyncio
import sys
import re
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def final_comprehensive_search():
    """
    Final comprehensive automated search
    """
    
    print("\n" + "="*80)
    print("APOLLO - FINAL COMPREHENSIVE AUTOMATED SEARCH")
    print("="*80 + "\n")
    
    prices = []
    api_calls = []
    
    async with async_playwright() as p:
        print(">>> Launching Chrome with stealth...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=100,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-automation',
                '--no-sandbox',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )
        
        page = await context.new_page()
        
        # Anti-detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        """)
        
        # Monitor API calls
        async def handle_response(response):
            url = response.url
            api_calls.append(url)
            
            if 'api' in url and response.status == 200:
                try:
                    body = await response.text()
                    if '"price"' in body or '"rate"' in body:
                        print(f"\n>>> [PRICE API FOUND] {url}")
                        print(f"    Response: {body[:200]}...")
                        
                        price_vals = re.findall(r'"(?:price|rate|cost|total)":\s*(\d+(?:\.\d{2})?)', body)
                        for p in price_vals:
                            prices.append(float(p))
                except:
                    pass
        
        page.on('response', handle_response)
        
        print(">>> Going to apollocamper.com (MAIN SITE)...")
        
        try:
            await page.goto('https://www.apollocamper.com/', timeout=90000)
            
            print(">>> Waiting for page to fully load (60 seconds)...")
            
            # Wait for proper content
            for i in range(60):
                await asyncio.sleep(1)
                try:
                    text = await page.inner_text('body', timeout=2000)
                    if len(text) > 1000 and 'motorhome' in text.lower():
                        print(f"\n>>> Page loaded successfully after {i+1} seconds!")
                        break
                except:
                    pass
            
            # Take screenshot
            await page.screenshot(path='data/screenshots/apollo_final_1_loaded.png', full_page=True)
            
            print("\n>>> STEP 1: Inspecting homepage booking widget...")
            
            # Log all form elements
            print("\n    All SELECT elements on page:")
            selects = await page.query_selector_all('select')
            for i, sel in enumerate(selects):
                try:
                    name = await sel.get_attribute('name')
                    id_attr = await sel.get_attribute('id')
                    is_vis = await sel.is_visible()
                    if is_vis:
                        # Get options
                        options = await sel.query_selector_all('option')
                        first_opt = await options[0].inner_text() if options else 'N/A'
                        print(f"      Select {i}: name={name}, id={id_attr}, first_option={first_opt[:30]}")
                except:
                    pass
            
            print("\n    All INPUT elements (visible only):")
            inputs = await page.query_selector_all('input')
            visible_inputs = []
            for i, inp in enumerate(inputs):
                try:
                    is_vis = await inp.is_visible()
                    if is_vis:
                        inp_type = await inp.get_attribute('type')
                        name = await inp.get_attribute('name')
                        placeholder = await inp.get_attribute('placeholder')
                        visible_inputs.append(inp)
                        print(f"      Input {i}: type={inp_type}, name={name}, placeholder={placeholder}")
                except:
                    pass
            
            print(f"\n    Total visible inputs: {len(visible_inputs)}")
            
            print("\n>>> STEP 2: Filling out homepage booking widget...")
            
            # Try to fill the widget on the homepage
            filled_count = 0
            
            # 1. Pick up location
            try:
                pickup_loc = await page.query_selector('select#ctl00_ContentPlaceHolder1_StartLocation, select[name*="StartLocation"]')
                if pickup_loc:
                    print("\n    [1/5] Pickup Location...")
                    options = await pickup_loc.query_selector_all('option')
                    for opt in options:
                        text = await opt.inner_text()
                        value = await opt.get_attribute('value')
                        if 'los angeles' in text.lower() or 'lax' in value.lower() or value == '210':  # Common LA codes
                            print(f"          Selecting: {text}")
                            await pickup_loc.select_option(value=value)
                            filled_count += 1
                            await asyncio.sleep(1)
                            break
            except Exception as e:
                print(f"    [ERROR] Pickup location: {str(e)[:50]}")
            
            # 2. Drop off location
            try:
                dropoff_loc = await page.query_selector('select#ctl00_ContentPlaceHolder1_EndLocation, select[name*="EndLocation"]')
                if dropoff_loc:
                    print("\n    [2/5] Dropoff Location...")
                    await dropoff_loc.select_option(index=0)  # Usually "Same as pickup"
                    filled_count += 1
                    await asyncio.sleep(1)
                    print("          Same as pickup")
            except Exception as e:
                print(f"    [ERROR] Dropoff: {str(e)[:50]}")
            
            # 3. Dates
            try:
                pickup_date = (datetime.now() + timedelta(days=30)).strftime('%m/%d/%Y')
                dropoff_date = (datetime.now() + timedelta(days=37)).strftime('%m/%d/%Y')
                
                date_input = await page.query_selector('input[name*="Date"], input[placeholder*="Date"]')
                if date_input:
                    print(f"\n    [3/5] Travel Dates...")
                    await date_input.click()
                    await asyncio.sleep(1)
                    await date_input.fill(f"{pickup_date} - {dropoff_date}")
                    filled_count += 1
                    await asyncio.sleep(1)
                    print(f"          {pickup_date} - {dropoff_date}")
            except Exception as e:
                print(f"    [ERROR] Dates: {str(e)[:50]}")
            
            # 4. Passengers
            try:
                passengers = await page.query_selector('select[name*="Passenger"]')
                if passengers:
                    print("\n    [4/5] Passengers...")
                    await passengers.select_option(value='2')
                    filled_count += 1
                    await asyncio.sleep(1)
                    print("          2 passengers")
            except Exception as e:
                print(f"    [ERROR] Passengers: {str(e)[:50]}")
            
            # 5. License
            try:
                license_sel = await page.query_selector('select[name*="Licence"], select[name*="License"]')
                if license_sel:
                    print("\n    [5/5] Driver License...")
                    await license_sel.select_option(index=1)  # First real option
                    filled_count += 1
                    await asyncio.sleep(1)
                    print("          Selected")
            except Exception as e:
                print(f"    [ERROR] License: {str(e)[:50]}")
            
            print(f"\n    >>> Filled {filled_count}/5 fields")
            
            await page.screenshot(path='data/screenshots/apollo_final_2_filled_form.png', full_page=True)
            
            print("\n>>> STEP 3: Clicking SEARCH button...")
            
            # Find and click search
            search_btn = await page.query_selector('button:has-text("Search"), input[type="submit"][value*="Search"], .search-button')
            
            if search_btn:
                print("    [FOUND] Search button!")
                print("    [CLICKING] ...")
                
                await search_btn.click()
                
                print("    [WAITING] For search results (30 seconds)...")
                await asyncio.sleep(30)
                
                await page.screenshot(path='data/screenshots/apollo_final_3_results.png', full_page=True)
                
                print("\n>>> STEP 4: Extracting prices from results...")
                
                current_url = page.url
                page_text = await page.inner_text('body')
                
                print(f"\n    Current URL: {current_url}")
                print(f"    Page text length: {len(page_text)} chars")
                
                # Extract prices
                visible_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', page_text)
                
                if visible_prices:
                    print(f"\n    [FOUND] {len(visible_prices)} price mentions on page:")
                    for p in visible_prices:
                        try:
                            val = float(p.replace(',', ''))
                            if 20 <= val <= 2000:
                                prices.append(val)
                                print(f"       ${val}")
                        except:
                            pass
                
                # Look for vehicle cards
                vehicles = await page.query_selector_all('[class*="vehicle"], [class*="result"], article, .product-card')
                print(f"\n    Found {len(vehicles)} potential vehicle elements")
                
                for i, veh in enumerate(vehicles[:5]):
                    try:
                        veh_text = await veh.inner_text()
                        veh_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', veh_text)
                        if veh_prices:
                            print(f"    Vehicle {i}: {veh_prices}")
                    except:
                        pass
            
            else:
                print("    [NOT FOUND] No search button - form may not have loaded")
            
            # RESULTS
            print("\n" + "="*80)
            print("RESULTS")
            print("="*80)
            
            print(f"\nAPI Calls Captured: {len([a for a in api_calls if 'api' in a.lower()])}")
            
            if prices:
                unique = sorted(set(prices))
                print(f"\n>>> SUCCESS! {len(unique)} UNIQUE PRICES EXTRACTED!\n")
                
                for price in unique:
                    print(f"    ${price:.2f}")
                
                if len(unique) > 0:
                    print(f"\n>>> STATISTICS:")
                    print(f"    Lowest:  ${min(prices):.2f}")
                    print(f"    Highest: ${max(prices):.2f}")
                    print(f"    Average: ${sum(prices)/len(prices):.2f}")
                    print(f"\n>>> SOURCE: Direct from apollocamper.com")
                    print(f">>> METHOD: Automated form submission")
            else:
                print("\n>>> NO PRICES EXTRACTED IN AUTOMATION")
                print("\nPossible reasons:")
                print("  - Form didn't load all required fields")
                print("  - Search failed or redirected")
                print("  - Results page requires additional interaction")
                print("  - Cloudflare blocked the search endpoint")
            
            print("\n" + "="*80)
            print("BROWSER STAYS OPEN 90 SECONDS")
            print("="*80 + "\n")
            
            for i in range(90, 0, -1):
                print(f"{i:02d}s...", end='\r')
                await asyncio.sleep(1)
            
            print("\n\nClosing...")
            await browser.close()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(final_comprehensive_search())





