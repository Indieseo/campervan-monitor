"""
Get REAL live prices from Apollo Motorhomes - Version 2
Enhanced Cloudflare bypass and price extraction
"""

import asyncio
import sys
import re
import time
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from loguru import logger

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def get_apollo_real_prices_v2():
    """
    Get real live prices from Apollo Motorhomes - Enhanced version
    """
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - REAL LIVE PRICE EXTRACTION V2")
    print("="*80 + "\n")
    
    async with async_playwright() as p:
        print("[1/7] Launching browser with enhanced stealth...")
        
        # Launch non-headless for Cloudflare bypass
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=100,  # Slower for more human-like behavior
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-automation',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--window-size=1920,1080',
                '--start-maximized',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/Los_Angeles',
        )
        
        page = await context.new_page()
        
        # Enhanced anti-detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = {runtime: {}, loadTimes: function() {}, csi: function() {}};
            
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        print("[2/7] Navigating to Apollo Motorhomes...")
        
        try:
            # Start with USA site
            target_url = 'https://www.apollocamper.com/'
            await page.goto(target_url, wait_until='domcontentloaded', timeout=60000)
            print(f"      Loaded: {target_url}")
            
            await asyncio.sleep(3)
            
            print("[3/7] Waiting for Cloudflare clearance...")
            
            # Extended Cloudflare wait with human behavior
            max_wait = 120  # 2 minutes
            start_time = time.time()
            cleared = False
            
            while (time.time() - start_time) < max_wait:
                elapsed = int(time.time() - start_time)
                
                # Check content
                content = await page.content()
                text_content = await page.evaluate('() => document.body.innerText') if content else ""
                
                # Check if Cloudflare is still present
                is_cloudflare = any(ind in content.lower() for ind in ['just a moment', 'checking your browser', 'verifying you are human'])
                
                if not is_cloudflare and len(content) > 10000:
                    print(f"      [OK] Cloudflare cleared after {elapsed}s")
                    cleared = True
                    break
                
                if elapsed % 5 == 0:  # Every 5 seconds
                    print(f"      [{elapsed:03d}s] Waiting... (Cloudflare check active)", end='\r')
                    
                    # Simulate human behavior
                    if elapsed % 15 == 0 and elapsed > 0:
                        # Move mouse
                        await page.mouse.move(500 + (elapsed % 100), 300 + (elapsed % 50))
                        await asyncio.sleep(0.3)
                
                await asyncio.sleep(1)
            
            print()  # New line after progress
            
            if not cleared:
                print(f"      [WARNING] Still waiting after {int(time.time() - start_time)}s")
                print("      [INFO] Continuing anyway - might need manual intervention")
            
            # Take screenshot of current state
            await page.screenshot(path='data/screenshots/apollo_v2_after_cloudflare.png', full_page=True)
            print("      Screenshot: apollo_v2_after_cloudflare.png")
            
            await asyncio.sleep(2)
            
            print("\n[4/7] Looking for vehicle/price pages...")
            
            current_content = await page.content()
            current_text = await page.evaluate('() => document.body.innerText')
            
            print(f"      Current URL: {page.url}")
            print(f"      Page length: {len(current_content)} chars")
            print(f"      Text length: {len(current_text)} chars")
            
            # Try to find links to vehicles/RVs/motorhomes
            vehicle_links = []
            
            # Look for specific links
            try:
                all_links = await page.query_selector_all('a[href]')
                print(f"      Found {len(all_links)} links on page")
                
                for link in all_links[:100]:  # Check first 100 links
                    try:
                        href = await link.get_attribute('href')
                        text = await link.inner_text()
                        
                        if href and any(keyword in href.lower() for keyword in ['vehicle', 'rv', 'motorhome', 'camper', 'rent', 'fleet', 'class']):
                            vehicle_links.append({
                                'url': href if href.startswith('http') else f"https://www.apollocamper.com{href}",
                                'text': text[:50] if text else 'N/A'
                            })
                    except:
                        continue
                
                if vehicle_links:
                    print(f"      [OK] Found {len(vehicle_links)} vehicle-related links")
                    for i, link in enumerate(vehicle_links[:5]):
                        print(f"         {i+1}. {link['text']}: {link['url']}")
                else:
                    print("      [WARNING] No vehicle links found")
            
            except Exception as e:
                print(f"      [ERROR] Link extraction failed: {e}")
            
            print("\n[5/7] Trying to navigate to vehicle pages...")
            
            # Try specific URLs known to have vehicle info
            test_urls = [
                'https://www.apollocamper.com/usa/rv-rental',
                'https://www.apollocamper.com/motorhome-rental',
                'https://www.apollocamper.com/vehicles',
                'https://www.apollocamper.com/fleet',
            ]
            
            # Add found vehicle links
            for vlink in vehicle_links[:3]:
                if vlink['url'] not in test_urls:
                    test_urls.append(vlink['url'])
            
            best_page_content = ""
            best_page_url = ""
            best_page_score = 0
            
            for test_url in test_urls:
                try:
                    print(f"      Trying: {test_url}")
                    response = await page.goto(test_url, wait_until='domcontentloaded', timeout=20000)
                    
                    if response and response.status == 200:
                        await asyncio.sleep(2)
                        
                        # Wait for potential Cloudflare again
                        cf_wait_time = 0
                        while cf_wait_time < 15:
                            content = await page.content()
                            if not any(ind in content.lower() for ind in ['just a moment', 'checking your browser']):
                                break
                            await asyncio.sleep(1)
                            cf_wait_time += 1
                        
                        content = await page.content()
                        text = await page.evaluate('() => document.body.innerText')
                        
                        # Score this page based on relevant keywords
                        score = 0
                        score += text.lower().count('$') * 2
                        score += text.lower().count('price') * 3
                        score += text.lower().count('per day') * 5
                        score += text.lower().count('per night') * 5
                        score += text.lower().count('vehicle') * 1
                        score += text.lower().count('motorhome') * 1
                        score += text.lower().count('class a') * 2
                        score += text.lower().count('class b') * 2
                        score += text.lower().count('class c') * 2
                        
                        print(f"         Score: {score}")
                        
                        if score > best_page_score:
                            best_page_score = score
                            best_page_content = text
                            best_page_url = test_url
                            
                            # Take screenshot if this looks good
                            if score > 10:
                                screenshot_name = f"data/screenshots/apollo_v2_{test_url.split('/')[-1]}.png"
                                await page.screenshot(path=screenshot_name, full_page=True)
                                print(f"         [OK] Saved screenshot: {screenshot_name}")
                
                except Exception as e:
                    print(f"         [ERROR] {str(e)[:50]}")
                    continue
            
            print(f"\n[6/7] Extracting prices from best page (score: {best_page_score})...")
            print(f"      Best URL: {best_page_url}")
            
            if not best_page_content:
                best_page_content = await page.evaluate('() => document.body.innerText')
                best_page_url = page.url
            
            # Extract prices using multiple patterns
            prices_found = []
            
            print("      Searching for price patterns...")
            
            # Pattern 1: $XXX per day/night
            matches = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per|/)\s*(?:day|night)', best_page_content, re.IGNORECASE)
            if matches:
                print(f"      Pattern '$X per day': {matches}")
                prices_found.extend([float(m.replace(',', '')) for m in matches])
            
            # Pattern 2: $XXX/day
            matches = re.findall(r'\$(\d+(?:,\d{3})*)\s*/\s*(?:day|night)', best_page_content, re.IGNORECASE)
            if matches:
                print(f"      Pattern '$/day': {matches}")
                prices_found.extend([float(m.replace(',', '')) for m in matches])
            
            # Pattern 3: From $XXX
            matches = re.findall(r'from\s*\$(\d+(?:,\d{3})*)', best_page_content, re.IGNORECASE)
            if matches:
                print(f"      Pattern 'from $': {matches}")
                prices_found.extend([float(m.replace(',', '')) for m in matches])
            
            # Pattern 4: Price: $XXX
            matches = re.findall(r'price:?\s*\$(\d+(?:,\d{3})*)', best_page_content, re.IGNORECASE)
            if matches:
                print(f"      Pattern 'price: $': {matches}")
                prices_found.extend([float(m.replace(',', '')) for m in matches])
            
            # Filter to daily rate range
            daily_rates = [p for p in prices_found if 30 <= p <= 500]
            
            print(f"\n[7/7] RESULTS")
            print("="*80)
            
            if daily_rates:
                unique_rates = sorted(set(daily_rates))
                print(f"\n      [SUCCESS] FOUND {len(daily_rates)} REAL PRICE(S)!")
                print(f"\n      PRICES FOUND: {unique_rates}")
                print(f"\n      PRICE ANALYSIS:")
                print(f"         Lowest:  ${min(daily_rates):.2f}/day")
                print(f"         Highest: ${max(daily_rates):.2f}/day")
                print(f"         Average: ${sum(daily_rates)/len(daily_rates):.2f}/day")
                print(f"         Median:  ${sorted(daily_rates)[len(daily_rates)//2]:.2f}/day")
                print(f"\n      These are REAL LIVE PRICES from Apollo Motorhomes!")
            else:
                if prices_found:
                    print(f"      [PARTIAL] Found {len(prices_found)} prices but none in daily rate range (30-500)")
                    print(f"      All prices: {sorted(set(prices_found))[:10]}")
                else:
                    print(f"      [NO PRICES FOUND]")
                    print(f"      Possible reasons:")
                    print(f"         - Cloudflare still blocking content")
                    print(f"         - Need to interact with search form")
                    print(f"         - Prices loaded via JavaScript after page render")
                    print(f"         - Booking system on different domain/subdomain")
                
                # Show sample content
                print(f"\n      Sample of page content:")
                lines = best_page_content.split('\n')
                for line in lines[:30]:
                    if line.strip():
                        print(f"      {line.strip()[:80]}")
            
            print("\n" + "="*80)
            print("EXTRACTION COMPLETE")
            print("="*80 + "\n")
            
            # Keep browser open longer to inspect
            print("Keeping browser open for 10 seconds for inspection...")
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(get_apollo_real_prices_v2())





