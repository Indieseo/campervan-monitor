"""
Advanced Interactive Cloudflare Bypass for Apollo Motorhomes
Uses real human-like clicking, scrolling, and form interaction
"""

import asyncio
import sys
import re
import random
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def human_like_delay(min_ms=500, max_ms=2000):
    """Random human-like delay"""
    await asyncio.sleep(random.uniform(min_ms/1000, max_ms/1000))


async def move_mouse_naturally(page, x, y):
    """Move mouse in a natural curved path"""
    current_x, current_y = 0, 0
    steps = random.randint(10, 20)
    
    for i in range(steps):
        intermediate_x = current_x + (x - current_x) * (i / steps)
        intermediate_y = current_y + (y - current_y) * (i / steps)
        # Add slight randomness
        intermediate_x += random.uniform(-5, 5)
        intermediate_y += random.uniform(-5, 5)
        await page.mouse.move(intermediate_x, intermediate_y)
        await asyncio.sleep(random.uniform(0.01, 0.03))


async def interactive_apollo_crawl():
    """
    Interactive crawl with human-like behavior
    """
    
    print("\n" + "="*80)
    print("APOLLO - ADVANCED INTERACTIVE CLOUDFLARE BYPASS")
    print("="*80 + "\n")
    
    prices_found = []
    
    async with async_playwright() as p:
        print("[1/10] Launching REAL browser (you'll see it)...")
        
        # Launch with maximum stealth
        browser = await p.chromium.launch(
            headless=False,  # MUST be False
            slow_mo=50,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-automation',
                '--disable-infobars',
                '--window-size=1920,1080',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/Los_Angeles',
            geolocation={'latitude': 34.0522, 'longitude': -118.2437},
            permissions=['geolocation'],
        )
        
        page = await context.new_page()
        
        # Maximum stealth injection
        await page.add_init_script("""
            // Remove all automation traces
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                    {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                    {name: 'Native Client', filename: 'internal-nacl-plugin'}
                ]
            });
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = {runtime: {}, loadTimes: function() {}, csi: function() {}, app: {}};
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            
            // Remove automation flags
            delete window.navigator.__proto__.webdriver;
            window.navigator.chrome = {runtime: {}};
        """)
        
        print("[2/10] Navigating to Apollo homepage...")
        print("       URL: https://www.apollocamper.com/\n")
        
        try:
            await page.goto('https://www.apollocamper.com/', wait_until='domcontentloaded', timeout=90000)
            
            print("[3/10] Simulating REAL HUMAN behavior...")
            print("       - Random mouse movements")
            print("       - Natural scrolling")
            print("       - Realistic delays\n")
            
            # Wait for initial load
            await human_like_delay(2000, 3000)
            
            # Natural mouse movements
            for _ in range(5):
                x = random.randint(200, 1700)
                y = random.randint(200, 800)
                await move_mouse_naturally(page, x, y)
                await human_like_delay(300, 800)
            
            # Natural scrolling
            print("[4/10] Scrolling page naturally...")
            for scroll_pos in [300, 600, 900, 1200, 600, 0]:
                await page.evaluate(f'window.scrollTo({{top: {scroll_pos}, behavior: "smooth"}})')
                await human_like_delay(800, 1500)
            
            # Check if Cloudflare cleared
            text = await page.evaluate('() => document.body.innerText')
            content = await page.content()
            
            is_blocked = 'cloudflare' in text.lower() or 'verifying' in text.lower()
            
            if is_blocked:
                print("       [WAITING] Cloudflare challenge active...")
                
                # Extended wait with more human behavior
                for i in range(20):
                    await asyncio.sleep(1)
                    await page.mouse.move(500 + i*20, 400 + i*10)
                    
                    text = await page.evaluate('() => document.body.innerText')
                    if 'cloudflare' not in text.lower():
                        print(f"       [SUCCESS] Cleared after {i+1} seconds!")
                        break
            else:
                print("       [OK] No Cloudflare challenge detected!")
            
            await page.screenshot(path='data/screenshots/apollo_interactive_1.png')
            print("\n[5/10] Looking for booking widget...")
            
            # Look for the booking form
            await asyncio.sleep(2)
            
            # Try to find "Check Availability" button
            check_button = await page.query_selector('button:has-text("CHECK AVAILABILITY"), a:has-text("CHECK AVAILABILITY")')
            
            if check_button:
                print("       [FOUND] Check Availability button!")
                print("       [ACTION] Moving mouse to button...")
                
                # Get button position
                box = await check_button.bounding_box()
                if box:
                    await move_mouse_naturally(page, box['x'] + box['width']/2, box['y'] + box['height']/2)
                    await human_like_delay(500, 1000)
                    
                    print("       [ACTION] Clicking button...")
                    try:
                        await check_button.click()
                        await human_like_delay(3000, 5000)
                        print("       [OK] Clicked!")
                    except:
                        print("       [FAILED] Could not click, trying link navigation...")
            
            print("\n[6/10] Looking for vehicle/pricing links...")
            
            # Find all links
            links = await page.query_selector_all('a')
            vehicle_links = []
            
            for link in links[:50]:
                try:
                    href = await link.get_attribute('href')
                    text = await link.inner_text()
                    
                    if href and any(keyword in href.lower() for keyword in ['vehicle', 'motorhome', 'camper', 'rv', 'rent']):
                        if text and len(text) < 50:
                            vehicle_links.append({'href': href, 'text': text})
                            print(f"       Found: {text} -> {href}")
                except:
                    continue
            
            if vehicle_links:
                print(f"\n[7/10] Clicking on first vehicle link: {vehicle_links[0]['text']}")
                
                # Click the first vehicle link
                try:
                    link = await page.query_selector(f'a[href*="{vehicle_links[0]["href"]}"]')
                    if link:
                        box = await link.bounding_box()
                        if box:
                            await move_mouse_naturally(page, box['x'] + 20, box['y'] + 10)
                            await human_like_delay(500, 1000)
                            await link.click()
                            await human_like_delay(3000, 5000)
                            
                            # Check new page
                            new_text = await page.evaluate('() => document.body.innerText')
                            new_url = page.url
                            
                            print(f"       [OK] Navigated to: {new_url}")
                            
                            # Look for prices
                            new_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', new_text)
                            if new_prices:
                                print(f"       [PRICES FOUND] {len(new_prices)} price mentions:")
                                for p in new_prices[:15]:
                                    try:
                                        val = float(p.replace(',', ''))
                                        if 30 <= val <= 1000:
                                            prices_found.append(val)
                                            print(f"          ${val}")
                                    except:
                                        pass
                            
                            await page.screenshot(path='data/screenshots/apollo_interactive_2.png')
                except Exception as e:
                    print(f"       [ERROR] {str(e)[:50]}")
            
            print("\n[8/10] Trying direct URLs with session cookies...")
            
            # Now that we have session cookies, try direct URLs
            direct_urls = [
                'https://www.apollocamper.com/vehicles',
                'https://www.apollocamper.com/usa',
                'https://www.apollocamper.com/motorhomes',
            ]
            
            for url in direct_urls:
                try:
                    print(f"\n       Trying: {url}")
                    
                    # Human-like navigation delay
                    await human_like_delay(2000, 3000)
                    
                    response = await page.goto(url, wait_until='networkidle', timeout=30000)
                    print(f"       Status: {response.status}")
                    
                    if response.status == 200:
                        await human_like_delay(2000, 3000)
                        
                        # Scroll page
                        await page.evaluate('window.scrollTo({top: 500, behavior: "smooth"})')
                        await human_like_delay(1000, 2000)
                        
                        text = await page.evaluate('() => document.body.innerText')
                        
                        if 'cloudflare' not in text.lower():
                            page_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
                            if page_prices:
                                print(f"       [FOUND] {len(page_prices)} prices:")
                                for p in page_prices[:10]:
                                    try:
                                        val = float(p.replace(',', ''))
                                        if 30 <= val <= 1000:
                                            prices_found.append(val)
                                            print(f"          ${val}")
                                    except:
                                        pass
                        else:
                            print(f"       [BLOCKED] Cloudflare active")
                except Exception as e:
                    print(f"       [ERROR] {str(e)[:40]}")
            
            print("\n[9/10] Extracting all page content...")
            
            final_text = await page.evaluate('() => document.body.innerText')
            final_prices = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', final_text)
            
            for p in final_prices:
                try:
                    val = float(p.replace(',', ''))
                    if 30 <= val <= 1000:
                        prices_found.append(val)
                except:
                    pass
            
            await page.screenshot(path='data/screenshots/apollo_interactive_final.png')
            
            print("\n[10/10] RESULTS")
            print("="*80)
            
            if prices_found:
                unique_prices = sorted(set(prices_found))
                print(f"\n>>> SUCCESS! Found {len(unique_prices)} REAL PRICES:")
                print()
                for price in unique_prices:
                    print(f"    ${price:.2f}")
                
                print(f"\n>>> STATISTICS:")
                print(f"    Lowest:  ${min(prices_found):.2f}/day")
                print(f"    Highest: ${max(prices_found):.2f}/day")
                print(f"    Average: ${sum(prices_found)/len(prices_found):.2f}/day")
            else:
                print("\n>>> NO PRICES EXTRACTED")
                print("    Apollo's protection is very strong")
                print("    May require actual search with dates/locations")
            
            print("\n" + "="*80)
            print("BROWSER WILL STAY OPEN FOR 60 SECONDS")
            print("You can manually navigate to see more")
            print("="*80 + "\n")
            
            # Keep browser open
            for i in range(60, 0, -1):
                print(f"Closing in {i:02d} seconds...", end='\r')
                await asyncio.sleep(1)
            
            print("\n\nClosing...")
            await browser.close()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(interactive_apollo_crawl())





