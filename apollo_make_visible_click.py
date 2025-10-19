"""
Make the booking widget visible with JavaScript, then click and fill
"""

import asyncio
import sys
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def make_visible_and_click():
    """
    Force the hidden booking widget to be visible, then interact
    """
    
    print("\n" + "="*80)
    print("APOLLO - MAKE WIDGET VISIBLE + AUTOMATED CLICKING")
    print("="*80 + "\n")
    
    prices = []
    
    async with async_playwright() as p:
        print("[1/10] Launching...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=400,  # Very slow to see everything
            args=['--start-maximized']
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        # Monitor API
        async def handle_response(response):
            if 'api' in response.url and response.status == 200:
                try:
                    body = await response.text()
                    price_matches = re.findall(r'"(?:price|rate|cost|daily)":\s*(\d+(?:\.\d{2})?)', body)
                    if price_matches:
                        print(f"\n>>> [PRICE API!] {response.url[:60]}")
                        print(f"    Values: {price_matches}")
                        for p in price_matches:
                            prices.append(float(p))
                except:
                    pass
        
        page.on('response', handle_response)
        
        print("[2/10] Loading apollocamper.com...")
        
        try:
            await page.goto('https://www.apollocamper.com/', timeout=90000)
            await asyncio.sleep(8)
            
            print("\n[3/10] MAKING BOOKING WIDGET VISIBLE (removing display:none)...")
            
            # Use JavaScript to make widget visible
            made_visible = await page.evaluate('''() => {
                const widget = document.getElementById('bwp_fields');
                if (widget) {
                    widget.style.display = 'block';
                    widget.style.visibility = 'visible';
                    widget.style.opacity = '1';
                    console.log('Widget made visible!');
                    return true;
                }
                return false;
            }''')
            
            if made_visible:
                print("    [SUCCESS] Widget is now visible!")
            else:
                print("    [WARNING] Widget not found or already visible")
            
            await asyncio.sleep(2)
            await page.screenshot(path='data/screenshots/apollo_visible_1.png', full_page=True)
            
            print("\n[4/10] Scrolling to widget...")
            await page.evaluate('document.getElementById("bwp_fields").scrollIntoView({behavior: "smooth", block: "center"})')
            await asyncio.sleep(2)
            
            print("\n[5/10] Clicking PICKUP LOCATION button...")
            
            # Click trigger_pickup by ID
            pickup_clicked = await page.evaluate('''() => {
                // Try multiple IDs
                const ids = ['trigger_pickup', 'triggerPickup', 'bwp_pickup'];
                for (const id of ids) {
                    const btn = document.getElementById(id);
                    if (btn) {
                        btn.click();
                        console.log('Clicked pickup:', id);
                        return true;
                    }
                }
                // Try by text content
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    if (btn.textContent.includes('Pick up')) {
                        btn.click();
                        console.log('Clicked pickup by text');
                        return true;
                    }
                }
                return false;
            }''')
            
            if pickup_clicked:
                print("    Clicked pickup!")
                await asyncio.sleep(3)
                
                # Look for location list
                options = await page.query_selector_all('[class*="location"] li, [role="option"]')
                print(f"    Found {len(options)} location options")
                
                if options:
                    for opt in options[:20]:
                        try:
                            text = await opt.inner_text()
                            if 'los angeles' in text.lower() or 'california' in text.lower():
                                print(f"    Selecting: {text[:40]}")
                                await opt.click()
                                await asyncio.sleep(2)
                                break
                        except:
                            continue
            
            print("\n[6/10] Clicking DATES button...")
            
            dates_clicked = await page.evaluate('''() => {
                const datesBtn = document.getElementById('trigger_dates');
                if (datesBtn) {
                    datesBtn.click();
                    console.log('Clicked dates button');
                    return true;
                }
                return false;
            }''')
            
            if dates_clicked:
                print("    Clicked dates!")
                await asyncio.sleep(3)
                
                # Look for calendar
                calendar = await page.query_selector('.calendar, [class*="datepicker"], [class*="DatePicker"]')
                if calendar:
                    print("    Found calendar - clicking dates...")
                    
                    # Click cells for pickup (30 days from now) and dropoff (37 days)
                    cells = await page.query_selector_all('.cellDate[class*="selectable"]')
                    print(f"    Calendar has {len(cells)} selectable dates")
                    
                    if len(cells) > 35:
                        await cells[30].click()  # ~30 days ahead
                        await asyncio.sleep(1)
                        await cells[37].click()  # 7 days later
                        await asyncio.sleep(2)
                        print("    Selected dates!")
            
            await page.screenshot(path='data/screenshots/apollo_visible_2_filled.png', full_page=True)
            
            print("\n[7/10] Clicking PASSENGERS button...")
            
            await page.evaluate('''() => {
                const passBtn = document.getElementById('triggerPassengers');
                if (passBtn) passBtn.click();
            }''')
            await asyncio.sleep(2)
            
            # Select 2 passengers
            await page.evaluate('''() => {
                // Look for passenger count buttons/options
                const options = document.querySelectorAll('[class*="passenger"] button, [class*="passenger"] li');
                for (const opt of options) {
                    if (opt.innerText.includes('2')) {
                        opt.click();
                        break;
                    }
                }
            }''')
            
            print("    Set passengers")
            
            print("\n[8/10] Clicking SEARCH button...")
            
            # Click search
            search_clicked = await page.evaluate('''() => {
                const searchBtn = document.querySelector('.bookingWidgetSearchButton, #bwp_searchButton, button[id*="search"]');
                if (searchBtn) {
                    searchBtn.click();
                    console.log('Clicked SEARCH!');
                    return true;
                }
                return false;
            }''')
            
            if search_clicked:
                print("    [SUCCESS] Search clicked!")
                print("    Waiting 20 seconds for results...")
                
                await asyncio.sleep(20)
                
                await page.screenshot(path='data/screenshots/apollo_visible_3_results.png', full_page=True)
            
            print("\n[9/10] Extracting prices...")
            
            current_url = page.url
            page_text = await page.inner_text('body')
            
            print(f"\n    Current URL: {current_url}")
            print(f"    Page length: {len(page_text)} chars")
            
            # Extract prices
            found_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', page_text)
            
            if found_prices:
                print(f"\n    [FOUND] {len(found_prices)} price mentions:")
                for p in found_prices:
                    try:
                        val = float(p.replace(',', ''))
                        if 20 <= val <= 2000:
                            prices.append(val)
                            print(f"       ${val}")
                    except:
                        pass
            
            print("\n[10/10] FINAL RESULTS")
            print("="*80)
            
            if prices:
                unique = sorted(set(prices))
                print(f"\n>>> BREAKTHROUGH! {len(unique)} REAL APOLLO PRICES EXTRACTED!\n")
                
                for price in unique:
                    print(f"    ${price:.2f}")
                
                print(f"\n>>> STATISTICS:")
                print(f"    Lowest:  ${min(prices):.2f}")
                print(f"    Highest: ${max(prices):.2f}")
                print(f"    Average: ${sum(prices)/len(prices):.2f}")
                print(f"\n>>> METHOD: Forced widget visibility + JavaScript automation")
                print(f">>> SOURCE: apollocamper.com direct")
            else:
                print("\n>>> Still no prices in automated flow")
                print("    The widget might redirect to a search results page")
                print("    Or require additional parameters")
            
            print("\n" + "="*80)
            print("BROWSER OPEN 90 SECONDS")
            print("="*80 + "\n")
            
            for i in range(90, 0, -1):
                print(f"{i:02d}s...", end='\r')
                await asyncio.sleep(1)
            
            await browser.close()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(make_visible_and_click())

