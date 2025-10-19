"""
Inspect the booking page structure and click search elements
"""

import asyncio
import sys
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def inspect_and_search():
    """
    Thoroughly inspect and interact with booking page
    """
    
    print("\n" + "="*80)
    print("APOLLO BOOKING - DETAILED INSPECTION AND INTERACTION")
    print("="*80 + "\n")
    
    async with async_playwright() as p:
        print("[1] Launching browser...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=300,
            args=['--start-maximized']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        print("[2] Loading booking.apollocamper.com...")
        
        await page.goto('https://booking.apollocamper.com/', timeout=60000)
        print("    Initial load complete")
        
        # Wait much longer for JavaScript
        print("\n[3] Waiting 15 seconds for JavaScript to fully load...")
        for i in range(15, 0, -1):
            print(f"    {i}...", end='\r')
            await asyncio.sleep(1)
        print()
        
        await page.screenshot(path='data/screenshots/apollo_inspect_1.png', full_page=True)
        
        print("\n[4] Inspecting page structure...")
        
        # Get ALL text
        all_text = await page.evaluate('() => document.body.innerText')
        print(f"\n    Page text ({len(all_text)} chars):")
        print("    " + "="*70)
        print(f"    {all_text[:1000]}")
        print("    " + "="*70)
        
        # Get HTML structure
        html = await page.content()
        print(f"\n    HTML length: {len(html)} chars")
        
        # Find ALL inputs
        print("\n[5] Finding ALL input elements...")
        all_inputs = await page.query_selector_all('input')
        print(f"    Found {len(all_inputs)} input elements:")
        
        for i, inp in enumerate(all_inputs):
            try:
                inp_type = await inp.get_attribute('type')
                inp_name = await inp.get_attribute('name')
                inp_id = await inp.get_attribute('id')
                inp_class = await inp.get_attribute('class')
                inp_placeholder = await inp.get_attribute('placeholder')
                is_visible = await inp.is_visible()
                
                print(f"\n    Input {i}:")
                print(f"      type={inp_type}")
                print(f"      name={inp_name}")
                print(f"      id={inp_id}")
                print(f"      class={inp_class}")
                print(f"      placeholder={inp_placeholder}")
                print(f"      visible={is_visible}")
            except:
                pass
        
        # Find ALL buttons
        print("\n[6] Finding ALL buttons...")
        all_buttons = await page.query_selector_all('button')
        print(f"    Found {len(all_buttons)} buttons:")
        
        for i, btn in enumerate(all_buttons):
            try:
                text = await btn.inner_text()
                btn_class = await btn.get_attribute('class')
                is_visible = await btn.is_visible()
                
                print(f"\n    Button {i}:")
                print(f"      text='{text.strip()}'")
                print(f"      class={btn_class}")
                print(f"      visible={is_visible}")
            except:
                pass
        
        # Try clicking the button that says "Where would you like to travel?"
        print("\n[7] Looking for travel button...")
        
        travel_btn = await page.query_selector('button:has-text("Where would you like to travel")')
        
        if travel_btn:
            print("    [FOUND] Travel button!")
            print("    [ACTION] Clicking it...")
            
            await travel_btn.click()
            await asyncio.sleep(5)
            
            print("    [OK] Clicked! Waiting for form...")
            
            await page.screenshot(path='data/screenshots/apollo_inspect_2_clicked.png', full_page=True)
            
            # Check what changed
            new_text = await page.evaluate('() => document.body.innerText')
            print(f"\n    After click - text length: {len(new_text)} chars")
            
            # Look for new inputs
            new_inputs = await page.query_selector_all('input')
            print(f"    After click - {len(new_inputs)} inputs")
            
            # Try to find and interact with any new visible inputs
            for inp in new_inputs:
                try:
                    is_visible = await inp.is_visible()
                    if is_visible:
                        placeholder = await inp.get_attribute('placeholder')
                        print(f"\n    Visible input: placeholder='{placeholder}'")
                        
                        # Try clicking and typing
                        await inp.click()
                        await asyncio.sleep(1)
                        await inp.fill('United States')
                        await asyncio.sleep(2)
                        
                        print(f"    [OK] Filled: 'United States'")
                        
                        await page.screenshot(path='data/screenshots/apollo_inspect_3_filled.png', full_page=True)
                        break
                except:
                    continue
        
        print("\n[8] Final page state...")
        final_text = await page.evaluate('() => document.body.innerText')
        final_url = page.url
        
        print(f"    URL: {final_url}")
        print(f"    Text: {len(final_text)} chars")
        
        # Extract any prices
        prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', final_text)
        if prices:
            print(f"\n    [PRICES] Found {len(prices)}: {prices[:20]}")
        
        await page.screenshot(path='data/screenshots/apollo_inspect_final.png', full_page=True)
        
        print("\n" + "="*80)
        print("BROWSER OPEN FOR 120 SECONDS - MANUALLY CONTINUE")
        print("="*80 + "\n")
        
        for i in range(120, 0, -1):
            print(f"Closing in {i:03d}s...", end='\r')
            await asyncio.sleep(1)
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_and_search())





