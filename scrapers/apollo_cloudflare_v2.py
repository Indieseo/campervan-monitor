"""
Apollo Motorhomes - Enhanced Cloudflare Bypass V2
Uses playwright-stealth, extended waits, and smarter detection
"""

import asyncio
import sys
import time
from playwright.async_api import async_playwright, Page
from loguru import logger

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def bypass_apollo_cloudflare():
    """
    Enhanced Cloudflare bypass for Apollo Motorhomes
    
    Key improvements:
    1. Non-headless browser (Cloudflare detects headless)
    2. Extended wait times (up to 60 seconds)
    3. Better human simulation
    4. Multiple retry attempts
    5. Real browser profile
    """
    
    print("\n" + "="*80)
    print("APOLLO MOTORHOMES - ENHANCED CLOUDFLARE BYPASS V2")
    print("="*80 + "\n")
    
    target_url = "https://www.apollocamper.com/"
    
    async with async_playwright() as p:
        print("[1/6] Launching non-headless Chrome with stealth settings...")
        
        # Launch browser in non-headless mode (critical for Cloudflare)
        browser = await p.chromium.launch(
            headless=False,  # MUST be False for Cloudflare
            slow_mo=50,  # Slow down operations to appear more human
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--window-size=1920,1080',
                '--start-maximized',
                # Additional stealth flags
                '--disable-automation',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
            ]
        )
        
        print("[2/6] Creating realistic browser context...")
        
        # Create context with realistic settings
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            java_script_enabled=True,
        )
        
        page = await context.new_page()
        
        print("[3/6] Injecting anti-detection scripts...")
        
        # Inject comprehensive anti-detection
        await page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Override the `plugins` property to use a custom getter.
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Override the `languages` property to use a custom getter.
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Override the `chrome` property
            window.chrome = {
                runtime: {}
            };
            
            // Pass the Permission Test
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Pass the Plugins Length Test
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Pass the Languages Test
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Pass the iframe Test
            Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                get: function() {
                    return window;
                }
            });
            
            // Pass toString test, though it breaks console.debug()
            window.console.debug = () => {
                return null;
            };
        """)
        
        print("[4/6] Navigating to Apollo Motorhomes...")
        print(f"      Target: {target_url}")
        
        try:
            # Navigate with extended timeout
            await page.goto(target_url, wait_until='domcontentloaded', timeout=60000)
            print("      [OK] Initial navigation complete")
        except Exception as e:
            print(f"      [ERROR] Navigation failed: {e}")
            return
        
        # Take initial screenshot
        await page.screenshot(path="data/screenshots/Apollo_v2_step1_initial.png", full_page=True)
        print("      [OK] Screenshot 1: Initial page")
        
        # Wait a bit
        await asyncio.sleep(3)
        
        print("\n[5/6] Checking for Cloudflare challenge...")
        
        # Check for Cloudflare
        content = await page.content()
        has_cloudflare = any(indicator in content.lower() for indicator in [
            'cloudflare', 'just a moment', 'checking your browser', 'ray id'
        ])
        
        if has_cloudflare:
            print("      [DETECTED] Cloudflare challenge present")
            print("      [WAIT] Allowing up to 60 seconds for clearance...")
            print("             (Watch the browser window - challenge should solve automatically)")
            
            # Simulate very human-like behavior
            print("\n      Simulating human behavior:")
            await asyncio.sleep(2)
            
            # Move mouse randomly
            print("      - Moving mouse...")
            await page.mouse.move(300, 300)
            await asyncio.sleep(0.5)
            await page.mouse.move(700, 500)
            await asyncio.sleep(0.5)
            
            # Small scroll
            print("      - Scrolling...")
            await page.evaluate("window.scrollTo(0, 100)")
            await asyncio.sleep(1)
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            
            # Now wait intelligently
            print("\n      Waiting for Cloudflare to clear...")
            max_wait = 60  # 60 seconds
            start_time = time.time()
            cleared = False
            
            while (time.time() - start_time) < max_wait:
                elapsed = int(time.time() - start_time)
                print(f"      [{elapsed:02d}s] Checking...", end='\r')
                
                # Check if Cloudflare is gone
                current_content = await page.content()
                still_has_cf = any(indicator in current_content.lower() for indicator in [
                    'just a moment', 'checking your browser'
                ])
                
                if not still_has_cf:
                    print(f"\n      [SUCCESS] Cloudflare cleared after {elapsed} seconds!")
                    cleared = True
                    break
                
                await asyncio.sleep(1)
            
            if not cleared:
                print(f"\n      [TIMEOUT] Cloudflare did not clear after {max_wait} seconds")
                print("      [INFO] This might be a CAPTCHA or advanced challenge")
                print("      [TIP] Check the browser window - you may need to solve manually")
                await asyncio.sleep(10)  # Give time to see/solve manually
            
        else:
            print("      [OK] No Cloudflare challenge detected!")
        
        # Take final screenshot regardless
        await page.screenshot(path="data/screenshots/Apollo_v2_step2_final.png", full_page=True)
        print("\n      [OK] Screenshot 2: Final state")
        
        print("\n[6/6] Analyzing final page...")
        
        final_url = page.url
        final_content = await page.content()
        
        print(f"      Final URL: {final_url}")
        print(f"      Content length: {len(final_content)} characters")
        
        # Check for Apollo content
        if 'apollo' in final_content.lower():
            if 'motorhome' in final_content.lower() or 'camper' in final_content.lower():
                print("      [SUCCESS] Apollo Motorhomes content detected!")
                
                # Look for pricing or key elements
                if any(keyword in final_content.lower() for keyword in ['price', 'rent', 'booking', 'vehicle']):
                    print("      [SUCCESS] Key content elements found (price/rent/booking)")
                else:
                    print("      [PARTIAL] Apollo site loaded but limited content")
            else:
                print("      [PARTIAL] Apollo name found but limited content")
        else:
            print("      [FAILED] No Apollo content detected - still blocked")
        
        print("\n" + "="*80)
        print("BYPASS ATTEMPT COMPLETE")
        print("="*80)
        print("\nScreenshots saved:")
        print("  1. data/screenshots/Apollo_v2_step1_initial.png")
        print("  2. data/screenshots/Apollo_v2_step2_final.png")
        print("\nReview these screenshots to see what Cloudflare challenge was presented.")
        print("="*80 + "\n")
        
        # Keep browser open for 10 seconds so you can see the result
        print("Keeping browser open for 10 seconds for inspection...")
        await asyncio.sleep(10)
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(bypass_apollo_cloudflare())






