"""
Use PURE JavaScript to fill and submit Apollo booking form
Bypass all visibility checks
"""

import asyncio
import sys
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def pure_javascript_automation():
    """
    Use pure JavaScript for all interactions
    """
    
    print("\n" + "="*80)
    print("APOLLO - PURE JAVASCRIPT AUTOMATION (100% JS CLICKS)")
    print("="*80 + "\n")
    
    prices = []
    
    async with async_playwright() as p:
        print("[1/6] Launching...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=500,
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
                        print(f"\n>>> [PRICE API!] {response.url[:70]}")
                        print(f"    Prices: {price_matches}")
                        for p in price_matches:
                            prices.append(float(p))
                except:
                    pass
        
        page.on('response', handle_response)
        
        print("[2/6] Loading apollocamper.com...")
        
        try:
            await page.goto('https://www.apollocamper.com/', timeout=90000)
            await asyncio.sleep(10)
            
            print("\n[3/6] Using PURE JAVASCRIPT to fill entire form...")
            
            # Execute comprehensive JavaScript to fill and submit form
            result = await page.evaluate('''async () => {
                const log = [];
                
                // 1. Make widget visible
                const widget = document.getElementById('bwp_fields');
                if (widget) {
                    widget.style.display = 'block';
                    widget.style.visibility = 'visible';
                    widget.style.opacity = '1';
                    log.push('Widget made visible');
                }
                
                // Wait a bit
                await new Promise(r => setTimeout(r, 1000));
                
                // 2. Click pickup location button  
                const pickupButtons = document.querySelectorAll('button');
                for (const btn of pickupButtons) {
                    if (btn.textContent.includes('Pick up from')) {
                        btn.click();
                        log.push('Clicked pickup trigger');
                        await new Promise(r => setTimeout(r, 3000));
                        
                        // Select first location option - try multiple selectors
                        const locationItems = document.querySelectorAll('.widgetLocations button.item, ul li button, [class*="location"] button');
                        log.push('Found ' + locationItems.length + ' location items');
                        
                        if (locationItems.length > 0) {
                            // Click first real location (skip headers)
                            for (let i = 0; i < Math.min(10, locationItems.length); i++) {
                                const text = locationItems[i].textContent;
                                if (text && !text.includes('Same as') && text.length > 2) {
                                    locationItems[i].click();
                                    log.push('Selected location: ' + text.substring(0, 30));
                                    break;
                                }
                            }
                        }
                        break;
                    }
                }
                
                await new Promise(r => setTimeout(r, 1000));
                
                // 3. Click dates button
                const datesTrigger = document.getElementById('trigger_dates');
                if (datesTrigger) {
                    datesTrigger.click();
                    log.push('Clicked dates trigger');
                    await new Promise(r => setTimeout(r, 2000));
                    
                    // Click calendar dates
                    const dateCells = document.querySelectorAll('.cellDate.selectable');
                    if (dateCells.length > 35) {
                        dateCells[30].click();  // Pickup
                        await new Promise(r => setTimeout(r, 500));
                        dateCells[37].click();  // Dropoff
                        log.push('Selected dates from calendar');
                    }
                }
                
                await new Promise(r => setTimeout(r, 1000));
                
                // 4. Click passengers
                const passengersTrigger = document.getElementById('triggerPassengers');
                if (passengersTrigger) {
                    passengersTrigger.click();
                    log.push('Clicked passengers trigger');
                    await new Promise(r => setTimeout(r, 1000));
                    
                    // Increment passenger count
                    const incrementBtn = document.querySelector('.widgetPassengers .increment');
                    if (incrementBtn) {
                        incrementBtn.click();
                        log.push('Incremented passengers');
                    }
                }
                
                await new Promise(r => setTimeout(r, 1000));
                
                // 5. Click search button
                const searchBtn = document.querySelector('.bookingWidgetSearchButton, button[class*="search"]');
                if (searchBtn) {
                    searchBtn.click();
                    log.push('CLICKED SEARCH BUTTON!');
                } else {
                    // Try finding any button with "search" in class or text
                    const allButtons = document.querySelectorAll('button');
                    for (const btn of allButtons) {
                        if (btn.textContent.toLowerCase().includes('search')) {
                            btn.click();
                            log.push('Clicked search via text match');
                            break;
                        }
                    }
                }
                
                return log;
            }''')
            
            print("\n   JavaScript execution log:")
            for line in result:
                print(f"      - {line}")
            
            print("\n[4/6] Waiting 20 seconds for search results...")
            await asyncio.sleep(20)
            
            await page.screenshot(path='data/screenshots/apollo_js_results.png', full_page=True)
            
            print("\n[5/6] Extracting prices from results page...")
            
            current_url = page.url
            page_text = await page.inner_text('body')
            
            print(f"\n    Current URL: {current_url}")
            print(f"    Page text length: {len(page_text)} chars")
            
            # Extract all dollar amounts
            found_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', page_text)
            
            if found_prices:
                print(f"\n    [PRICES ON PAGE] Found {len(found_prices)} mentions:")
                for p in found_prices:
                    try:
                        val = float(p.replace(',', ''))
                        if 20 <= val <= 2000:
                            prices.append(val)
                            print(f"       ${val}")
                    except:
                        pass
            
            # Look for vehicle results
            vehicles = await page.query_selector_all('[class*="vehicle"], article, .result-card')
            if vehicles:
                print(f"\n    Found {len(vehicles)} vehicle elements")
            
            print("\n[6/6] RESULTS")
            print("="*80)
            
            if prices:
                unique = sorted(set(prices))
                print(f"\n>>> BREAKTHROUGH! {len(unique)} REAL APOLLO PRICES!\n")
                
                for price in unique:
                    print(f"    ${price:.2f}")
                
                print(f"\n>>> STATISTICS:")
                print(f"    Lowest:  ${min(prices):.2f}")
                print(f"    Highest: ${max(prices):.2f}")
                print(f"    Average: ${sum(prices)/len(prices):.2f}")
                print(f"\n>>> METHOD: 100% JavaScript automation")
                print(f">>> SOURCE: apollocamper.com")
            else:
                print("\n>>> NO PRICES EXTRACTED YET")
                print(f"    Check screenshot: apollo_js_results.png")
                print(f"    Current URL: {current_url}")
            
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
    asyncio.run(pure_javascript_automation())

