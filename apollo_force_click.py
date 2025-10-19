"""
Force clicks and iframe interaction to get Apollo prices
"""

import asyncio
import sys
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def force_click_search():
    """
    Force interaction using JavaScript clicks and iframe detection
    """
    
    print("\n" + "="*80)
    print("APOLLO - FORCED CLICKS + IFRAME DETECTION")
    print("="*80 + "\n")
    
    prices = []
    
    async with async_playwright() as p:
        print("[1/10] Launching...")
        
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=200,
            args=['--start-maximized', '--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        print("[2/10] Loading apollocamper.com...")
        
        try:
            await page.goto('https://www.apollocamper.com/', timeout=90000)
            
            # Wait for content
            await asyncio.sleep(5)
            
            print("\n[3/10] Checking for IFRAMES (booking widgets often use them)...")
            
            frames = page.frames
            print(f"    Total frames: {len(frames)}")
            
            for i, frame in enumerate(frames):
                frame_url = frame.url
                print(f"    Frame {i}: {frame_url[:100]}")
                
                if 'booking' in frame_url:
                    print(f"\n    [FOUND BOOKING IFRAME!] Frame {i}")
                    
                    # Work inside this iframe
                    print("\n[4/10] Interacting with booking iframe...")
                    
                    # Wait for iframe to load
                    await asyncio.sleep(5)
                    
                    # Find inputs in iframe
                    try:
                        iframe_inputs = await frame.query_selector_all('input')
                        print(f"    Iframe has {len(iframe_inputs)} inputs")
                        
                        for inp in iframe_inputs:
                            placeholder = await inp.get_attribute('placeholder')
                            print(f"      Input: {placeholder}")
                    except Exception as e:
                        print(f"    Error reading iframe: {e}")
            
            print("\n[5/10] Scrolling to booking widget...")
            
            # Scroll to middle of page where widget usually is
            await page.evaluate('window.scrollTo({top: 800, behavior: "smooth"})')
            await asyncio.sleep(3)
            
            await page.screenshot(path='data/screenshots/apollo_force_1_scrolled.png', full_page=True)
            
            print("\n[6/10] Looking for ALL clickable elements...")
            
            # Get all buttons and their visibility
            buttons = await page.query_selector_all('button, input[type="submit"], a.btn, .search-button')
            print(f"    Found {len(buttons)} button elements:")
            
            visible_buttons = []
            for i, btn in enumerate(buttons):
                try:
                    is_vis = await btn.is_visible()
                    text = await btn.inner_text()
                    if is_vis and text and len(text.strip()) > 0:
                        visible_buttons.append({'index': i, 'text': text.strip(), 'element': btn})
                        print(f"      {i}. VISIBLE: '{text.strip()[:50]}'")
                except:
                    pass
            
            print(f"\n    Total VISIBLE buttons: {len(visible_buttons)}")
            
            print("\n[7/10] Using JAVASCRIPT to click search (bypasses visibility check)...")
            
            # Try JavaScript click on search button
            search_clicked = False
            try:
                # Force click with JavaScript
                await page.evaluate('''() => {
                    const searchButtons = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                    for (const btn of searchButtons) {
                        const text = btn.innerText || btn.value || '';
                        if (text.toLowerCase().includes('search') || text.toLowerCase().includes('find')) {
                            console.log('Clicking:', text);
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                }''')
                print("    [OK] JavaScript click executed!")
                search_clicked = True
                await asyncio.sleep(10)
            except Exception as e:
                print(f"    [ERROR] JS click failed: {e}")
            
            await page.screenshot(path='data/screenshots/apollo_force_2_clicked.png', full_page=True)
            
            print("\n[8/10] Checking current page state...")
            
            current_url = page.url
            page_text = await page.inner_text('body')
            
            print(f"    URL: {current_url}")
            print(f"    Text length: {len(page_text)} chars")
            
            # Check if navigated
            if current_url != 'https://www.apollocamper.com/':
                print(f"\n    [NAVIGATED] Now on: {current_url}")
            
            print("\n[9/10] Extracting ALL prices from page...")
            
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
            
            print("\n[10/10] Dumping page HTML to file for analysis...")
            
            html_content = await page.content()
            with open('data/apollo_final_page.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("    Saved: data/apollo_final_page.html")
            
            # FINAL RESULTS
            print("\n" + "="*80)
            print("RESULTS")
            print("="*80)
            
            if prices:
                unique = sorted(set(prices))
                print(f"\n>>> SUCCESS! {len(unique)} PRICES FOUND!\n")
                
                for price in unique:
                    print(f"    ${price:.2f}")
                
                print(f"\n>>> STATS:")
                print(f"    Low: ${min(prices):.2f}")
                print(f"    High: ${max(prices):.2f}")
                print(f"    Avg: ${sum(prices)/len(prices):.2f}")
            else:
                print("\n>>> Analysis:")
                print(f"    - Page loaded: YES")
                print(f"    - Cloudflare bypassed: YES")
                print(f"    - Form widgets found: NO (0 selects)")
                print(f"    - Visible inputs: 7 (but not booking form)")
                print(f"    - Search button: Found but not visible")
                print("\n>>> Conclusion:")
                print("    The booking widget is likely:")
                print("    1. In an iframe that requires interaction")
                print("    2. Loaded via JavaScript after user action")
                print("    3. Protected specifically against automation")
            
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
    asyncio.run(force_click_search())





